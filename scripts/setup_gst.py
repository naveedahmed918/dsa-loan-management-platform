"""GST on lender invoices: Output CGST / SGST / IGST accounts and two Sales Taxes and Charges Templates.

DSA commission is a taxable service at 18%. In-state (CGST 9% + SGST 9%) is the company default; use the
inter-state template (IGST 18%) on an invoice to a lender billed from another state.
With --reraise, lender invoices that were raised without tax are cancelled and raised again with GST.

Usage: cd ~/frappe/frappe-bench-v15/sites && ../env/bin/python ../apps/dsa_loan/scripts/setup_gst.py dsaloan.localhost [--reraise]
Safe to run again.
"""
import sys

import frappe


def account(company, abbr, name, parent, rate):
	full = f"{name} - {abbr}"
	if not frappe.db.exists("Account", full):
		frappe.get_doc({"doctype": "Account", "account_name": name, "company": company, "parent_account": parent,
		                "account_type": "Tax", "tax_rate": rate, "is_group": 0}).insert()
	return full


def template(company, abbr, title, rows, default):
	name = f"{title} - {abbr}"
	if not frappe.db.exists("Sales Taxes and Charges Template", name):
		frappe.get_doc({"doctype": "Sales Taxes and Charges Template", "title": title, "company": company, "is_default": default,
		                "taxes": [{"charge_type": "On Net Total", "account_head": acc, "rate": rate, "description": desc}
		                          for acc, rate, desc in rows]}).insert()
	return name


def run(reraise):
	for company, abbr in frappe.get_all("Company", fields=["name", "abbr"], as_list=True):
		parent = frappe.db.get_value("Account", {"company": company, "account_name": "Duties and Taxes", "is_group": 1})
		if not parent:
			print(f"{company}: no 'Duties and Taxes' group, skipped")
			continue
		cgst = account(company, abbr, "Output Tax CGST", parent, 9)
		sgst = account(company, abbr, "Output Tax SGST", parent, 9)
		igst = account(company, abbr, "Output Tax IGST", parent, 18)
		template(company, abbr, "Output GST In-state 18%", [(cgst, 9, "CGST @ 9%"), (sgst, 9, "SGST @ 9%")], 1)
		template(company, abbr, "Output GST Inter-state 18%", [(igst, 18, "IGST @ 18%")], 0)
		print(f"{company}: GST accounts and templates ready (In-state is the default)")

	if reraise:
		from dsa_loan.dsa_loan_portal.invoicing import process

		for app, si in frappe.get_all("Loan Application", {"sales_invoice": ("is", "set")}, ["name", "sales_invoice"], as_list=True):
			inv = frappe.get_doc("Sales Invoice", si)
			if inv.docstatus == 1 and not inv.total_taxes_and_charges:
				inv.flags.ignore_permissions = True
				inv.cancel()
				frappe.db.set_value("Loan Application", app, "sales_invoice", None)
				process(app)
				new_si = frappe.db.get_value("Loan Application", app, "sales_invoice")
				print(f"{app}: {si} cancelled, re-raised as {new_si} with GST "
				      f"{frappe.db.get_value('Sales Invoice', new_si, 'total_taxes_and_charges')}")


frappe.init(site=sys.argv[1] if len(sys.argv) > 1 else "dsaloan.localhost", sites_path=".")
frappe.connect()
frappe.set_user("Administrator")
try:
	run("--reraise" in sys.argv)
	frappe.db.commit()
	print("committed")
except Exception:
	frappe.db.rollback()
	raise
finally:
	frappe.destroy()
