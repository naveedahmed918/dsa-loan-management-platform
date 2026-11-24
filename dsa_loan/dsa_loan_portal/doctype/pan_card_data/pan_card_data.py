# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _

from dsa_loan.dsa_loan_portal.document_data import ExtractedDocument, clean_pan_field


class PANCardData(ExtractedDocument):
	def validate_document(self):
		clean_pan_field(self, "pan_number")
		customer_pan = frappe.db.get_value("Loan Customer", self.applicant, "pan")
		if self.pan_number and customer_pan and customer_pan != self.pan_number:
			frappe.msgprint(_("The extracted PAN differs from the PAN on Loan Customer {0}.").format(self.applicant),
			                indicator="orange", title=_("PAN mismatch"))
