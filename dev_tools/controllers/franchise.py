# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from dsa_loan.dsa_loan_portal.utils import check_range, clean_gstin, clean_mobile, clean_pan


class Franchise(Document):
	def before_naming(self):
		# The code is the record name, so normalise it before naming, not in validate.
		self.franchise_code = (self.franchise_code or "").strip().upper()

	def validate(self):
		clean_mobile(self, "contact_number")
		clean_pan(self)
		clean_gstin(self)
		check_range(self, "agreement_start_date", "agreement_end_date")
		if flt(self.settlement_percentage) > 100:
			frappe.throw(_("Settlement Percentage cannot exceed 100."))
