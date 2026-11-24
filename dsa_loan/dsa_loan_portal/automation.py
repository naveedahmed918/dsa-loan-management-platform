"""Commission and settlement automation.

Event                                         Automatic result
--------------------------------------------  ------------------------------------------------------------------
Loan Disbursement becomes Confirmed           Commission Calculation (slab's %, GST and TDS rates)
Lender Sales Invoice raised (invoicing.py)    Commission Invoice linked to it; the commissions become Invoiced
1st of every month (scheduler)                Lender Payout Statement per lender and month for every commission no
                                              statement covers yet (last month, or a top-up for a month already
                                              reconciled), expected amount pre-filled
Payout statement Matched / Partially Matched  Franchise Settlement (Draft) for that period created or refreshed;
                                              a Debit Note (Draft) when the lender paid less than expected
Loan Application Closed inside the slab's     Commission Clawback for each commission on the loan
clawback window
Commission Clawback created                   Credit Note (Draft) for the clawed-back amount

Everything is created with ignore_permissions (the user who triggers it may not own commission records)
and never blocks the triggering save: a failure is logged and shown as a message instead.
"""

import frappe
from frappe import _
from frappe.utils import add_months, date_diff, flt, get_first_day, get_last_day, getdate, nowdate

COUNTED = ("Calculated", "Approved", "Invoiced", "Partially Paid", "Paid")


def _safely(label, fn, *args):
	"""Run fn; on failure roll back only its own work, log it and tell the user, never break the caller."""
	point = "dsa_auto_" + frappe.generate_hash(length=8)  # unique: these calls can nest
	frappe.db.savepoint(point)
	try:
		return fn(*args)
	except Exception as e:
		frappe.db.rollback(save_point=point)
		frappe.log_error(title=f"DSA automation: {label}")
		frappe.msgprint(_("{0} was not created automatically: {1}").format(label, e), indicator="orange", alert=True)


# ---------------------------------------------------------------- 1. commission on confirmed disbursement

def on_disbursement_confirmed(disbursement):
	return _safely(_("Commission Calculation"), create_commission, disbursement)


def create_commission(disbursement):
	if frappe.db.exists("Commission Calculation", {"loan_disbursement": disbursement.name, "calculation_status": ("!=", "Reversed")}):
		return None
	from dsa_loan.dsa_loan_portal.doctype.commission_slab_structure.commission_slab_structure import find_structure

	app = frappe.db.get_value("Loan Application", disbursement.loan_application,
		["lender", "loan_product", "loan_scheme"], as_dict=True)
	slab = find_structure(app.lender, app.loan_product, app.loan_scheme, disbursement.disbursement_date)
	if not slab:
		frappe.msgprint(_("No active Commission Slab Structure for {0}; create the Commission Calculation by hand.").format(app.lender),
			indicator="orange", alert=True)
		return None
	if not flt(frappe.db.get_value("Commission Slab Structure", slab, "commission_percentage")):
		frappe.msgprint(_("Commission Slab {0} has no Commission %; create the Commission Calculation by hand.").format(slab),
			indicator="orange", alert=True)
		return None
	calc = frappe.get_doc({"doctype": "Commission Calculation", "loan_application": disbursement.loan_application,
	                       "loan_disbursement": disbursement.name, "commission_slab": slab,
	                       "calculation_date": disbursement.disbursement_date})
	calc.insert(ignore_permissions=True)
	frappe.msgprint(_("Commission Calculation {0} created: {1}").format(calc.name, frappe.format(calc.gross_commission, "Currency")),
		alert=True)
	return calc


# ---------------------------------------------------------------- 2. commission invoice for the lender Sales Invoice

def on_sales_invoice_raised(app, invoice, lines):
	return _safely(_("Commission Invoice"), create_commission_invoice, app, invoice, lines)


