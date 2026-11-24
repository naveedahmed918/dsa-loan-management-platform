"""Read-only APIs for the DSA admin dashboard (Aniket's dashboard v2, branch aniket/dsa/dashboard).

Adapted to this app's DocTypes: his version reads Lender Application / Lender Disbursement / Lender
Commission Record / Lender Query / Loan Sanction Condition, which do not exist here. The data returned has
the same shape his page (public/js/dsa_admin_dashboard_v2) expects.

Mapping
  Lender Application            -> Loan Application (date: application_date, status: final_status)
  submitted / approved amount   -> requested_loan_amount / sanctioned_amount
  Lender Disbursement Processed -> Loan Disbursement Confirmed (current_disbursement_amount)
  Lender Commission Pending     -> Commission Calculation not yet Paid / Reversed (gross_commission)
  Lender Query open             -> Loan Application in Query Raised
  Document awaiting verification-> Document Checklist rows Received / Under Verification
  Sanction conditions           -> sanctions expiring within 15 days
"""

from datetime import date, timedelta

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, getdate, nowdate, strip_html_tags

PAGE = "dsa-admin-dashboard-v2"
DEFAULT_PRESET = "this_month"
MAX_ROWS = 5000
PRESETS = [
	{"value": "today", "label": "Today"},
	{"value": "this_week", "label": "This Week"},
	{"value": "this_month", "label": "This Month"},
	{"value": "last_month", "label": "Last Month"},
	{"value": "this_quarter", "label": "This Quarter"},
	{"value": "this_year", "label": "This Year"},
	{"value": "custom", "label": "Custom Range"},
]
SANCTIONED_OR_LATER = ["Sanctioned", "Partially Disbursed", "Disbursed", "Closed"]
PIPELINE = ["Draft", "Documents Pending", "Ready for Submission", "Submitted", "Under Review", "Query Raised", "On Hold",
            "Sanctioned", "Partially Disbursed", "Disbursed", "Rejected", "Withdrawn", "Closed"]
COMMISSION_OPEN = ["Calculated", "Approved", "Invoiced", "Partially Paid"]


def _guard():
	frappe.only_for("System Manager")


def _read(doctype, fields, filters=None, order_by=None, limit=MAX_ROWS):
	if not frappe.has_permission(doctype, "read"):
		return []
	return frappe.get_list(doctype, fields=fields, filters=filters or None, order_by=order_by, limit_page_length=limit)


def _route(doctype, filters=None):
	return {"doctype": doctype, "filters": filters or {}}


