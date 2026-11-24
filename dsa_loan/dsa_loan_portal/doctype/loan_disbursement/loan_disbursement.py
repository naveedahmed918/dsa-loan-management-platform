# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.doctype.loan_application.loan_application import DISBURSABLE, set_final_status


class LoanDisbursement(Document):
	def validate(self):
		app = frappe.db.get_value(
			"Loan Application", self.loan_application, ["lender", "sanctioned_amount", "final_status", "dsa_branch"], as_dict=True
		)
		self.lender, self.sanctioned_amount, self.dsa_branch = app.lender, app.sanctioned_amount, app.dsa_branch
		if self.is_new() and app.final_status not in DISBURSABLE:
			frappe.throw(_("Loan Application {0} must be Sanctioned before disbursement (it is {1}).").format(self.loan_application, app.final_status))
		if flt(self.current_disbursement_amount) <= 0:
			frappe.throw(_("Current Disbursement Amount must be greater than zero."))
		if frappe.db.exists(
			"Loan Disbursement",
			{"loan_application": self.loan_application, "disbursement_number": self.disbursement_number, "name": ("!=", self.name)},
		):
			frappe.throw(_("Disbursement number {0} already exists for {1}.").format(self.disbursement_number, self.loan_application))
		self.lock_confirmed()
		self.set_amounts()

	def lock_confirmed(self):
		if not self.is_new() and self.get_doc_before_save() and self.get_doc_before_save().disbursement_status == "Confirmed":
			before = self.get_doc_before_save()
			if flt(before.current_disbursement_amount) != flt(self.current_disbursement_amount):
				frappe.throw(_("A Confirmed disbursement's amount cannot be changed. Mark it Reversed and create a new one."))

	def set_amounts(self):
		rows = frappe.get_all(
			"Loan Disbursement",
			filters={"loan_application": self.loan_application, "disbursement_status": "Confirmed", "name": ("!=", self.name)},
			fields=[{"SUM": "current_disbursement_amount", "as": "total"}],
		)
		self.previous_disbursed_amount = flt(rows[0].total) if rows else 0
		counted = self.disbursement_status == "Confirmed"
		self.total_disbursed_amount = self.previous_disbursed_amount + (flt(self.current_disbursement_amount) if counted else 0)
		if flt(self.sanctioned_amount) and self.previous_disbursed_amount + flt(self.current_disbursement_amount) > flt(self.sanctioned_amount):
			frappe.throw(_("Total disbursed would exceed the sanctioned amount {0}.").format(frappe.format(self.sanctioned_amount, "Currency")))
		self.balance_amount = flt(self.sanctioned_amount) - self.total_disbursed_amount

	def on_update(self):
		if self.has_value_changed("disbursement_status") and self.disbursement_status == "Confirmed":
			fully = flt(self.balance_amount) <= 0 or self.disbursement_type in ("Full", "Final")
			set_final_status(self.loan_application, "Disbursed" if fully else "Partially Disbursed")
			from dsa_loan.dsa_loan_portal.automation import on_disbursement_confirmed

			on_disbursement_confirmed(self)
		if self.has_value_changed("disbursement_status") and self.disbursement_status == "Reversed":
			for calc in frappe.get_all("Commission Calculation", {"loan_disbursement": self.name}, ["name", "calculation_status"]):
				if calc.calculation_status in ("Draft", "Calculated", "Approved"):
					frappe.db.set_value("Commission Calculation", calc.name, "calculation_status", "Reversed")
				else:
					frappe.msgprint(_("Commission {0} is already {1}; record a Commission Clawback for it.").format(calc.name, calc.calculation_status), indicator="orange")