def create_commission_invoice(app, invoice, lines):
	if frappe.db.exists("Commission Invoice", {"erpnext_sales_invoice": invoice.name}):
		return None
	tax = {"CGST": 0, "SGST": 0, "IGST": 0}
	for row in invoice.taxes:
		for kind in tax:
			if kind in (row.account_head or "").upper():
				tax[kind] += flt(row.tax_amount)
	tds = sum(flt(frappe.db.get_value("Commission Calculation", d.calculation, "tds_amount")) for d in lines)
	ci = frappe.get_doc({
		"doctype": "Commission Invoice", "company": invoice.company, "lender": app.lender, "invoice_type": "Commission",
		"invoice_number": invoice.name, "invoice_date": invoice.posting_date, "due_date": invoice.due_date,
		"invoice_status": "Submitted", "erpnext_sales_invoice": invoice.name, "taxable_amount": invoice.net_total,
		"cgst_amount": tax["CGST"], "sgst_amount": tax["SGST"], "igst_amount": tax["IGST"], "tds_expected": tds,
		"remarks": _("Raised automatically with {0} for {1}.").format(invoice.name, app.name)})
	ci.insert(ignore_permissions=True)
	for d in lines:
		status = frappe.db.get_value("Commission Calculation", d.calculation, "calculation_status")
		if status in ("Draft", "Calculated", "Approved"):
			frappe.db.set_value("Commission Calculation", d.calculation, "calculation_status", "Invoiced")
	return ci


# ---------------------------------------------------------------- 3. monthly payout statements

def create_monthly_payout_statements(month_start=None):
	"""Scheduler (1st of the month). Finds commissions that no payout statement covers yet - last month's, and any
	late or back-dated ones from earlier months - and, per lender and month, adds them to that month's open
	statement or creates a statement for them (a top-up when the month's statement is already reconciled).
	month_start limits it to one month (also lets the current month be done early). Safe to run again."""
	from dsa_loan.dsa_loan_portal.doctype.lender_payout_statement.lender_payout_statement import OPEN

	filters = {"calculation_status": ("in", COUNTED), "payout_statement": ("is", "not set")}
	if month_start:
		start = get_first_day(month_start)
		filters["calculation_date"] = ("between", [start, get_last_day(start)])
	else:
		filters["calculation_date"] = ("<", get_first_day(nowdate()))
	groups = {}
	for c in frappe.get_all("Commission Calculation", filters, ["lender", "calculation_date", "gross_commission", "tds_amount"]):
		groups.setdefault((c.lender, get_first_day(c.calculation_date)), []).append(c)

	made = []
	for (lender, start), calcs in sorted(groups.items()):
		end = get_last_day(start)
		open_one = frappe.db.get_value("Lender Payout Statement", {"lender": lender, "reconciliation_status": ("in", OPEN),
		                                "period_from": ("<=", end), "period_to": (">=", start)})
		if open_one:  # not reconciled yet: it simply takes the new commissions in
			frappe.get_doc("Lender Payout Statement", open_one).save(ignore_permissions=True)
			continue
		base = f"AUTO-{lender}-{start.strftime('%Y-%m')}"
		number, n = base, 1
		while frappe.db.exists("Lender Payout Statement", {"lender": lender, "statement_number": number}):
			n += 1
			number = f"{base}-{n}"
		top_up = n > 1 or frappe.db.exists("Lender Payout Statement", {"lender": lender, "period_from": ("<=", end),
		                                                                 "period_to": (">=", start)})
		doc = frappe.get_doc({
			"doctype": "Lender Payout Statement", "statement_number": number, "lender": lender, "statement_date": nowdate(),
			"period_from": start, "period_to": end,
			"total_lender_commission": sum(flt(c.gross_commission) for c in calcs),
			"total_tds": sum(flt(c.tds_amount) for c in calcs),
			"remarks": (_("Top-up: {0} commission(s) for this month arrived after its statement was reconciled. ").format(len(calcs))
			            if top_up else "")
			+ _("Created automatically with the expected commission. Correct the figures to the lender's statement "
			    "and enter the Actual Received Amount to reconcile.")})
		doc.insert(ignore_permissions=True)
		made.append(doc.name)
	return made


# ---------------------------------------------------------------- 4. after a payout is reconciled

def on_payout_reconciled(statement):
	_safely(_("Franchise Settlement"), refresh_franchise_settlements, statement)
	if statement.reconciliation_status == "Partially Matched":
		_safely(_("Debit Note"), debit_note_for_shortfall, statement)


