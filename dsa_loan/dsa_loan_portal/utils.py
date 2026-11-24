"""Shared validation and calculation helpers for the DSA Loan Portal DocTypes."""

import re

import frappe
from frappe import _
from frappe.utils import flt, getdate

MOBILE_RE = re.compile(r"^[6-9]\d{9}$")
PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
GSTIN_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]$")
IFSC_RE = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")


def label(doc, fieldname):
	return _(doc.meta.get_label(fieldname))


def clean_mobile(doc, *fieldnames):
	"""Normalise Indian mobile numbers to 10 digits and reject anything else."""
	for fn in fieldnames:
		raw = (doc.get(fn) or "").strip()
		if not raw:
			continue
		digits = re.sub(r"\D", "", raw)
		if len(digits) == 12 and digits.startswith("91"):
			digits = digits[2:]
		if not MOBILE_RE.match(digits):
			frappe.throw(_("{0} must be a valid 10-digit Indian mobile number.").format(label(doc, fn)))
		doc.set(fn, digits)


def clean_code(doc, fieldname, pattern, what):
	value = (doc.get(fieldname) or "").strip().upper()
	if not value:
		return
	if not pattern.match(value):
		frappe.throw(_("{0} is not a valid {1}.").format(label(doc, fieldname), what))
	doc.set(fieldname, value)


def clean_pan(doc, fieldname="pan"):
	clean_code(doc, fieldname, PAN_RE, "PAN")


def clean_gstin(doc, fieldname="gstin"):
	clean_code(doc, fieldname, GSTIN_RE, "GSTIN")


def clean_ifsc(doc, fieldname="ifsc_code"):
	clean_code(doc, fieldname, IFSC_RE, "IFSC code")


PINCODE_RE = re.compile(r"^[1-9][0-9]{5}$")


def clean_pincode(doc, *fields):
	"""Indian PIN code: 6 digits, never starting with 0 (spaces removed)."""
	for field in fields:
		value = re.sub(r"\s", "", doc.get(field) or "")
		if value and not PINCODE_RE.match(value):
			frappe.throw(_("{0} must be a valid 6-digit PIN code.").format(doc.meta.get_label(field)))
		doc.set(field, value or None)


def check_range(doc, low, high, inclusive=True):
	"""Throw when doc.high is set and smaller than doc.low (works for numbers and dates)."""
	lo, hi = doc.get(low), doc.get(high)
	if lo in (None, "") or hi in (None, ""):
		return
	if doc.meta.get_field(low) and doc.meta.get_field(low).fieldtype in ("Date", "Datetime"):
		lo, hi = getdate(lo), getdate(hi)
	else:
		lo, hi = flt(lo), flt(hi)
		if not hi:
			return  # an empty (0) maximum means "no upper limit"
	if hi < lo or (not inclusive and hi == lo):
		frappe.throw(_("{0} cannot be earlier or lower than {1}.").format(label(doc, high), label(doc, low)))


def check_belongs(child_doctype, child_name, field, expected, what):
	"""Throw unless frappe.db.get_value(child_doctype, child_name, field) == expected."""
	if not child_name or not expected:
		return
	actual = frappe.db.get_value(child_doctype, child_name, field)
	if actual != expected:
		frappe.throw(
			_("{0} {1} does not belong to {2} {3}.").format(_(child_doctype), child_name, _(what), expected)
		)


def emi(principal, annual_rate, months):
	"""Standard reducing-balance EMI."""
	principal, months = flt(principal), int(months or 0)
	if principal <= 0 or months <= 0:
		return 0
	r = flt(annual_rate) / 1200
	if not r:
		return flt(principal / months, 2)
	factor = (1 + r) ** months
	return flt(principal * r * factor / (factor - 1), 2)


def is_active_on(valid_from, valid_to, on_date):
	on_date = getdate(on_date)
	return (not valid_from or getdate(valid_from) <= on_date) and (not valid_to or getdate(valid_to) >= on_date)
