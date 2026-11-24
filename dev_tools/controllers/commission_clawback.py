# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CommissionClawback(Document):
	def validate(self):
		calc = frappe.db.get_value(
			"Commission Calculation", self.commission_calculation, ["loan_application", "lender", "gross_commission"], as_dict=True
		)
		self.loan_application, self.lender, self.original_commission = calc.loan_application, calc.lender, calc.gross_commission
		if self.commission_invoice:
			inv_lender = frappe.db.get_value("Commission Invoice", self.commission_invoice, "lender")
			if inv_lender != self.lender:
				frappe.throw(_("Commission Invoice {0} belongs to lender {1}.").format(self.commission_invoice, inv_lender))

		if self.clawback_percentage and not self.clawback_amount:
			self.clawback_amount = flt(self.original_commission * flt(self.clawback_percentage) / 100, 2)
		elif self.clawback_amount and self.original_commission:
			self.clawback_percentage = flt(self.clawback_amount * 100 / self.original_commission, 2)
		if flt(self.clawback_amount) <= 0:
			frappe.throw(_("Clawback Amount must be greater than zero."))
		if flt(self.clawback_amount) > flt(self.original_commission):
			frappe.throw(_("Clawback Amount cannot exceed the original commission {0}.").format(self.original_commission))
		if flt(self.recovery_amount) > flt(self.clawback_amount):
			frappe.throw(_("Recovery Amount cannot exceed the Clawback Amount."))

		if self.recovery_status in ("Pending", "Partially Recovered", "Recovered"):
			if flt(self.recovery_amount) >= flt(self.clawback_amount):
				self.recovery_status = "Recovered"
			elif flt(self.recovery_amount) > 0:
				self.recovery_status = "Partially Recovered"
			else:
				self.recovery_status = "Pending"

	def after_insert(self):
		from dsa_loan.dsa_loan_portal.automation import on_clawback_created

		on_clawback_created(self)

	def on_update(self):
		if self.recovery_status == "Recovered" and flt(self.clawback_amount) >= flt(self.original_commission):
			frappe.db.set_value("Commission Calculation", self.commission_calculation, "calculation_status", "Reversed")
