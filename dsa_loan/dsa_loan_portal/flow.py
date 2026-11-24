"""Server side of the guided flow on the forms (buttons and the progress bar on Loan Application).

Everything goes through the normal controllers, so every rule and automatic step still applies.
"""

import json

import frappe
from frappe import _
from frappe.utils import flt, nowdate


@frappe.whitelist()
def application_flow(application):
	"""Progress of one application: documents per applicant, consent, money, commission and invoice."""
	app = frappe.get_doc("Loan Application", application)
	app.check_permission("read")
	applicants = [app.primary_customer] + [r.applicant for r in app.co_applicants]
	checklists = []
	for c in frappe.get_all("Document Checklist", {"loan_application": app.name}, ["name", "applicant"], order_by="creation"):
		rows = frappe.get_all("Document Checklist Item", {"parent": c.name, "parenttype": "Document Checklist"}, pluck="document_status")
		needed = [r for r in rows if r != "Not Applicable"]
		checklists.append({"name": c.name, "applicant": c.applicant,
		                   "customer_name": frappe.db.get_value("Loan Customer", c.applicant, "customer_name"),
		                   "verified": sum(1 for r in needed if r == "Verified"), "total": len(needed),
		                   "attention": sum(1 for r in needed if r in ("Rejected", "Resubmission Required"))})
	consent_missing = [{"name": a, "customer_name": frappe.db.get_value("Loan Customer", a, "customer_name")}
	                   for a in applicants if not frappe.db.get_value("Loan Customer", a, "kyc_consent")]
	tranches = frappe.get_all("Loan Disbursement", {"loan_application": app.name},
	                          ["name", "disbursement_number", "disbursement_status", "current_disbursement_amount"], order_by="creation")
	disbursed = sum(flt(t.current_disbursement_amount) for t in tranches if t.disbursement_status == "Confirmed")
	numbers = [int(t.disbursement_number) for t in tranches if str(t.disbursement_number).isdigit()]
	return {
		"checklists": checklists,
		"consent_missing": consent_missing,
		"tranches": tranches,
		"disbursed": disbursed,
		"balance": max(flt(app.sanctioned_amount) - disbursed, 0),
		"next_number": str(max(numbers or [0]) + 1),
		"commissions": frappe.get_all("Commission Calculation", {"loan_application": app.name},
		                              ["name", "gross_commission", "calculation_status"], order_by="creation"),
	}


@frappe.whitelist()
def record_disbursement(application, values):
	"""Create a Confirmed Loan Disbursement from the application's dialog; automation then takes over."""
	app = frappe.get_doc("Loan Application", application)
	app.check_permission("write")
	v = json.loads(values) if isinstance(values, str) else values
	info = application_flow(application)
	doc = frappe.get_doc({
		"doctype": "Loan Disbursement", "loan_application": app.name, "disbursement_number": info["next_number"],
		"disbursement_date": v.get("disbursement_date") or nowdate(), "disbursement_type": v.get("disbursement_type") or "Full",
		"disbursement_status": "Confirmed", "current_disbursement_amount": flt(v.get("amount")),
		"payment_mode": v.get("payment_mode"), "payment_reference": v.get("payment_reference"),
		"beneficiary_name": v.get("beneficiary_name"), "lender_reference_number": v.get("lender_reference_number"),
	})
	doc.insert()
	return doc.name


@frappe.whitelist()
def verify_received(checklist):
	"""Mark every Received row Verified (rows backed by a document record must have it linked)."""
	doc = frappe.get_doc("Document Checklist", checklist)
	doc.check_permission("write")
	changed = 0
	for row in doc.documents:
		if row.document_status == "Received" and (row.extracted_data or not row.extracted_data_type):
			row.document_status = "Verified"
			changed += 1
	if changed:
		doc.save()
	return changed
