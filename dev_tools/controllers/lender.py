# Copyright (c) 2026
# For license information, please see license.txt

from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import clean_gstin, clean_pan


class Lender(Document):
	def before_naming(self):
		# The code is the record name, so normalise it before naming, not in validate.
		self.lender_code = (self.lender_code or "").strip().upper()

	def validate(self):
		clean_pan(self)
		clean_gstin(self)
