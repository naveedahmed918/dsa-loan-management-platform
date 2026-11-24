"""Export the site's DSA Loan Portal records to apps/dsa_loan/sample_data/ (one JSON file per DocType).

Run from <bench>/sites:  ../env/bin/python ../apps/dsa_loan/dev_tools/export_sample_data.py dsaloan.localhost
Load them into another site with apps/dsa_loan/scripts/load_sample_data.py.

What is left out or cleared so the files are safe to share and load anywhere:
- records belonging to the applications in EXCLUDE_APPLICATIONS (entered under real people's names) and their
  customers, leads, checklists, documents, disbursements, commissions and commission invoices;
- links to records that only exist on this site: ERPNext Sales / Purchase Invoices, Customers, Communications,
  attached files, users;
- invoice recipients and CC addresses (real email addresses); email group members are not exported at all;
- the company name, replaced by a placeholder that the loader swaps for the target site's company.
"""
import json
import os
import sys

import frappe

EXCLUDE_APPLICATIONS = {"LAPP-2026-00015", "LAPP-2026-00016"}
COMPANY = "__COMPANY__"
ORDER = ["Lender Type", "Lender", "Lender Branch", "Loan Product", "Loan Scheme", "Commission Slab Structure",
         "Lender Document Rule", "Franchise", "DSA Branch", "Lender Login", "Loan Lead", "Loan Customer", "Loan Application",
         "Document Checklist", "Aadhaar Card Data", "PAN Card Data", "Address Proof Data", "Bank Statement Data",
         "Salary Slip Data", "ITR Data", "Form 16 Data", "Loan Disbursement", "Lender Payout Statement",
         "Commission Calculation", "Commission Invoice", "Commission Clawback", "Franchise Settlement"]
CLEAR = {"sales_invoice", "erpnext_sales_invoice", "erpnext_purchase_invoice", "erpnext_customer", "invoice_communication",
         "invoice_email_recipients", "invoice_emailed_on", "invoice_error", "invoice_cc", "user_id"}
DROP = {"owner", "modified_by", "_user_tags", "_comments", "_assign", "_liked_by", "_seen"}


def excluded_sets():
	apps = [a for a in EXCLUDE_APPLICATIONS if frappe.db.exists("Loan Application", a)]
	if not apps:  # already deleted from the site: nothing to leave out
		return {}
	ex = {"Loan Application": set(apps)}
	ex["Loan Customer"] = {frappe.db.get_value("Loan Application", a, "primary_customer") for a in apps} | set(
		frappe.get_all("Co-Applicant", {"parent": ("in", list(apps))}, pluck="applicant"))
	ex["Loan Lead"] = {frappe.db.get_value("Loan Application", a, "loan_lead") for a in apps}
	ex["Document Checklist"] = set(frappe.get_all("Document Checklist", {"loan_application": ("in", list(apps))}, pluck="name"))
	ex["Loan Disbursement"] = set(frappe.get_all("Loan Disbursement", {"loan_application": ("in", list(apps))}, pluck="name"))
	ex["Commission Calculation"] = set(frappe.get_all("Commission Calculation", {"loan_application": ("in", list(apps))}, pluck="name"))
	sis = {frappe.db.get_value("Loan Application", a, "sales_invoice") for a in apps} - {None}
	ex["Commission Invoice"] = set(frappe.get_all("Commission Invoice", {"erpnext_sales_invoice": ("in", list(sis) or [""])}, pluck="name"))
	# an empty link must never count as "excluded" (records without that link would all drop out)
	return {dt: {n for n in names if n} for dt, names in ex.items()}


def keep(dt, d, ex):
	if d["name"] in ex.get(dt, set()):
		return False
	links = {"loan_application": "Loan Application", "primary_customer": "Loan Customer", "applicant": "Loan Customer",
	         "loan_lead": "Loan Lead", "document_checklist": "Document Checklist", "loan_disbursement": "Loan Disbursement",
	         "commission_calculation": "Commission Calculation", "commission_invoice": "Commission Invoice"}
	return not any(d.get(f) in ex.get(target, set()) for f, target in links.items())


def clean(d, attach_fields):
	for k in list(d):
		if k in DROP:
			d.pop(k)
		elif k in CLEAR or k in attach_fields:
			d[k] = None
		elif k in ("company", "assigned_company") and d[k]:
			d[k] = COMPANY
	if d.get("invoice_status") in ("Invoice Created", "Emailed", "Email Pending", "Failed"):
		d["invoice_status"] = None  # the invoice itself is not exported; re-create it with the form button
	return d


def run(out_dir):
	os.makedirs(out_dir, exist_ok=True)
	ex = excluded_sets()
	counts = {}
	for dt in ORDER:
		meta = frappe.get_meta(dt)
		attach = {f.fieldname for f in meta.fields if f.fieldtype in ("Attach", "Attach Image")}
		rows = []
		for name in frappe.get_all(dt, pluck="name", order_by="creation asc"):
			d = frappe.get_doc(dt, name).as_dict(convert_dates_to_str=True)
			if not keep(dt, d, ex):
				continue
			for t in meta.get_table_fields():
				child_attach = {f.fieldname for f in frappe.get_meta(t.options).fields if f.fieldtype == "Attach"}
				d[t.fieldname] = [clean(dict(c), child_attach) for c in d.get(t.fieldname) or []
				                  if not (c.get("applicant") in ex.get("Loan Customer", set()))]
			rows.append(clean(dict(d), attach))
		counts[dt] = len(rows)
		with open(os.path.join(out_dir, frappe.scrub(dt) + ".json"), "w", encoding="utf-8") as fh:
			json.dump(rows, fh, indent=1, default=str, ensure_ascii=False)

	employees = set()
	for dt in ("DSA Branch", "Loan Lead", "Loan Application", "Lender Login", "Franchise", "Commission Calculation"):
		for f in ("branch_manager", "assigned_agent", "assigned_employee", "owner_employee"):
			if frappe.get_meta(dt).has_field(f):
				employees |= set(frappe.get_all(dt, {f: ("is", "set")}, pluck=f))
	emp_rows = []
	for e in sorted(employees):
		doc = frappe.get_doc("Employee", e)
		emp_rows.append({"name": doc.name, "first_name": doc.first_name, "last_name": doc.last_name, "employee_name": doc.employee_name,
		                 "gender": doc.gender, "date_of_birth": str(doc.date_of_birth), "date_of_joining": str(doc.date_of_joining),
		                 "status": doc.status, "company": COMPANY, "naming_series": doc.naming_series})
	with open(os.path.join(out_dir, "employee.json"), "w", encoding="utf-8") as fh:
		json.dump(emp_rows, fh, indent=1)
	counts["Employee"] = len(emp_rows)

	groups = sorted({g for g in frappe.get_all("Lender", pluck="invoice_email_group") if g})
	manifest = {"order": ORDER, "company_placeholder": COMPANY, "email_groups": groups, "counts": counts,
	            "excluded_applications": sorted(EXCLUDE_APPLICATIONS)}
	with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
		json.dump(manifest, fh, indent=1)
	for dt, n in counts.items():
		print(f"{dt:<26} {n}")


if __name__ == "__main__":
	frappe.init(site=sys.argv[1] if len(sys.argv) > 1 else "dsaloan.localhost", sites_path=".")
	frappe.connect()
	try:
		run(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample_data"))
	finally:
		frappe.destroy()
