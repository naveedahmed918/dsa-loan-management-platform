# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

from dsa_loan.dsa_loan_portal.utils import check_belongs, check_range


class LenderLogin(Document):
	"""Who may use which lender portal. Stores the username only; passwords never belong here."""

	def validate(self):
		check_belongs("Lender Branch", self.lender_branch, "lender", self.lender, "Lender")
		check_range(self, "access_start_date", "access_end_date")
		if self.access_end_date and getdate(self.access_end_date) < getdate(nowdate()) and self.access_status == "Active":
			self.access_status = "Expired"
		if self.access_type == "Individual" and self.access_status == "Active" and self.login_username:
			dup = frappe.db.get_value(
				"Lender Login",
				{"lender": self.lender, "login_username": self.login_username, "access_status": "Active", "name": ("!=", self.name)},
			)
			if dup:
				frappe.throw(_("Username {0} is already active for {1} in {2}.").format(self.login_username, self.lender, dup))
