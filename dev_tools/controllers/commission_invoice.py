# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate


class CommissionInvoice(Document):
	def validate(self):
		if flt(self.taxable_amount) <= 0:
			frappe.throw(_("Taxable Amount must be greater than zero."))
		if flt(self.igst_amount) and (flt(self.cgst_amount) or flt(self.sgst_amount)):
			frappe.throw(_("Use either IGST or CGST + SGST, not both."))
		if abs(flt(self.cgst_amount) - flt(self.sgst_amount)) > 0.01:
			frappe.throw(_("CGST and SGST must be equal."))
		if self.due_date and getdate(self.due_date) < getdate(self.invoice_date):
			frappe.throw(_("Due Date cannot be before Invoice Date."))
		if self.invoice_number and frappe.db.exists(
			"Commission Invoice", {"invoice_number": self.invoice_number, "company": self.company, "name": ("!=", self.name)}
		):
			frappe.throw(_("Invoice number {0} is already used.").format(self.invoice_number))
		self.total_gst_amount = flt(flt(self.cgst_amount) + flt(self.sgst_amount) + flt(self.igst_amount), 2)
		self.invoice_total = flt(flt(self.taxable_amount) + self.total_gst_amount, 2)
