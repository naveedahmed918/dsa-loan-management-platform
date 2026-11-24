# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, date_diff, flt, getdate, now_datetime, nowdate

from dsa_loan.dsa_loan_portal.utils import check_belongs, emi, is_active_on

# Order of final_status values that code may move forward automatically.
FORWARD = ["Draft", "Documents Pending", "Ready for Submission", "Submitted", "Under Review", "Query Raised",
           "Sanctioned", "Partially Disbursed", "Disbursed"]
DISBURSABLE = ("Sanctioned", "Partially Disbursed")
CONSENT_NEEDED = ("Ready for Submission", "Submitted")
CIBIL_VALID_DAYS = 30
RBI_LTV_LOAN_TYPES = ("Home Purchase", "Home Loan", "Balance Transfer")


def rbi_ltv_cap(amount):
	"""RBI housing-loan LTV ceiling: up to 30 lakh 90%, above 30 up to 75 lakh 80%, above 75 lakh 75%."""
	return 90 if amount <= 3000000 else 80 if amount <= 7500000 else 75


class LoanApplication(Document):
	def validate(self):
		from dsa_loan.dsa_loan_portal.utils import clean_pincode

		clean_pincode(self, "property_pincode")
		check_belongs("Loan Product", self.loan_product, "lender", self.lender, "Lender")
		check_belongs("Lender Branch", self.lender_branch, "lender", self.lender, "Lender")
		check_belongs("Loan Scheme", self.loan_scheme, "loan_product", self.loan_product, "Loan Product")
		self.validate_co_applicants()
		self.validate_status_fields()
		self.validate_consent()
		self.validate_limits()
		self.estimated_emi = emi(self.requested_loan_amount, self.expected_interest_rate, self.requested_tenure_months)
		if self.sanction_date and self.lender_submission_date and getdate(self.sanction_date) < getdate(self.lender_submission_date):
			frappe.throw(_("Sanction Date cannot be before Lender Submission Date."))
		if self.has_value_changed("manager_approval") and self.manager_approval in ("Approved", "Rejected"):
			self.manager_approval_date = now_datetime()
		self.application_status = self.coarse_status()

	def validate_co_applicants(self):
		seen = set()
		for row in self.co_applicants:
			if row.applicant == self.primary_customer:
				frappe.throw(_("Row {0}: the primary customer cannot also be a co-applicant.").format(row.idx))
			if row.applicant in seen:
				frappe.throw(_("Row {0}: {1} is added twice.").format(row.idx, row.applicant))
			seen.add(row.applicant)

	def validate_status_fields(self):
		"""Server-side twin of the form's mandatory_depends_on rules."""
		if self.final_status == "Sanctioned" and not (self.sanctioned_amount and self.sanction_date):
			frappe.throw(_("Enter the Sanctioned Amount and Sanction Date before marking the application Sanctioned."))
		if self.final_status == "Rejected" and not self.rejection_reason:
			frappe.throw(_("Enter the Rejection Reason before marking the application Rejected."))
		# Disbursed / Partially Disbursed are set by confirming a Loan Disbursement (which also creates the
		# commission and the lender invoice); typing them here by hand would skip all of that.
		if (self.final_status in ("Partially Disbursed", "Disbursed") and self.has_value_changed("final_status")
				and not frappe.db.exists("Loan Disbursement", {"loan_application": self.name, "disbursement_status": "Confirmed"})):
			frappe.throw(_("Record the money released with the <b>New Disbursement</b> button (status Confirmed). The application "
			               "then becomes {0} by itself, and the commission and lender invoice are created.").format(self.final_status))

	def validate_limits(self):
		"""Requested amount / tenure inside the product and scheme limits; LTV inside the RBI cap and the scheme's."""
		amount, tenure = flt(self.requested_loan_amount), cint(self.requested_tenure_months)
		for doctype, name in (("Loan Product", self.loan_product), ("Loan Scheme", self.loan_scheme)):
			if not name:
				continue
			lim = frappe.db.get_value(doctype, name, ["minimum_loan_amount", "maximum_loan_amount",
				"minimum_tenure_months", "maximum_tenure_months"], as_dict=True)
			if flt(lim.minimum_loan_amount) and amount < flt(lim.minimum_loan_amount):
				frappe.throw(_("{0} {1} lends at least {2}.").format(doctype, name, frappe.format(lim.minimum_loan_amount, "Currency")))
			if flt(lim.maximum_loan_amount) and amount > flt(lim.maximum_loan_amount):
				frappe.throw(_("{0} {1} lends at most {2}.").format(doctype, name, frappe.format(lim.maximum_loan_amount, "Currency")))
			if cint(lim.minimum_tenure_months) and tenure < cint(lim.minimum_tenure_months):
				frappe.throw(_("{0} {1} needs a tenure of at least {2} months.").format(doctype, name, lim.minimum_tenure_months))
			if cint(lim.maximum_tenure_months) and tenure > cint(lim.maximum_tenure_months):
				frappe.throw(_("{0} {1} allows at most {2} months.").format(doctype, name, lim.maximum_tenure_months))

		if not flt(self.property_value) or self.loan_type not in RBI_LTV_LOAN_TYPES:
			return
		for which, value in (("requested", amount), ("sanctioned", flt(self.sanctioned_amount))):
			if not value:
				continue
			cap = rbi_ltv_cap(value)
			scheme_cap = flt(frappe.db.get_value("Loan Scheme", self.loan_scheme, "maximum_ltv")) if self.loan_scheme else 0
			if scheme_cap:
				cap = min(cap, scheme_cap)
			ltv = value / flt(self.property_value) * 100
			if ltv > cap:
				frappe.throw(_("The {0} amount is {1}% of the property value; the limit is {2}% (RBI cap for this loan size{3}).").format(
					which, round(ltv, 1), cap, _(" and the scheme's limit") if scheme_cap else ""))

	def validate_consent(self):
		"""Every applicant must have given KYC & credit check consent before the file goes to the lender."""
		if not (self.has_value_changed("final_status") and self.final_status in CONSENT_NEEDED):
			return
		applicants = [self.primary_customer] + [r.applicant for r in self.co_applicants]
		missing = [a for a in applicants if not frappe.db.get_value("Loan Customer", a, "kyc_consent")]
		if missing:
			frappe.throw(_("Record KYC & credit check consent on {0} before marking the application {1}.").format(
				", ".join(missing), self.final_status))
		if self.final_status == "Submitted":
			report_date = frappe.db.get_value("Loan Customer", self.primary_customer, "cibil_report_date")
			if not report_date or date_diff(nowdate(), report_date) > CIBIL_VALID_DAYS:
				frappe.msgprint(_("The primary customer's CIBIL report is missing or older than {0} days.").format(CIBIL_VALID_DAYS),
					indicator="orange", alert=True)

	def coarse_status(self):
		if self.final_status in ("Disbursed", "Closed"):
			return "Completed"
		if self.final_status in ("Rejected", "Withdrawn"):
			return "Cancelled"
		if self.final_status == "On Hold":
			return "On Hold"
		return "Open" if self.final_status == "Draft" else "In Progress"

	def after_insert(self):
		if self.loan_lead:
			from dsa_loan.dsa_loan_portal.doctype.loan_lead.loan_lead import mark_converted

			mark_converted(self.loan_lead)

	def on_update(self):
		from dsa_loan.dsa_loan_portal.document_data import make_checklists

		# a customer without a branch inherits it so branch users can see them
		for applicant in [self.primary_customer] + [r.applicant for r in self.co_applicants]:
			if not frappe.db.get_value("Loan Customer", applicant, "dsa_branch"):
				frappe.db.set_value("Loan Customer", applicant, "dsa_branch", self.dsa_branch)
		created = make_checklists(self)
		if created:
			frappe.msgprint(_("{0} document checklist(s) created, one per applicant.").format(created), alert=True)

		from dsa_loan.dsa_loan_portal.invoicing import on_application_update

		on_application_update(self)
		if self.final_status == "Closed" and self.has_value_changed("final_status"):
			from dsa_loan.dsa_loan_portal.automation import on_application_closed

			on_application_closed(self)


