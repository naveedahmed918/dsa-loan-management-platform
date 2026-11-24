"""Commission Calculation now records which Lender Payout Statement covers it. Link the existing ones.

A reconciled statement (Matched / Partially Matched / Closed) covers only the commissions it marked Paid or
Partially Paid; anything calculated later for that month stays unlinked, for the monthly job's top-up.
An open or disputed statement covers every unlinked commission in its period.
"""

import frappe

COUNTED = ("Calculated", "Approved", "Invoiced", "Partially Paid", "Paid")
RECONCILED = ("Matched", "Partially Matched", "Closed")


def execute():
	for st in frappe.get_all("Lender Payout Statement", fields=["name", "lender", "period_from", "period_to", "reconciliation_status"],
	                         order_by="creation"):
		statuses = ("Paid", "Partially Paid") if st.reconciliation_status in RECONCILED else COUNTED
		for calc in frappe.get_all("Commission Calculation", {
			"lender": st.lender, "calculation_date": ("between", [st.period_from, st.period_to]),
			"calculation_status": ("in", statuses), "payout_statement": ("is", "not set")}, pluck="name"):
			frappe.db.set_value("Commission Calculation", calc, "payout_statement", st.name, update_modified=False)