def _period(preset, from_date=None, to_date=None):
	today = getdate(nowdate())
	if preset == "custom":
		if not from_date or not to_date:
			frappe.throw(_("Choose both From and To dates."))
		start, end = getdate(from_date), getdate(to_date)
		if start > end:
			frappe.throw(_("From date must be on or before To date."))
		return start, end
	if preset == "today":
		return today, today
	if preset == "this_week":
		start = today - timedelta(days=today.weekday())
		return start, start + timedelta(days=6)
	if preset == "last_month":
		end = today.replace(day=1) - timedelta(days=1)
		return end.replace(day=1), end
	if preset == "this_quarter":
		month = ((today.month - 1) // 3) * 3 + 1
		start = date(today.year, month, 1)
		nxt = date(today.year + (1 if month > 9 else 0), (month + 3 - 1) % 12 + 1, 1)
		return start, nxt - timedelta(days=1)
	if preset == "this_year":
		return date(today.year, 1, 1), date(today.year, 12, 31)
	if preset == "this_month":
		start = today.replace(day=1)
		end = date(today.year, 12, 31) if today.month == 12 else date(today.year, today.month + 1, 1) - timedelta(days=1)
		return start, end
	frappe.throw(_("Unknown date range."))


@frappe.whitelist()
def get_context():
	_guard()
	user = frappe.get_cached_doc("User", frappe.session.user)
	lenders = _read("Lender", ["name", "lender_name"], order_by="lender_name asc", limit=1000)
	sidebar = [
		{"key": "dashboard", "label": "Dashboard", "icon": "layout-dashboard", "items": [
			{"label": "Overview", "route": [PAGE]}]},
		{"key": "lenders", "label": "Lender Management", "icon": "landmark", "items": [
			{"label": "Lenders", "doctype": "Lender", "route": ["List", "Lender"]},
			{"label": "Loan Products", "doctype": "Loan Product", "route": ["List", "Loan Product"]},
			{"label": "Loan Schemes", "doctype": "Loan Scheme", "route": ["List", "Loan Scheme"]},
			{"label": "Lender Branches", "doctype": "Lender Branch", "route": ["List", "Lender Branch"]},
			{"label": "Commission Slabs", "doctype": "Commission Slab Structure", "route": ["List", "Commission Slab Structure"]}]},
		{"key": "operations", "label": "Operations", "icon": "briefcase-business", "items": [
			{"label": "Leads", "doctype": "Loan Lead", "route": ["List", "Loan Lead"]},
			{"label": "Customers", "doctype": "Loan Customer", "route": ["List", "Loan Customer"]},
			{"label": "Applications", "doctype": "Loan Application", "route": ["List", "Loan Application"]},
			{"label": "Documents", "doctype": "Document Checklist", "route": ["List", "Document Checklist"]},
			{"label": "Disbursements", "doctype": "Loan Disbursement", "route": ["List", "Loan Disbursement"]}]},
		{"key": "finance", "label": "Finance", "icon": "wallet", "items": [
			{"label": "Commissions", "doctype": "Commission Calculation", "route": ["List", "Commission Calculation"]},
			{"label": "Commission Invoices", "doctype": "Commission Invoice", "route": ["List", "Commission Invoice"]},
			{"label": "Payout Statements", "doctype": "Lender Payout Statement", "route": ["List", "Lender Payout Statement"]},
			{"label": "Clawbacks", "doctype": "Commission Clawback", "route": ["List", "Commission Clawback"]},
			{"label": "Franchise Settlements", "doctype": "Franchise Settlement", "route": ["List", "Franchise Settlement"]}]},
		{"key": "network", "label": "Branches & Franchises", "icon": "building-2", "items": [
			{"label": "DSA Branches", "doctype": "DSA Branch", "route": ["List", "DSA Branch"]},
			{"label": "Franchises", "doctype": "Franchise", "route": ["List", "Franchise"]}]},
		{"key": "reports", "label": "Reports & Analytics", "icon": "chart-no-axes-combined", "items": [
			{"label": "Reports", "route": ["List", "Report"]}]},
	]
	quick_actions = [{"label": label, "icon": icon, "doctype": dt} for label, icon, dt in [
		("New Lead", "plus", "Loan Lead"), ("New Application", "file-plus", "Loan Application"),
		("New Customer", "user-plus", "Loan Customer"), ("New Lender", "landmark", "Lender"),
		("New Payout Statement", "wallet", "Lender Payout Statement")] if frappe.has_permission(dt, "create")]
	return {
		"first_name": user.first_name or "", "full_name": user.full_name or "", "image": user.user_image or "",
		"user": frappe.session.user, "page": PAGE, "is_system_manager": "System Manager" in frappe.get_roles(),
		"presets": PRESETS, "default_preset": DEFAULT_PRESET,
		"lenders": [{"value": "", "label": "All Lenders"}] + [{"value": r.name, "label": r.lender_name or r.name} for r in lenders],
		"default_lender": "", "quick_actions": quick_actions, "sidebar": sidebar, "currency": "INR",
	}


@frappe.whitelist()
def get_overview(preset=None, lender=None, from_date=None, to_date=None):
	_guard()
	start, end = _period(preset or DEFAULT_PRESET, from_date, to_date)
	rng = [str(start), str(end)]
	sel = lender if lender and frappe.db.exists("Lender", lender) else ""
	lf = [["lender", "=", sel]] if sel else []
	lfd = {"lender": sel} if sel else {}

	lenders = _read("Lender", ["name", "lender_name", "lender_status", "lender_type"],
	                [["name", "=", sel]] if sel else [], "lender_name asc", 1000)
	apps = _read("Loan Application", ["name", "lender", "final_status", "requested_loan_amount", "sanctioned_amount",
	                                  "application_date", "loan_type", "dsa_branch"],
	             lf + [["application_date", "between", rng]], "application_date desc")
	sanctioned = [a for a in apps if a.final_status in SANCTIONED_OR_LATER]
	rejected = [a for a in apps if a.final_status == "Rejected"]

	disb = _read("Loan Disbursement", ["name", "lender", "current_disbursement_amount", "dsa_branch"],
	             lf + [["disbursement_status", "=", "Confirmed"], ["disbursement_date", "between", rng]])
	disbursed = flt(sum(flt(d.current_disbursement_amount) for d in disb), 2)

	comm = _read("Commission Calculation", ["name", "lender", "gross_commission"],
	             lf + [["calculation_status", "in", COMMISSION_OPEN], ["calculation_date", "between", rng]])
	pending_commission = flt(sum(flt(c.gross_commission) for c in comm), 2)

	queries = _read("Loan Application", ["name"], lf + [["final_status", "=", "Query Raised"]])

	pipeline = [{"label": s, "count": sum(1 for a in apps if a.final_status == s),
	             "route": _route("Loan Application", {"final_status": s, **lfd, "application_date": ["between", rng]})}
	            for s in PIPELINE]

	tasks = []
	app_names = [a.name for a in _read("Loan Application", ["name"], lf)] if sel else None
	cl_filters = [["Document Checklist Item", "document_status", "in", ["Received", "Under Verification"]]]
	if sel:
		cl_filters.append(["loan_application", "in", app_names or ["__none__"]])
	to_verify = sorted({c.name for c in _read("Document Checklist", ["name"], cl_filters, limit=1000)})  # one row per document
	if to_verify:
		tasks.append({"label": "Checklists with documents awaiting verification", "priority": "Medium", "count": len(to_verify),
		              "route": _route("Document Checklist", {"name": ["in", to_verify]})})
	if queries:
		tasks.append({"label": "Lender queries to answer", "priority": "High", "count": len(queries),
		              "route": _route("Loan Application", {"final_status": "Query Raised", **lfd})})
	expiring = _read("Loan Application", ["name"], lf + [["final_status", "=", "Sanctioned"],
	                 ["sanction_valid_until", "between", [nowdate(), add_days(nowdate(), 15)]]])
	if expiring:
		tasks.append({"label": "Sanctions expiring within 15 days", "priority": "High", "count": len(expiring),
		              "route": _route("Loan Application", {"name": ["in", [a.name for a in expiring]]})})
	waiting = _read("Loan Disbursement", ["name"], lf + [["disbursement_status", "in", ["Draft", "Pending"]]], limit=1000)
	if waiting:
		tasks.append({"label": "Disbursements not yet confirmed", "priority": "Medium", "count": len(waiting),
		              "route": _route("Loan Disbursement", {"disbursement_status": ["in", ["Draft", "Pending"]], **lfd})})

	perf = {r.name: {"lender": r.name, "lender_name": r.lender_name or r.name, "status": r.lender_status or "",
	                 "lender_type": r.lender_type or "", "applications": 0, "approved": 0, "disbursed": 0.0, "commission": 0.0}
	        for r in lenders}
	for a in apps:
		if a.lender in perf:
			perf[a.lender]["applications"] += 1
			perf[a.lender]["approved"] += a.final_status in SANCTIONED_OR_LATER
	for d in disb:
		if d.lender in perf:
			perf[d.lender]["disbursed"] += flt(d.current_disbursement_amount)
	for c in comm:
		if c.lender in perf:
			perf[c.lender]["commission"] += flt(c.gross_commission)

	kpis = [
		{"key": "lenders", "label": "Total Lenders", "value": len(lenders), "format": "Number",
		 "route": _route("Lender", {"name": sel} if sel else {}), "preview": "Lender master records in the selected lender scope."},
		{"key": "active_lenders", "label": "Active Lenders", "value": sum(1 for r in lenders if r.lender_status == "Active"),
		 "format": "Number", "route": _route("Lender", {"lender_status": "Active", **({"name": sel} if sel else {})}),
		 "preview": "Lenders whose status is Active."},
		{"key": "applications", "label": "Applications", "value": len(apps), "format": "Number",
		 "route": _route("Loan Application", {**lfd, "application_date": ["between", rng]}),
		 "preview": "Loan applications dated in the selected range."},
		{"key": "approved", "label": "Sanctioned", "value": len(sanctioned), "format": "Number",
		 "route": _route("Loan Application", {"final_status": ["in", SANCTIONED_OR_LATER], **lfd, "application_date": ["between", rng]}),
		 "preview": "Applications sanctioned or further along (part / fully disbursed, closed)."},
		{"key": "rejected", "label": "Rejected", "value": len(rejected), "format": "Number",
		 "route": _route("Loan Application", {"final_status": "Rejected", **lfd, "application_date": ["between", rng]}),
		 "preview": "Applications rejected by the lender."},
		{"key": "disbursed", "label": "Disbursed Amount", "value": disbursed, "format": "Currency",
		 "route": _route("Loan Disbursement", {"disbursement_status": "Confirmed", **lfd, "disbursement_date": ["between", rng]}),
		 "preview": "Sum of Confirmed disbursements in the selected range."},
		{"key": "commission", "label": "Commission Not Yet Paid", "value": pending_commission, "format": "Currency",
		 "route": _route("Commission Calculation", {"calculation_status": ["in", COMMISSION_OPEN], **lfd, "calculation_date": ["between", rng]}),
		 "preview": "Gross commission calculated but not yet fully paid by the lender."},
		{"key": "queries", "label": "Open Queries", "value": len(queries), "format": "Number",
		 "route": _route("Loan Application", {"final_status": "Query Raised", **lfd}),
		 "preview": "Applications where the lender has raised a query."},
	]
	return {
		"from_date": str(start), "to_date": str(end), "lender": sel, "currency": "INR",
		"data": {
			"kpis": kpis, "pipeline": pipeline, "tasks": tasks,
			"lenders": sorted(perf.values(), key=lambda i: (-i["applications"], i["lender_name"])),
			"disbursements": {"amount": disbursed, "count": len(disb), "average": flt(disbursed / len(disb), 2) if disb else 0},
			"commissions": {"pending_amount": pending_commission, "pending_count": len(comm)},
			"query_count": len(queries),
			"charts": _charts(start, end, rng, sel, lf, lfd, apps, disb, perf),
		},
	}


def _months(end, n=6):
	"""The n calendar months ending with the month of `end`, oldest first, as (first_day, last_day)."""
	out, y, m = [], end.year, end.month
	for _ in range(n):
		first = date(y, m, 1)
		last = (date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)) - timedelta(days=1)
		out.append((first, last))
		y, m = (y - 1, 12) if m == 1 else (y, m - 1)
	return out[::-1]


