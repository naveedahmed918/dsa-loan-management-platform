# Copyright (c) 2026
# For license information, please see license.txt

from frappe.model.document import Document

from dsa_loan.dsa_loan_portal.utils import check_belongs, check_range


class LoanScheme(Document):
	def before_naming(self):
		# The code is the record name, so normalise it before naming, not in validate.
		self.scheme_code = (self.scheme_code or "").strip().upper()

	def validate(self):
		check_belongs("Loan Product", self.loan_product, "lender", self.lender, "Lender")
		check_range(self, "effective_from", "effective_to")
		check_range(self, "minimum_age", "maximum_age")
		check_range(self, "minimum_loan_amount", "maximum_loan_amount")
		check_range(self, "minimum_interest_rate", "maximum_interest_rate")
		check_range(self, "minimum_tenure_months", "maximum_tenure_months")
