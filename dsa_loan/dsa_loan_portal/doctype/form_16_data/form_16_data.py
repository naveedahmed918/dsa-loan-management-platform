# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.document_data import ExtractedDocument, applicant_pan, clean_pan_field


class Form16Data(ExtractedDocument):
	def validate_document(self):
		clean_pan_field(self, "employee_pan")
		pan = applicant_pan(self.document_checklist)
		if self.employee_pan and pan and self.employee_pan != pan:
			frappe.throw(_("Form 16 PAN {0} does not match the applicant's PAN card.").format(self.employee_pan))
		if self.gross_salary and self.total_deductions and not self.taxable_income:
			self.taxable_income = flt(self.gross_salary) - flt(self.total_deductions)
		if self.assessment_year:
			itr_income = frappe.db.get_value(
				"ITR Data", {"document_checklist": self.document_checklist, "assessment_year": self.assessment_year}, "total_income"
			)
			if itr_income and self.taxable_income and abs(flt(itr_income) - flt(self.taxable_income)) > 0.1 * flt(itr_income):
				frappe.msgprint(_("Form 16 taxable income differs from the {0} ITR by more than 10%.").format(self.assessment_year),
				                indicator="orange")
