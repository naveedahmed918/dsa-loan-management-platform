# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

from dsa_loan.dsa_loan_portal.utils import check_belongs, check_range


class CommissionSlabStructure(Document):
	"""Which basis (disbursed, sanctioned or fixed) applies to a lender/product/scheme for a period.
	The rate itself is entered on each Commission Calculation."""

	def validate(self):
		check_range(self, "effective_from", "effective_to")
		check_belongs("Loan Product", self.loan_product, "lender", self.lender, "Lender")
		check_belongs("Loan Scheme", self.loan_scheme, "loan_product", self.loan_product, "Loan Product")
		if self.slab_status == "Active":
			self.validate_no_overlap()

	def validate_no_overlap(self):
		"""Only one Active structure may cover the same lender/product/scheme on any date."""
		others = frappe.get_all(
			"Commission Slab Structure",
			filters={
				"slab_status": "Active",
				"lender": self.lender,
				"loan_product": self.loan_product or ("is", "not set"),
				"loan_scheme": self.loan_scheme or ("is", "not set"),
				"name": ("!=", self.name),
			},
			fields=["name", "effective_from", "effective_to"],
		)
		start, end = getdate(self.effective_from), getdate(self.effective_to) if self.effective_to else None
		for o in others:
			o_start, o_end = getdate(o.effective_from), getdate(o.effective_to) if o.effective_to else None
			if (end is None or o_start <= end) and (o_end is None or start <= o_end):
				frappe.throw(_("Active slab {0} already covers these dates for the same lender, product and scheme.").format(o.name))


def find_structure(lender, loan_product, loan_scheme, on_date):
	"""The most specific Active structure on a date: scheme, then product, then lender-wide."""
	scopes = []
	if loan_scheme:
		scopes.append({"loan_product": loan_product, "loan_scheme": loan_scheme})
	scopes.append({"loan_product": loan_product, "loan_scheme": ("is", "not set")})
	scopes.append({"loan_product": ("is", "not set"), "loan_scheme": ("is", "not set")})
	for scope in scopes:
		rows = frappe.get_all(
			"Commission Slab Structure",
			filters=dict(scope, slab_status="Active", lender=lender, effective_from=("<=", on_date)),
			or_filters=[["effective_to", "is", "not set"], ["effective_to", ">=", on_date]],
			pluck="name",
			order_by="effective_from desc",
			limit=1,
		)
		if rows:
			return rows[0]
	return None
