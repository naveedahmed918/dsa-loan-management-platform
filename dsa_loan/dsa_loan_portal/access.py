"""Roles and branch / franchise data separation.

Roles
-----
DSA Admin          masters (lenders, products, schemes, branches, franchises), read on everything else
Branch Manager     full control of leads, customers, applications and documents in their branch
DSA Agent          creates leads, customers, applications and uploads documents
Document Verifier  verifies document checklists and extracted document data
DSA Accounts       disbursements, commissions, invoices, payouts and franchise settlements
Franchise Partner  works their own franchise's leads and applications; reads their settlements

Which role can do what on each DocType is set in the DocType permissions (tools/generate_doctypes.py, ACCESS).

Data separation
---------------
A user only sees records of the DSA Branches they are given (a User Permission on DSA Branch). Every
customer-facing DocType carries a dsa_branch link, so Frappe filters lists, reports and links automatically.
A Franchise Partner also gets a User Permission on their Franchise, so they see only their settlements.
Users without any DSA Branch User Permission (e.g. head office) see every branch.
"""

import frappe
from frappe import _

ROLES = ["DSA Admin", "Branch Manager", "DSA Agent", "Document Verifier", "DSA Accounts", "Franchise Partner"]


def create_roles():
	"""Make sure the app's roles exist. Runs on install and before every migrate."""
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)


def _allow(user, doctype, value):
	if not frappe.db.exists("User Permission", {"user": user, "allow": doctype, "for_value": value}):
		frappe.get_doc(
			{"doctype": "User Permission", "user": user, "allow": doctype, "for_value": value, "apply_to_all_doctypes": 1}
		).insert(ignore_permissions=True)


@frappe.whitelist()
def grant_branch_access(user, dsa_branch=None, franchise=None):
	"""Limit `user` to one DSA Branch, or to a Franchise and all of its branches. Can be called again to add more."""
	frappe.only_for(("System Manager", "DSA Admin"))
	if not (dsa_branch or franchise):
		frappe.throw(_("Give a DSA Branch or a Franchise."))
	branches = [dsa_branch] if dsa_branch else []
	if franchise:
		_allow(user, "Franchise", franchise)
		branches += frappe.get_all("DSA Branch", {"franchise": franchise}, pluck="name")
		if not branches:
			frappe.throw(_("Franchise {0} has no DSA Branch yet; create its branch first.").format(franchise))
	for branch in set(branches):
		_allow(user, "DSA Branch", branch)
	return sorted(set(branches))


def sync_franchise_branch(doc, method=None):
	"""DSA Branch hook: users of a franchise automatically get access to its new branches."""
	if not doc.franchise:
		return
	for user in frappe.get_all("User Permission", {"allow": "Franchise", "for_value": doc.franchise}, pluck="user"):
		_allow(user, "DSA Branch", doc.name)
