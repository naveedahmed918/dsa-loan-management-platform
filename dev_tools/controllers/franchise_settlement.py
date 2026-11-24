# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from dsa_loan.dsa_loan_portal.utils import check_range

RECEIVED = ("Paid", "Partially Paid")


class FranchiseSettlement(Document):
	"""Pays a franchise its share of the commission actually received for its loans in a period."""

	def validate(self):
		check_range(self, "settlement_period_from", "settlement_period_to")
		if frappe.db.exists(
			"Franchise Settlement", {"settlement_number": self.settlement_number, "name": ("!=", self.name)}
		):
			frappe.throw(_("Settlement number {0} is already used.").format(self.settlement_number))
		self.validate_no_overlap()
		if not self.franchise_share_percentage:
			self.franchise_share_percentage = frappe.db.get_value("Franchise", self.franchise, "settlement_percentage")
		if flt(self.franchise_share_percentage) > 100:
			frappe.throw(_("Franchise Share Percentage cannot exceed 100."))

		rows = frappe.get_all(
			"Commission Calculation",
			filters={
				"franchise": self.franchise,
				"calculation_status": ("in", RECEIVED),
				"calculation_date": ("between", [self.settlement_period_from, self.settlement_period_to]),
			},
			fields=[{"SUM": "gross_commission", "as": "total"}],
		)
		self.total_gross_commission = flt(rows[0].total if rows else 0, 2)
		self.franchise_share_amount = flt(self.total_gross_commission * flt(self.franchise_share_percentage) / 100, 2)
		self.net_payable = flt(
			self.franchise_share_amount - flt(self.deductions) + flt(self.gst_amount) - flt(self.tds_amount), 2
		)
		if self.has_value_changed("settlement_status") and self.settlement_status == "Paid" and not self.settlement_date:
			frappe.throw(_("Enter the Settlement Date before marking it Paid."))

	def validate_no_overlap(self):
		"""A franchise's commission for a period may only be settled once."""
		if self.settlement_status == "Cancelled":
			return
		others = frappe.get_all(
			"Franchise Settlement",
			filters={"franchise": self.franchise, "settlement_status": ("!=", "Cancelled"), "name": ("!=", self.name)},
			fields=["name", "settlement_period_from", "settlement_period_to"],
		)
		start, end = getdate(self.settlement_period_from), getdate(self.settlement_period_to)
		for o in others:
			if getdate(o.settlement_period_from) <= end and start <= getdate(o.settlement_period_to):
				frappe.throw(_("Settlement {0} already covers part of this period for {1}.").format(o.name, self.franchise))
