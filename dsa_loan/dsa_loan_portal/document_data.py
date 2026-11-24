"""Document checklist rows and the extracted-data DocTypes behind them.

Each applicant gets one Document Checklist per Loan Application. Its rows are the documents to verify;
each row can point (Dynamic Link) to a record in one of the extracted-data DocTypes below.
"""

import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, date_diff, getdate, now_datetime

from dsa_loan.dsa_loan_portal.utils import PAN_RE

EXTRACTED_DOCTYPES = (
	"Aadhaar Card Data",
	"PAN Card Data",
	"Address Proof Data",
	"Bank Statement Data",
	"Salary Slip Data",
	"ITR Data",
	"Form 16 Data",
)

SALARIED_ONLY = ("Salary Slip Data", "Form 16 Data")

# (document name, extracted-data DocType), in checklist order: 13 rows for a salaried applicant.
STANDARD_DOCUMENTS = [
	("Aadhaar Card", "Aadhaar Card Data"),
	("PAN Card", "PAN Card Data"),
	("Address Proof", "Address Proof Data"),
	("Bank Statement – Last 6 Months", "Bank Statement Data"),
	("Salary Slip – Month 1", "Salary Slip Data"),
	("Salary Slip – Month 2", "Salary Slip Data"),
	("Salary Slip – Month 3", "Salary Slip Data"),
	("ITR – Year 1", "ITR Data"),
	("ITR – Year 2", "ITR Data"),
	("ITR – Year 3", "ITR Data"),
	("Form 16 – Year 1", "Form 16 Data"),
	("Form 16 – Year 2", "Form 16 Data"),
	("Form 16 – Year 3", "Form 16 Data"),
]

MIN_BANK_MONTHS = 6
COUNT_RULES = {  # DocType -> (field that must differ between records, how many are needed, what it is)
	"Salary Slip Data": ("salary_month", 3, "salary months"),
	"ITR Data": ("assessment_year", 3, "ITR assessment years"),
	"Form 16 Data": ("assessment_year", 3, "Form 16 assessment years"),
}


def standard_rows(employment_type):
	"""Checklist rows for one applicant. Salary slips and Form 16 apply to salaried applicants only."""
	salaried = employment_type in (None, "", "Salaried")
	rows = []
	for name, doctype in STANDARD_DOCUMENTS:
		rows.append(
			{
				"document_name": name,
				"extracted_data_type": doctype,
				"document_status": "Pending" if salaried or doctype not in SALARIED_ONLY else "Not Applicable",
			}
		)
	return rows


def month_key(d):
	d = getdate(d)
	return (d.year, d.month)


class ExtractedDocument(Document):
	"""Base controller for the extracted-data DocTypes."""

	def validate(self):
		checklist = frappe.db.get_value(
			"Document Checklist", self.document_checklist, ["loan_application", "applicant", "dsa_branch"], as_dict=True
		)
		self.loan_application, self.applicant = checklist.loan_application, checklist.applicant
		self.dsa_branch = checklist.dsa_branch
		if self.extraction_status in ("Extracted", "Verified") and not self.extracted_on:
			self.extracted_on = now_datetime()
		self.validate_document()
		self.validate_distinct()

	def validate_document(self):
		"""Per-document checks; overridden by subclasses."""

	def validate_distinct(self):
		"""Salary months / assessment years must differ between records of the same checklist."""
		rule = COUNT_RULES.get(self.doctype)
		if not rule or not self.get(rule[0]):
			return
		field, _count, what = rule
		for other in frappe.get_all(
			self.doctype, {"document_checklist": self.document_checklist, "name": ("!=", self.name)}, ["name", field]
		):
			if not other.get(field):
				continue
			same = (
				month_key(other.get(field)) == month_key(self.get(field))
				if field == "salary_month"
				else other.get(field) == self.get(field)
			)
			if same:
				frappe.throw(_("{0} already has a record for this period ({1}); {2} must all be different.").format(
					self.document_checklist, other.name, what))

	def on_update(self):
		link_to_checklist(self)

	def on_trash(self):
		checklist = frappe.get_doc("Document Checklist", self.document_checklist)
		for row in checklist.documents:
			if row.extracted_data_type == self.doctype and row.extracted_data == self.name:
				row.extracted_data = None
		checklist.flags.ignore_permissions = True
		checklist.save()


