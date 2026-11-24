# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate

from dsa_loan.dsa_loan_portal.document_data import MIN_BANK_MONTHS, ExtractedDocument, clean_last_4, months_between


class BankStatementData(ExtractedDocument):
	def validate_document(self):
		clean_last_4(self, "account_last_4", "bank account number")
		if self.period_from and self.period_to:
			if getdate(self.period_to) < getdate(self.period_from):
				frappe.throw(_("Period To cannot be before Period From."))
			self.months_covered = months_between(self.period_from, self.period_to)
			if self.months_covered < MIN_BANK_MONTHS:
				frappe.msgprint(_("This statement covers {0} months; lenders need at least {1}.").format(
					self.months_covered, MIN_BANK_MONTHS), indicator="orange")
