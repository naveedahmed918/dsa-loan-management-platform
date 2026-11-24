"""Remove what the consolidated field spec (Nov 2026) replaced: legacy DocTypes, their tables,
and old columns left in reused tables.

`bench migrate` deletes orphan DocType records but keeps their tables, and never drops columns of
fields that were removed. This patch cleans both up, but only where nothing is lost: a table or
column that still holds data is kept and listed in the Error Log for manual migration.
"""

import frappe

LEGACY_DOCTYPES = [
	# child tables dropped from the final spec (only Co-Applicant stays)
	"Commission Slab",
	"Commission Invoice Item",
	"Payout Statement Item",
	"Franchise Settlement Item",
	# children / dependents first
	"Lender Application Document",
	"Lender Application Status Log",
	"Lender Document Checklist Item",
	"Lender Query",
	"Loan Sanction Condition",
	"Lender Commission Tier",
	"Lender Commission Record",
	"Lender Disbursement",
	"Lender Application",
	"Loan Co-applicant",
	"Customer Loan Application",
	"Lender Commission Slab",
	"Lender Scheme Rate Card",
	"Lender Loan Product",
	"Lender Agreement",
	"Franchise Commission Share",
	"Franchise Sub-DSA Partner",
]

MODULE = "DSA Loan Portal"

STANDARD_COLUMNS = {
	"name", "creation", "modified", "modified_by", "owner", "docstatus", "idx", "parent", "parentfield",
	"parenttype", "_user_tags", "_comments", "_assign", "_liked_by", "_seen",
}


def execute():
	kept = remove_legacy_doctypes() + trim_old_columns()
	if kept:
		frappe.log_error(
			title="dsa_loan: legacy data kept",
			message="These still hold data. Move it to the new DocTypes/fields, then remove them:\n" + "\n".join(kept),
		)


def remove_legacy_doctypes():
	kept = []
	for doctype in LEGACY_DOCTYPES:
		has_table = frappe.db.table_exists(doctype)
		if has_table and frappe.db.count(doctype):
			kept.append(f"table tab{doctype}")
			continue
		if frappe.db.exists("DocType", doctype):
			frappe.delete_doc("DocType", doctype, force=True, ignore_permissions=True, ignore_missing=True)
		if frappe.db.table_exists(doctype):
			frappe.db.sql_ddl(f"DROP TABLE `tab{doctype}`")
	return kept


def trim_old_columns():
	"""Drop columns of the module's DocTypes that no current field uses and that hold no values."""
	kept = []
	for doctype in frappe.get_all("DocType", {"module": MODULE}, pluck="name"):
		if not frappe.db.table_exists(doctype):
			continue
		frappe.clear_cache(doctype=doctype)
		meta = frappe.get_meta(doctype)
		current = {df.fieldname for df in meta.fields} | STANDARD_COLUMNS
		if meta.is_submittable:
			current.add("amended_from")
		for column in frappe.db.get_table_columns(doctype):
			if column in current:
				continue
			if column_has_values(doctype, column):
				kept.append(f"column tab{doctype}.{column}")
				continue
			frappe.db.sql_ddl(f"ALTER TABLE `tab{doctype}` DROP COLUMN `{column}`")
	return kept


def column_has_values(doctype, column):
	"""True when any row has something other than NULL, an empty string or zero."""
	return bool(
		frappe.db.sql(
			f"""SELECT 1 FROM `tab{doctype}`
			WHERE `{column}` IS NOT NULL
				AND CAST(`{column}` AS CHAR) <> ''
				AND CAST(`{column}` AS CHAR) NOT REGEXP '^-?0+([.]0+)?$'
			LIMIT 1"""
		)
	)
