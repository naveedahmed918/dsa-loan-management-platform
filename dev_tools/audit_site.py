"""Audit a site against the dsa_loan DocType JSON files: anything missing, different or extra.

Run from the bench:  cd sites && ../env/bin/python ../tools/audit_site.py dsaloan.localhost
"""
import glob
import json
import os
import sys

import frappe

SITE = sys.argv[1] if len(sys.argv) > 1 else "dsaloan.localhost"
MODULE = "DSA Loan Portal"
APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "apps", "dsa_loan", "dsa_loan", "dsa_loan_portal", "doctype"))
LEGACY = [
	"Customer Loan Application", "Franchise Commission Share", "Franchise Sub-DSA Partner", "Lender Agreement",
	"Lender Application", "Lender Application Document", "Lender Application Status Log", "Lender Commission Record",
	"Lender Commission Slab", "Lender Commission Tier", "Lender Disbursement", "Lender Document Checklist Item",
	"Lender Loan Product", "Lender Query", "Lender Scheme Rate Card", "Loan Co-applicant", "Loan Sanction Condition",
	"Lender Status", "DSA Customer",
	"Commission Slab", "Commission Invoice Item", "Payout Statement Item", "Franchise Settlement Item",
]
STD_COLS = {"name", "creation", "modified", "modified_by", "owner", "docstatus", "idx", "parent", "parentfield",
            "parenttype", "_user_tags", "_comments", "_assign", "_liked_by", "_seen", "naming_series"}
NO_COLUMN = {"Section Break", "Column Break", "Tab Break", "HTML", "Table", "Table MultiSelect", "Button", "Heading", "Fold", "Image"}

issues = []


def issue(kind, msg):
	issues.append((kind, msg))
	print(f"[{kind}] {msg}")


frappe.init(site=SITE, sites_path=".")
frappe.connect()

spec = {}
for p in glob.glob(os.path.join(APP_DIR, "*", "*.json")):
	if os.path.basename(os.path.dirname(p)) + ".json" == os.path.basename(p):
		d = json.load(open(p))
		spec[d["name"]] = d

# 1. DocTypes: spec vs database
db_dts = set(frappe.get_all("DocType", {"module": MODULE}, pluck="name"))
for dt in sorted(set(spec) - db_dts):
	issue("MISSING DOCTYPE", dt)
for dt in sorted(db_dts - set(spec)):
	issue("EXTRA DOCTYPE", dt)
for dt in LEGACY:
	if frappe.db.exists("DocType", dt):
		issue("LEGACY DOCTYPE", dt)

# 2. Fields: spec vs database meta, and extra DB columns
for dt, d in sorted(spec.items()):
	want = [(f["fieldname"], f["fieldtype"], (f.get("options") or ""), int(f.get("reqd") or 0)) for f in d["fields"]]
	have = frappe.get_all("DocField", {"parent": dt, "parenttype": "DocType"}, ["fieldname", "fieldtype", "options", "reqd"], order_by="idx")
	have = [(h.fieldname, h.fieldtype, h.options or "", int(h.reqd or 0)) for h in have]
	if want != have:
		ws, hs = {w[0]: w for w in want}, {h[0]: h for h in have}
		for fn in ws.keys() - hs.keys():
			issue("MISSING FIELD", f"{dt}.{fn}")
		for fn in hs.keys() - ws.keys():
			issue("EXTRA FIELD", f"{dt}.{fn}")
		for fn in ws.keys() & hs.keys():
			if ws[fn] != hs[fn]:
				issue("FIELD DIFFERS", f"{dt}.{fn}: spec {ws[fn][1:]} vs site {hs[fn][1:]}")
		if [w[0] for w in want] == [h[0] for h in have] or (ws.keys() == hs.keys()):
			if [w[0] for w in want] != [h[0] for h in have]:
				issue("FIELD ORDER", dt)
	cols = set(frappe.db.get_table_columns(dt))
	field_cols = {f["fieldname"] for f in d["fields"] if f["fieldtype"] not in NO_COLUMN}
	if d.get("is_submittable"):
		field_cols.add("amended_from")
	for c in sorted(cols - field_cols - STD_COLS):
		issue("EXTRA DB COLUMN", f"tab{dt}.{c}")
	for c in sorted(field_cols - cols):
		issue("MISSING DB COLUMN", f"tab{dt}.{c}")

# 3. Leftover tables of deleted DocTypes
for dt in LEGACY:
	if frappe.db.table_exists(dt):
		issue("LEFTOVER TABLE", f"tab{dt} ({frappe.db.count(dt)} rows)")

# 4. Customisations and other records tied to the module or its DocTypes
targets = list(spec) + LEGACY
checks = [
	("Custom Field", "dt"), ("Property Setter", "doc_type"), ("Client Script", "dt"), ("Server Script", "reference_doctype"),
	("Print Format", "doc_type"), ("Notification", "document_type"), ("Report", "ref_doctype"), ("List View Settings", "name"),
	("Workflow", "document_type"), ("Dashboard Chart", "document_type"), ("Number Card", "document_type"),
]
for dt, field in checks:
	if frappe.db.exists("DocType", dt):
		for r in frappe.get_all(dt, {field: ("in", targets)}, ["name", field]):
			issue("CUSTOMISATION", f"{dt}: {r.name} -> {r.get(field)}")
for dt in ("Workspace", "Page", "Report", "Web Form", "Dashboard", "Module Onboarding"):
	if frappe.db.exists("DocType", dt) and frappe.get_meta(dt).has_field("module"):
		for n in frappe.get_all(dt, {"module": MODULE}, pluck="name"):
			issue("MODULE RECORD", f"{dt}: {n}")
for n in frappe.get_all("Desktop Icon", {"name": ("like", "%DSA%")}, pluck="name") if frappe.db.exists("DocType", "Desktop Icon") else []:
	issue("DESKTOP ICON", n)

# 5. Data rows (should be none on a fresh site)
for dt in sorted(spec):
	n = frappe.db.count(dt)
	if n:
		print(f"[info] {dt} has {n} records")

frappe.destroy()
print(f"\n{len(spec)} DocTypes in spec, {len(db_dts)} in module on site; {len(issues)} issue(s).")
