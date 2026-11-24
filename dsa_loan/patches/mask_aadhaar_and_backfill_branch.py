"""Mask full Aadhaar numbers already stored on Loan Customer and fill the new dsa_branch links."""

import re

import frappe


def execute():
	for name, aadhaar in frappe.get_all("Loan Customer", {"aadhaar_number": ("is", "set")}, ["name", "aadhaar_number"], as_list=True):
		digits = re.sub(r"\D", "", aadhaar)
		masked = "XXXX-XXXX-" + digits[-4:] if len(digits) >= 4 and not aadhaar.startswith("XXXX") else aadhaar
		if masked != aadhaar:
			frappe.db.set_value("Loan Customer", name, "aadhaar_number", masked, update_modified=False)

	for dt in ("Document Checklist", "Loan Disbursement"):
		frappe.db.sql(
			f"""update `tab{dt}` t join `tabLoan Application` a on a.name = t.loan_application
			set t.dsa_branch = a.dsa_branch where ifnull(t.dsa_branch, '') = ''"""
		)

	from dsa_loan.dsa_loan_portal.document_data import EXTRACTED_DOCTYPES

	for dt in EXTRACTED_DOCTYPES:
		frappe.db.sql(
			f"""update `tab{dt}` t join `tabDocument Checklist` c on c.name = t.document_checklist
			set t.dsa_branch = c.dsa_branch where ifnull(t.dsa_branch, '') = ''"""
		)

	# customers take the branch of their first lead / application
	frappe.db.sql(
		"""update `tabLoan Customer` c join `tabLoan Application` a on a.primary_customer = c.name
		set c.dsa_branch = a.dsa_branch where ifnull(c.dsa_branch, '') = ''"""
	)
	frappe.db.sql(
		"""update `tabLoan Customer` c join `tabLoan Lead` l on l.mobile_number = c.mobile_number
		set c.dsa_branch = l.dsa_branch where ifnull(c.dsa_branch, '') = ''"""
	)
