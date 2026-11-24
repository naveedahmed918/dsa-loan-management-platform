# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import clean_mobile


class LoanLead(Document):
	def validate(self):
		clean_mobile(self, "mobile_number", "alternate_mobile")
		if self.lead_status == "Converted" and not frappe.db.exists("Loan Application", {"loan_lead": self.name}):
			frappe.throw(_("Use the Convert to Customer button to convert a lead."))
		if self.is_new() or self.has_value_changed("mobile_number"):
			dup = frappe.db.get_value(
				"Loan Lead",
				{"mobile_number": self.mobile_number, "lead_status": ("not in", ["Converted", "Not Interested", "Lost"]), "name": ("!=", self.name)},
			)
			if dup:
				frappe.msgprint(_("An open lead {0} already exists with this mobile number.").format(dup), indicator="orange")


@frappe.whitelist()
def convert_to_customer(lead):
	"""Create or reuse the Loan Customer for this lead and return it, ready for a new Loan Application."""
	lead = frappe.get_doc("Loan Lead", lead)
	lead.check_permission("write")
	if lead.lead_status in ("Not Interested", "Lost"):
		frappe.throw(_("A {0} lead cannot be converted.").format(lead.lead_status))
	existing = frappe.db.get_value("Loan Application", {"loan_lead": lead.name})
	if existing:
		frappe.throw(_("Lead {0} is already converted into Loan Application {1}.").format(lead.name, existing))

	customer = frappe.db.get_value("Loan Customer", {"mobile_number": lead.mobile_number})
	if not customer:
		customer = frappe.get_doc(
			{
				"doctype": "Loan Customer",
				"customer_name": lead.customer_name,
				"mobile_number": lead.mobile_number,
				"alternate_mobile": lead.alternate_mobile,
				"email": lead.email,
				"employment_type": lead.employment_type,
				"dsa_branch": lead.dsa_branch,
			}
		).insert().name
	return customer


def mark_converted(lead):
	"""Called when a Loan Application is created from the lead."""
	frappe.db.set_value("Loan Lead", lead, "lead_status", "Converted")
