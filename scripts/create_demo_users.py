"""One demo user per DSA role, limited to the right branch / franchise, for trying the permissions.

Test passwords are generated and written to <bench>/demo_users.txt (outside git); nothing is printed.
Usage: cd ~/frappe/frappe-bench-v15/sites && ../env/bin/python ../apps/dsa_loan/scripts/create_demo_users.py dsaloan.localhost
Safe to run again (existing users are kept; their access is re-applied).
"""
import os
import secrets
import sys

import frappe

# email, first name, role, DSA Branch, Franchise code, employee first name (to link)
USERS = [
	("dsa.admin@example.com", "Demo Admin", "DSA Admin", None, None, None),
	("priya.nair@example.com", "Priya", "Branch Manager", "LFS-PUN-01", None, "Priya"),
	("rahul.kulkarni@example.com", "Rahul", "DSA Agent", "LFS-PUN-01", None, "Rahul"),
	("sneha.joshi@example.com", "Sneha", "DSA Agent", "LFS-MUM-HO", None, "Sneha"),
	("doc.verifier@example.com", "Demo Verifier", "Document Verifier", None, None, None),
	("accounts@example.com", "Demo Accounts", "DSA Accounts", None, None, None),
	("rohit.pawar@example.com", "Rohit", "Franchise Partner", None, "KLP", "Rohit"),
]


def run():
	from frappe.utils.password import update_password

	from dsa_loan.dsa_loan_portal.access import grant_branch_access

	lines = ["Demo users (local test site only). Log in at http://dsaloan.localhost:8001\n"]
	for email, first, role, branch, franchise, employee in USERS:
		if frappe.db.exists("User", email):
			user = frappe.get_doc("User", email)
		else:
			user = frappe.get_doc({"doctype": "User", "email": email, "first_name": first, "send_welcome_email": 0,
			                       "user_type": "System User"}).insert(ignore_permissions=True)
		if role not in [r.role for r in user.roles]:
			user.add_roles(role)
		password = secrets.token_urlsafe(9)
		update_password(email, password)
		if branch:
			grant_branch_access(email, dsa_branch=branch)
		if franchise:
			grant_branch_access(email, franchise=frappe.db.get_value("Franchise", {"franchise_code": franchise}))
		if employee:
			emp = frappe.db.get_value("Employee", {"first_name": employee})
			if emp:
				frappe.db.set_value("Employee", emp, "user_id", email)
		scope = f"branch {branch}" if branch else f"franchise {franchise}" if franchise else "all branches"
		lines.append(f"{role:<18} {email:<30} {password}   ({scope})")
	path = os.path.abspath(os.path.join(frappe.utils.get_bench_path(), "demo_users.txt"))
	with open(path, "w") as fh:
		fh.write("\n".join(lines) + "\n")
	print(f"{len(USERS)} demo users ready; passwords written to {path}")


frappe.init(site=sys.argv[1] if len(sys.argv) > 1 else "dsaloan.localhost", sites_path=".")
frappe.connect()
frappe.set_user("Administrator")
try:
	run()
	frappe.db.commit()
except Exception:
	frappe.db.rollback()
	raise
finally:
	frappe.destroy()