def refresh_franchise_settlements(statement):
	franchises = {f for f in frappe.get_all("Commission Calculation", {
		"lender": statement.lender, "calculation_date": ("between", [statement.period_from, statement.period_to]),
		"franchise": ("is", "set")}, pluck="franchise")}
	for franchise in franchises:
		existing = frappe.get_all("Franchise Settlement", {
			"franchise": franchise, "settlement_status": ("!=", "Cancelled"),
			"settlement_period_from": ("<=", statement.period_to), "settlement_period_to": (">=", statement.period_from)},
			["name", "settlement_status"])
		if existing:
			for s in existing:
				if s.settlement_status == "Draft":  # recompute totals with the newly received commission
					frappe.get_doc("Franchise Settlement", s.name).save(ignore_permissions=True)
			continue
		code = frappe.db.get_value("Franchise", franchise, "franchise_code") or franchise
		frappe.get_doc({
			"doctype": "Franchise Settlement", "franchise": franchise, "settlement_status": "Draft",
			"settlement_number": f"AUTO-{code}-{getdate(statement.period_from).strftime('%Y-%m')}",
			"settlement_period_from": statement.period_from, "settlement_period_to": statement.period_to,
			"remarks": _("Created automatically when {0} was reconciled.").format(statement.name)}).insert(ignore_permissions=True)


def debit_note_for_shortfall(statement):
	short = flt(statement.total_expected_commission) - flt(statement.total_lender_commission)
	if short <= 1 or frappe.db.exists("Commission Invoice", {"invoice_type": "Debit Note", "remarks": ("like", f"%{statement.name}%")}):
		return None
	company = frappe.db.get_value("Commission Calculation", {"lender": statement.lender}, "company") or frappe.db.get_value("Company", {})
	return frappe.get_doc({
		"doctype": "Commission Invoice", "company": company, "lender": statement.lender, "invoice_type": "Debit Note",
		"invoice_status": "Draft", "taxable_amount": round(short, 2), "cgst_amount": round(short * 0.09, 2),
		"sgst_amount": round(short * 0.09, 2),
		"remarks": _("Shortfall on payout {0}: expected {1}, lender paid commission of {2}.").format(
			statement.name, statement.total_expected_commission, statement.total_lender_commission)}).insert(ignore_permissions=True)


# ---------------------------------------------------------------- 5. clawback on early closure, credit note per clawback

def on_application_closed(app):
	return _safely(_("Commission Clawback"), clawback_on_closure, app)


def clawback_on_closure(app):
	made = []
	for calc in frappe.get_all("Commission Calculation", {"loan_application": app.name, "calculation_status": ("!=", "Reversed")},
	                           ["name", "commission_slab", "loan_disbursement"]):
		window, pct = frappe.db.get_value("Commission Slab Structure", calc.commission_slab,
		                                  ["clawback_window_months", "clawback_percentage"])
		if not window or not flt(pct) or frappe.db.exists("Commission Clawback", {"commission_calculation": calc.name}):
			continue
		disbursed = frappe.db.get_value("Loan Disbursement", calc.loan_disbursement, "disbursement_date")
		if date_diff(nowdate(), disbursed) > window * 30.4:
			continue
		invoice = frappe.db.get_value("Commission Invoice", {"erpnext_sales_invoice": app.sales_invoice}) if app.sales_invoice else None
		doc = frappe.get_doc({"doctype": "Commission Clawback", "commission_calculation": calc.name, "commission_invoice": invoice,
		                      "clawback_reason": "Loan Closure", "clawback_percentage": pct,
		                      "remarks": _("Created automatically: loan closed within {0} months of disbursement.").format(window)})
		doc.insert(ignore_permissions=True)
		made.append(doc.name)
	if made:
		frappe.msgprint(_("Commission Clawback created: {0}").format(", ".join(made)), alert=True)
	return made


def on_clawback_created(clawback):
	return _safely(_("Credit Note"), credit_note_for_clawback, clawback)


def credit_note_for_clawback(clawback):
	company = frappe.db.get_value("Commission Calculation", clawback.commission_calculation, "company")
	amount = flt(clawback.clawback_amount)
	return frappe.get_doc({
		"doctype": "Commission Invoice", "company": company, "lender": clawback.lender, "invoice_type": "Credit Note",
		"invoice_status": "Draft", "taxable_amount": amount, "cgst_amount": round(amount * 0.09, 2),
		"sgst_amount": round(amount * 0.09, 2),
		"remarks": _("Credit for clawback {0} ({1}) on {2}.").format(clawback.name, clawback.clawback_reason,
		                                                           clawback.loan_application)}).insert(ignore_permissions=True)
