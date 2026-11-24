# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class LenderBranch(Document):
	def validate(self):
		from dsa_loan.dsa_loan_portal.utils import clean_pincode

		clean_pincode(self, "pincode")
		self.branch_code = (self.branch_code or "").strip().upper()
		if frappe.db.exists(
			"Lender Branch", {"lender": self.lender, "branch_code": self.branch_code, "name": ("!=", self.name)}
		):
			frappe.throw(_("Branch code {0} is already used for lender {1}.").format(self.branch_code, self.lender))