def set_final_status(application, new_status):
	"""Move final_status forward only (never back), keeping application_status in step."""
	doc = frappe.get_doc("Loan Application", application)
	if doc.final_status in FORWARD and new_status in FORWARD and FORWARD.index(new_status) <= FORWARD.index(doc.final_status):
		return
	doc.final_status = new_status
	doc.application_status = doc.coarse_status()
	doc.db_update()
	if new_status == "Disbursed":
		from dsa_loan.dsa_loan_portal.invoicing import start_invoicing

		start_invoicing(doc)


def matching_rules(app, role, employment_type):
	"""Active Lender Document Rules for this application that apply to an applicant in the given role."""
	if not app.lender:
		return []
	rules = frappe.get_all(
		"Lender Document Rule",
		filters={"lender": app.lender, "is_active": 1},
		fields=["name", "loan_product", "loan_scheme", "applicant_type", "employment_type", "property_type", "document_name"],
		order_by="creation asc",
	)
	roles = {role, "All"} | ({"Property Owner"} if role == "Primary Applicant" else set())
	out = []
	for rule in rules:
		if rule.loan_product and rule.loan_product != app.loan_product:
			continue
		if rule.loan_scheme and rule.loan_scheme != app.loan_scheme:
			continue
		if rule.property_type and rule.property_type != app.property_type:
			continue
		if rule.employment_type and rule.employment_type != employment_type:
			continue
		if rule.applicant_type in roles:
			out.append(rule)
	return out