def link_to_checklist(record):
	"""Put the record into the first matching checklist row that has none yet."""
	checklist = frappe.get_doc("Document Checklist", record.document_checklist)
	if any(r.extracted_data_type == record.doctype and r.extracted_data == record.name for r in checklist.documents):
		return
	row = next(
		(r for r in checklist.documents if r.extracted_data_type == record.doctype and not r.extracted_data), None
	)
	if not row:
		frappe.msgprint(_("No empty {0} row in {1}; add one to link this record.").format(record.doctype, checklist.name),
		                indicator="orange")
		return
	row.extracted_data = record.name
	if record.source_file and not row.document_file:
		row.document_file = record.source_file
	if row.document_status == "Pending":
		row.document_status = "Received"
	checklist.flags.ignore_permissions = True
	checklist.save()


def clean_last_4(doc, fieldname, what):
	value = re.sub(r"\D", "", doc.get(fieldname) or "")
	if not value:
		return
	if len(value) > 4:
		frappe.throw(_("Store only the last 4 digits of the {0}, never the full number.").format(what))
	if len(value) != 4:
		frappe.throw(_("{0} must be exactly 4 digits.").format(doc.meta.get_label(fieldname)))
	doc.set(fieldname, value)


def clean_pan_field(doc, fieldname):
	value = (doc.get(fieldname) or "").strip().upper()
	if value and not PAN_RE.match(value):
		frappe.throw(_("{0} is not a valid PAN.").format(doc.meta.get_label(fieldname)))
	doc.set(fieldname, value)


def months_between(start, end):
	"""Whole calendar months covered by [start, end], counting partial first/last months."""
	start, end = getdate(start), getdate(end)
	return (end.year - start.year) * 12 + end.month - start.month + 1


def check_checklist(doc):
	"""Checks across a Document Checklist's rows and their extracted records."""
	for row in doc.documents:
		if row.extracted_data_type and row.extracted_data_type not in EXTRACTED_DOCTYPES:
			frappe.throw(_("Row {0}: {1} is not a document-data DocType.").format(row.idx, row.extracted_data_type))
		if row.extracted_data:
			owner = frappe.db.get_value(row.extracted_data_type, row.extracted_data, "document_checklist")
			if owner and owner != doc.name:
				frappe.throw(_("Row {0}: {1} belongs to checklist {2}.").format(row.idx, row.extracted_data, owner))
		if row.document_status == "Verified" and row.extracted_data_type and not row.extracted_data:
			frappe.throw(_("Row {0}: link the extracted {1} before marking {2} Verified.").format(
				row.idx, row.extracted_data_type, row.document_name))
		if row.document_status == "Verified" and row.extracted_data_type == "Bank Statement Data" and row.extracted_data:
			months = cint(frappe.db.get_value("Bank Statement Data", row.extracted_data, "months_covered"))
			if months < MIN_BANK_MONTHS:
				frappe.throw(_("Row {0}: the bank statement covers {1} months; at least {2} are needed.").format(
					row.idx, months, MIN_BANK_MONTHS))


def applicant_pan(checklist):
	"""PAN from the checklist's PAN Card Data, if extracted."""
	return frappe.db.get_value("PAN Card Data", {"document_checklist": checklist, "pan_number": ("is", "set")}, "pan_number")


def make_checklists(app):
	"""One Document Checklist per applicant (primary + co-applicants/guarantors) with the standard rows,
	plus any extra documents from matching active Lender Document Rules. Returns how many were created."""
	from dsa_loan.dsa_loan_portal.doctype.loan_application.loan_application import matching_rules

	applicants = [app.primary_customer] + [r.applicant for r in app.co_applicants]
	created = 0
	for applicant in applicants:
		if frappe.db.exists("Document Checklist", {"loan_application": app.name, "applicant": applicant}):
			continue
		employment = frappe.db.get_value("Loan Customer", applicant, "employment_type")
		rows = standard_rows(employment)
		names = {r["document_name"] for r in rows}
		role = "Primary Applicant" if applicant == app.primary_customer else next(
			(r.applicant_type for r in app.co_applicants if r.applicant == applicant), "Co-Applicant")
		for rule in matching_rules(app, role, employment):
			if rule.document_name not in names:
				rows.append({"document_name": rule.document_name, "document_status": "Pending"})
				names.add(rule.document_name)
		frappe.get_doc(
			{"doctype": "Document Checklist", "loan_application": app.name, "applicant": applicant, "documents": rows}
		).insert(ignore_permissions=True)
		created += 1
	return created
