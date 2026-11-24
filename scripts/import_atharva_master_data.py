"""Import the master data from branch atharva/home-loan-master-data (dsa_loan/fixtures/*.json) into a site.

Usage: cd ~/frappe/frappe-bench-v15/sites && ../env/bin/python ../apps/dsa_loan/scripts/import_atharva_master_data.py dsaloan.localhost [fixtures_dir, default scripts/data/atharva_fixtures]
Keeps the original record names, runs normal validation, skips records that already exist, all-or-nothing.
DSA Branch company is mapped to the site's company when the fixture's company does not exist.
"""
import json
import sys

import frappe

import os
SITE = sys.argv[1]
SRC = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "atharva_fixtures")
FILES = [("lender_type", "Lender Type"), ("lender", "Lender"), ("dsa_branch", "DSA Branch"),
         ("loan_product", "Loan Product"), ("loan_scheme", "Loan Scheme"), ("lender_document_rule", "Lender Document Rule")]
DROP = {"modified", "creation", "owner", "modified_by", "docstatus", "idx"}

frappe.init(site=SITE, sites_path=".")
frappe.connect()
frappe.set_user("Administrator")
company = frappe.db.get_value("Company", {})
errors = []
try:
	for f, dt in FILES:
		added = skipped = 0
		for r in json.load(open(f"{SRC}/{f}.json")):
			if frappe.db.exists(dt, r["name"]):
				skipped += 1
				continue
			data = {k: v for k, v in r.items() if k not in DROP}
			data["doctype"] = dt
			if dt == "DSA Branch" and not frappe.db.exists("Company", data.get("company")):
				data["company"] = company
			try:
				frappe.db.savepoint("row")
				frappe.get_doc(data).insert(set_name=r["name"])
				added += 1
			except Exception as e:
				frappe.db.rollback(save_point="row")
				errors.append(f"{dt} {r['name']}: {str(e)[:150]}")
		print(f"{dt:<22} added {added:>3}  already there {skipped}")
	# "format:LDR-{#####}" names draw from Frappe's shared counter (tabSeries key ""): keep it past LDR-000NN
	top = frappe.db.sql("select max(cast(substring(name, 5) as unsigned)) from `tabLender Document Rule` where name like 'LDR-%%'")[0][0] or 0
	frappe.db.sql("insert into tabSeries (name, current) values ('', %s) on duplicate key update current = greatest(current, %s)", (top, top))
	if errors:
		frappe.db.rollback()
		print("\nNOTHING SAVED, fix these first:\n  " + "\n  ".join(errors))
	else:
		frappe.db.commit()
		print("\ncommitted")
finally:
	frappe.destroy()
