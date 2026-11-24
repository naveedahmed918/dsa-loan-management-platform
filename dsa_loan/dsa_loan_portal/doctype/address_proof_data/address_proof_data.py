# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, nowdate

from dsa_loan.dsa_loan_portal.document_data import ExtractedDocument


class AddressProofData(ExtractedDocument):
	def validate_document(self):
		if self.valid_till and getdate(self.valid_till) < getdate(nowdate()):
			frappe.msgprint(_("This address proof expired on {0}.").format(self.valid_till), indicator="orange")
		if self.document_date and self.valid_till and getdate(self.valid_till) < getdate(self.document_date):
			frappe.throw(_("Valid Till cannot be before Document Date."))
