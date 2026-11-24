# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import check_range

TOLERANCE = 1.0  # rupees of rounding difference treated as a match
AUTO = ("Draft", "Pending Reconciliation", "Matched", "Partially Matched")
COUNTED = ("Calculated", "Approved", "Invoiced", "Partially Paid", "Paid")
OPEN = ("Draft", "Pending Reconciliation")  # a statement still taking in commissions for its period


class LenderPayoutStatement(Document):
	"""Reconciles a lender's payout statement for a period against the commissions calculated for it."""

	def validate(self):
		check_range(self, "period_from", "period_to")
		if frappe.db.exists(
			"Lender Payout Statement",
			{"lender": self.lender, "statement_number": self.statement_number, "name": ("!=", self.name)},
		):
			frappe.throw(_("Statement {0} of {1} is already recorded.").format(self.statement_number, self.lender))

		self.total_expected_commission = flt(sum(c.gross_commission for c in self.calculations()), 2)
		self.net_payable = flt(
			flt(self.total_lender_commission) - flt(self.total_tds) - flt(self.total_gst_adjustment) - flt(self.total_deductions), 2
		)
		if self.reconciliation_status in AUTO:
			self.reconciliation_status = self.auto_status()

	def is_open(self):
		"""New, or not yet reconciled before this save: it may take in commissions no statement covers yet.
		A reconciled statement is frozen; commissions that arrive later go to a top-up statement."""
		before = self.get_doc_before_save()
		return self.is_new() or not before or before.reconciliation_status in OPEN

	def calculations(self):
		rows = frappe.get_all(
			"Commission Calculation",
			filters={
				"lender": self.lender,
				"calculation_date": ("between", [self.period_from, self.period_to]),
				"calculation_status": ("in", COUNTED),
			},
			fields=["name", "gross_commission", "payout_statement"],
		)
		take_unlinked = self.is_open()
		return [r for r in rows if r.payout_statement == self.name or (take_unlinked and not r.payout_statement)]

	def auto_status(self):
		if self.actual_received_amount in (None, "") or not flt(self.actual_received_amount):
			return "Pending Reconciliation"
		commission_ok = abs(flt(self.total_lender_commission) - flt(self.total_expected_commission)) <= TOLERANCE
		payment_ok = abs(flt(self.actual_received_amount) - flt(self.net_payable)) <= TOLERANCE
		return "Matched" if commission_ok and payment_ok else "Partially Matched"

	def on_update(self):
		for c in self.calculations():  # claim them, so no other statement counts them twice
			if c.payout_statement != self.name:
				frappe.db.set_value("Commission Calculation", c.name, "payout_statement", self.name)
		if self.reconciliation_status not in ("Matched", "Partially Matched", "Closed"):
			return
		status = "Paid" if self.reconciliation_status in ("Matched", "Closed") else "Partially Paid"
		for c in self.calculations():
			frappe.db.set_value("Commission Calculation", c.name, "calculation_status", status)
		if self.reconciliation_status in ("Matched", "Partially Matched") and self.has_value_changed("reconciliation_status"):
			from dsa_loan.dsa_loan_portal.automation import on_payout_reconciled

			on_payout_reconciled(self)
