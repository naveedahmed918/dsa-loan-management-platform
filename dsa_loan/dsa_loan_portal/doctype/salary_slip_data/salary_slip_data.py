# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, get_first_day

from dsa_loan.dsa_loan_portal.document_data import ExtractedDocument


class SalarySlipData(ExtractedDocument):
	def validate_document(self):
		if self.salary_month:
			self.salary_month = get_first_day(self.salary_month)
		if self.gross_salary and self.net_salary and flt(self.net_salary) > flt(self.gross_salary):
			frappe.throw(_("Net Salary cannot be more than Gross Salary."))
		if self.gross_salary and not self.deductions and self.net_salary:
			self.deductions = flt(self.gross_salary) - flt(self.net_salary)