def _bucket(rows, field, months, value=None):
	vals = [0.0] * len(months)
	for r in rows:
		d = r.get(field)
		if not d:
			continue
		d = getdate(d)
		for i, (a, b) in enumerate(months):
			if a <= d <= b:
				vals[i] += flt(r.get(value)) if value else 1
				break
	return [flt(v, 2) for v in vals]


def _group(rows, key, value=None):
	out = {}
	for r in rows:
		k = r.get(key) or "Not set"
		g = out.setdefault(k, {"label": k, "count": 0, "amount": 0.0})
		g["count"] += 1
		g["amount"] += flt(r.get(value)) if value else 0
	return out


def _charts(start, end, rng, sel, lf, lfd, apps, disb, perf):
	"""Data for the dashboard visuals. Trends cover the 6 months up to the end of the selected range;
	everything else follows the selected range and lender."""
	months = _months(end)
	span = [str(months[0][0]), str(months[-1][1])]
	t_apps = _read("Loan Application", ["application_date"], lf + [["application_date", "between", span]])
	t_sanc = _read("Loan Application", ["sanction_date"], lf + [["sanction_date", "between", span]])
	t_disb = _read("Loan Disbursement", ["disbursement_date", "current_disbursement_amount"],
	               lf + [["disbursement_status", "=", "Confirmed"], ["disbursement_date", "between", span]])
	t_comm = _read("Commission Calculation", ["calculation_date", "gross_commission", "calculation_status"],
	               lf + [["calculation_status", "!=", "Reversed"], ["calculation_date", "between", span]])
	labels = [a.strftime("%b %y") for a, _ in months]
	trend = {
		"labels": labels, "range": span,
		"applications": _bucket(t_apps, "application_date", months),
		"sanctioned": _bucket(t_sanc, "sanction_date", months),
		"disbursed": _bucket(t_disb, "disbursement_date", months, "current_disbursement_amount"),
		"commission_earned": _bucket(t_comm, "calculation_date", months, "gross_commission"),
		"commission_paid": _bucket([c for c in t_comm if c.calculation_status == "Paid"], "calculation_date", months, "gross_commission"),
	}

	by_lender = sorted(({"label": p["lender_name"], "amount": flt(p["disbursed"], 2), "count": p["applications"],
	                     "route": _route("Loan Disbursement", {"lender": k, "disbursement_status": "Confirmed",
	                                                           "disbursement_date": ["between", rng]})}
	                    for k, p in perf.items() if p["disbursed"]), key=lambda r: -r["amount"])

	types = sorted(_group(apps, "loan_type", "requested_loan_amount").values(), key=lambda r: -r["count"])
	for t in types:
		t["route"] = _route("Loan Application", {"loan_type": t["label"], **lfd, "application_date": ["between", rng]})

	branches = _group(apps, "dsa_branch")
	for d in disb:
		b = branches.setdefault(d.dsa_branch or "Not set", {"label": d.dsa_branch or "Not set", "count": 0, "amount": 0.0})
		b["amount"] += flt(d.current_disbursement_amount)
	branches = sorted(branches.values(), key=lambda r: (-r["amount"], -r["count"]))
	for b in branches:
		b["route"] = _route("Loan Application", {"dsa_branch": b["label"], **lfd, "application_date": ["between", rng]})

	comm_all = _read("Commission Calculation", ["calculation_status", "gross_commission"],
	                 lf + [["calculation_date", "between", rng]])
	order = ["Calculated", "Approved", "Invoiced", "Partially Paid", "Paid", "Reversed", "Draft"]
	cs = _group(comm_all, "calculation_status", "gross_commission")
	commission = [dict(cs[s], route=_route("Commission Calculation", {"calculation_status": s, **lfd,
	                                                                     "calculation_date": ["between", rng]}))
	              for s in order if s in cs]

	app_names = [a.name for a in apps]
	docs = []
	if app_names:
		cl = frappe.get_all("Document Checklist", {"loan_application": ["in", app_names]}, pluck="name")
		items = frappe.get_all("Document Checklist Item", {"parent": ["in", cl or ["__none__"]], "parenttype": "Document Checklist"},
		                       ["document_status"])
		ds = _group(items, "document_status")
		d_order = ["Verified", "Under Verification", "Received", "Pending", "Resubmission Required", "Rejected", "Not Applicable"]
		docs = [dict(ds[s], route=_route("Document Checklist", {"name": ["in", cl]})) for s in d_order if s in ds]

	return {"trend": trend, "by_lender": by_lender, "loan_types": types, "branches": branches,
	        "commission_status": commission, "documents": docs}


