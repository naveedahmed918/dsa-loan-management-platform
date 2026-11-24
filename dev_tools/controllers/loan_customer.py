# Copyright (c) 2026
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, now_datetime, nowdate

from dsa_loan.dsa_loan_portal.utils import clean_mobile, clean_pan

MASKED_AADHAAR = re.compile(r"^XXXX-XXXX-\d{4}$")


def mask_aadhaar(value):
	"""Return Aadhaar as XXXX-XXXX-1234. Accepts 12 digits (any spacing) or an already masked value."""
	if not value:
		return value
	value = value.strip().upper()
	if MASKED_AADHAAR.match(value):
		return value
	digits = re.sub(r"\D", "", value)
	if len(digits) != 12:
		frappe.throw(_("Aadhaar Number must have 12 digits."))
	return "XXXX-XXXX-" + digits[-4:]


class LoanCustomer(Document):
	def validate(self):
		clean_mobile(self, "mobile_number", "alternate_mobile")
		clean_pan(self)
		self.aadhaar_number = mask_aadhaar(self.aadhaar_number)
		self.validate_consent()
		self.validate_cibil()
		if self.is_new() and frappe.db.exists("Loan Customer", {"mobile_number": self.mobile_number}):
			frappe.msgprint(_("Another customer already uses mobile {0}.").format(self.mobile_number), indicator="orange")

	def validate_consent(self):
		if self.kyc_consent:
			if not self.consent_mode:
				frappe.throw(_("Select how the customer gave consent (Consent Mode)."))
			if not self.consent_date:
				self.consent_date = now_datetime()
		else:
			self.consent_mode = self.consent_date = None
			if self.aadhaar_number or self.cibil_score:
				frappe.throw(_("Record the customer's KYC & credit check consent before saving Aadhaar or CIBIL details."))

	def validate_cibil(self):
		if self.cibil_score in (None, 0) and not self.cibil_report_date:
			self.cibil_score = None
			return
		score = self.cibil_score
		if score != -1 and not (300 <= (score or 0) <= 900):
			frappe.throw(_("CIBIL Score must be between 300 and 900, or -1 for no credit history."))
		if not self.cibil_report_date:
			frappe.throw(_("Enter the CIBIL Report Date along with the score."))
		if getdate(self.cibil_report_date) > getdate(nowdate()):
			frappe.throw(_("CIBIL Report Date cannot be in the future."))
