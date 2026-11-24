# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import check_range


class LoanProduct(Document):
	def before_naming(self):
		# The code is the record name, so normalise it before naming, not in validate.
		self.product_code = (self.product_code or "").strip().upper()

	def validate(self):
		check_range(self, "minimum_loan_amount", "maximum_loan_amount")
		check_range(self, "minimum_tenure_months", "maximum_tenure_months")
		check_range(self, "minimum_interest_rate", "maximum_interest_rate")
		check_range(self, "minimum_processing_fee", "maximum_processing_fee")
		check_range(self, "effective_from", "effective_to")
		if self.processing_fee_type == "Percentage" and flt(self.processing_fee) > 100:
			frappe.throw(_("A percentage processing fee cannot exceed 100."))