@frappe.whitelist()
def search(txt=""):
	_guard()
	txt = (txt or "").strip().replace("%", "")[:60]
	if len(txt) < 2:
		return []
	like = f"%{txt}%"
	specs = [
		("Lender", ["lender_name", "name"], "lender_name", "lender_status"),
		("Loan Application", ["name", "lender_application_number"], None, "final_status"),
		("Loan Customer", ["customer_name", "mobile_number", "name"], "customer_name", "mobile_number"),
		("Loan Product", ["product_name", "product_code"], "product_name", "lender"),
	]
	out = []
	for doctype, match, title, sub in specs:
		if not frappe.has_permission(doctype, "read"):
			continue
		fields = list(dict.fromkeys(["name"] + [f for f in (title, sub) if f]))
		for row in frappe.get_list(doctype, fields=fields, or_filters=[[f, "like", like] for f in match],
		                           order_by="modified desc", limit_page_length=5):
			out.append({"doctype": doctype, "name": row.name, "title": (row.get(title) or row.name) if title else row.name,
			            "sub": (row.get(sub) or "") if sub else ""})
	return out


@frappe.whitelist()
def get_notifications():
	_guard()
	rows = frappe.get_list("Notification Log", filters={"for_user": frappe.session.user},
	                       fields=["name", "subject", "read", "creation", "document_type", "document_name"],
	                       order_by="creation desc", limit_page_length=20)
	return {
		"unread": sum(1 for r in rows if not r.get("read")),
		"items": [{"subject": strip_html_tags(r.get("subject") or ""), "read": cint(r.get("read")), "creation": str(r.get("creation") or ""),
		           "document_type": r.get("document_type") or "", "document_name": r.get("document_name") or ""} for r in rows],
	}
