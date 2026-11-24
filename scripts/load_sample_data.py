"""Load the sample data in apps/dsa_loan/sample_data/ into a site.

Run from <bench>/sites after `bench --site <site> migrate` (the site needs ERPNext and a Company):
    ../env/bin/python ../apps/dsa_loan/scripts/load_sample_data.py <site>                 # masters + demo loans
    ../env/bin/python ../apps/dsa_loan/scripts/load_sample_data.py <site> --masters-only  # master data only

- Records are written exactly as exported: same names, statuses and amounts. Controllers and automation
  are not re-run, so no commissions, invoices or emails are created by loading.
- Records whose name already exists on the site are skipped, so running it again is safe.
- The placeholder company is replaced by the site's default company. The lender invoice email groups are
  created empty: add your own members (Email Group Member) before invoices are emailed.
- Invoices are not part of the sample data: use Lender Invoice > Create & Email Invoice on a Disbursed
  application to raise one.
"""
import json
import os
import sys

import frappe

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sample_data")
# Set-up data reused by every loan. Employees come along because branches and lender logins point to them.
MASTERS = ["Employee", "Lender Type", "Lender", "Lender Branch", "Loan Product", "Loan Scheme", "Commission Slab Structure",
           "Lender Document Rule", "Franchise", "DSA Branch", "Lender Login", "Loan Customer"]


def site_company():
	company = frappe.defaults.get_global_default("company") or frappe.db.get_value("Company", {}, "name")
	if not company:
		frappe.throw("This site has no Company yet. Finish the ERPNext setup wizard first.")
	return company


def put(doc_dict, doctype, company):
	data = json.loads(json.dumps(doc_dict).replace('"__COMPANY__"', json.dumps(company)))
	data["doctype"] = doctype
	doc = frappe.get_doc(data)
	doc.db_insert()
	for child in doc.get_all_children():
		child.db_insert()


def load(commit=True, masters_only=False):
	manifest = json.load(open(os.path.join(DATA, "manifest.json"), encoding="utf-8"))
	company = site_company()
	for title in manifest["email_groups"]:
		if not frappe.db.exists("Email Group", title):
			frappe.get_doc({"doctype": "Email Group", "title": title}).insert(ignore_permissions=True)
	result = {}
	doctypes = ["Employee"] + manifest["order"]
	if masters_only:
		doctypes = [d for d in doctypes if d in MASTERS]
	for doctype in doctypes:
		rows = json.load(open(os.path.join(DATA, frappe.scrub(doctype) + ".json"), encoding="utf-8"))
		added = 0
		for row in rows:
			if frappe.db.exists(doctype, row["name"]):
				continue
			put(row, doctype, company)
			added += 1
		result[doctype] = (added, len(rows) - added)

	# each DocType numbers on from the highest loaded name; employees too
	from dsa_loan.patches.sync_naming_counters import execute as sync_counters

	sync_counters()
	top = frappe.db.sql("select max(cast(substring_index(name, '-', -1) as unsigned)) from tabEmployee where name like 'HR-EMP-%%'")[0][0]
	if top:
		frappe.db.sql("insert into tabSeries (name, current) values ('HR-EMP-', %s) on duplicate key update current = greatest(current, %s)",
		              (top, top))
	if commit:
		frappe.db.commit()
		frappe.clear_cache()
	return result


if __name__ == "__main__":
	site = next((a for a in sys.argv[1:] if not a.startswith("--")), "dsaloan.localhost")
	frappe.init(site=site, sites_path=".")
	frappe.connect()
	frappe.set_user("Administrator")
	try:
		for dt, (added, skipped) in load(masters_only="--masters-only" in sys.argv).items():
			print(f"{dt:<26} added {added:>3}   already there {skipped}")
		print("committed")
	except Exception:
		frappe.db.rollback()
		print("ROLLED BACK - nothing loaded")
		raise
	finally:
		frappe.destroy()
