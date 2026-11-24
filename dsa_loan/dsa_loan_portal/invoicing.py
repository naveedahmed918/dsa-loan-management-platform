"""Lender invoice on disbursement.

When a Loan Application becomes Disbursed (and the lender has Auto Invoice on Disbursement ticked):

1. Wait until every Confirmed disbursement has a Commission Calculation (status "Awaiting Commission").
2. Raise and submit an ERPNext Sales Invoice on the lender's ERPNext Customer, one line per commission.
3. Render the lender's Email Template (default "DSA Disbursement Invoice") and email it, with the invoice
   PDF, to the lender's Invoice Email Group (or its Official Email).
4. Keep the email as a Communication linked to the Sales Invoice, the Loan Application and the Lender,
   and record the outcome on the Loan Application (Lender Invoice section).

If no outgoing Email Account is set up, the message is still saved (status "Email Pending") and can be sent
later with the "Send Invoice Email" button.
"""

import frappe
from frappe import _
from frappe.utils import add_days, flt, now_datetime, nowdate

ITEM_CODE = "DSA Commission"
DEFAULT_TEMPLATE = "DSA Disbursement Invoice"
PAYMENT_DAYS = 30

TEMPLATE_SUBJECT = (
	"Loan Disbursed: {{ customer.customer_name }} ({{ app.lender_application_number or app.name }}) - Invoice {{ invoice.name }}"
)
TEMPLATE_BODY = """<p>Dear {{ lender.contact_person or (lender.lender_name ~ " team") }},</p>

<p style="font-size:15px"><b>Status: Loan Disbursed</b>
({{ frappe.format(disbursements[-1].disbursement_date, "Date") if disbursements else "" }})</p>

<p>The home loan of <b>{{ customer.customer_name }}</b> (your reference
<b>{{ app.lender_application_number or "-" }}</b>, our application {{ app.name }}) has been fully disbursed.
Please find attached our invoice <b>{{ invoice.name }}</b> for the DSA commission.</p>

<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse">
  <tr><th align="left">Disbursement</th><th align="left">Date</th><th align="right">Amount disbursed</th><th align="right">Commission</th></tr>
  {% for d in disbursements %}
  <tr><td>{{ d.disbursement_number }}</td><td>{{ frappe.format(d.disbursement_date, "Date") }}</td>
      <td align="right">{{ frappe.format(d.current_disbursement_amount, "Currency") }}</td>
      <td align="right">{{ frappe.format(d.commission, "Currency") }}</td></tr>
  {% endfor %}
</table>

<p>Sanctioned amount: {{ frappe.format(app.sanctioned_amount, "Currency") }}<br>
Invoice total: <b>{{ frappe.format(invoice.grand_total, "Currency") }}</b><br>
Due date: {{ frappe.format(invoice.due_date, "Date") }}</p>

<p>Kindly arrange payment by the due date and quote the invoice number in your remittance advice.</p>

<p>Regards,<br>{{ invoice.company }}</p>
"""


# ---------------------------------------------------------------- setup

def ensure_setup():
	"""Service item and default email template. Runs after every migrate."""
	if not frappe.db.exists("DocType", "Item"):
		return  # ERPNext not installed
	if not frappe.db.exists("Item", ITEM_CODE):
		group = "Services" if frappe.db.exists("Item Group", "Services") else frappe.db.get_value("Item Group", {"is_group": 0})
		frappe.get_doc({
			"doctype": "Item", "item_code": ITEM_CODE, "item_name": ITEM_CODE, "item_group": group,
			"stock_uom": "Nos", "is_stock_item": 0, "is_sales_item": 1, "is_purchase_item": 0,
			"description": "Commission earned as Direct Selling Agent on a disbursed loan",
		}).insert(ignore_permissions=True)
	if not frappe.db.exists("Email Template", DEFAULT_TEMPLATE):
		frappe.get_doc({
			"doctype": "Email Template", "name": DEFAULT_TEMPLATE, "subject": TEMPLATE_SUBJECT,
			"use_html": 1, "response_html": TEMPLATE_BODY,
		}).insert(ignore_permissions=True)


# ---------------------------------------------------------------- triggers

def on_application_update(app):
	"""Loan Application on_update: start invoicing when the loan is marked Disbursed by hand."""
	if app.final_status == "Disbursed" and app.has_value_changed("final_status"):
		start_invoicing(app)


def start_invoicing(app):
	"""Called whenever an application becomes Disbursed (by hand or by its final disbursement)."""
	if not app.sales_invoice and frappe.db.get_value("Lender", app.lender, "auto_invoice_on_disbursement"):
		process(app.name)


def on_commission_update(doc, method=None):
	"""Commission Calculation hook: the last missing commission completes a waiting invoice."""
	status, invoice = frappe.db.get_value("Loan Application", doc.loan_application, ["final_status", "sales_invoice"])
	if status == "Disbursed" and not invoice and doc.calculation_status != "Reversed":
		if frappe.db.get_value("Lender", doc.lender, "auto_invoice_on_disbursement"):
			process(doc.loan_application)


@frappe.whitelist()
def create_and_send(application):
	"""Form button: create the invoice (if missing) and email it."""
	frappe.get_doc("Loan Application", application).check_permission("write")
	return process(application, manual=True)


@frappe.whitelist()
def resend_email(application):
	"""Form button: email the existing invoice again."""
	app = frappe.get_doc("Loan Application", application)
	app.check_permission("write")
	if not app.sales_invoice:
		frappe.throw(_("Create the invoice first."))
	return send_invoice_email(app)


# ---------------------------------------------------------------- work

def _set(app, **values):
	app.update(values)
	frappe.db.set_value("Loan Application", app.name, values, update_modified=False)


def commission_lines(app):
	"""(lines, missing): one line per Confirmed disbursement with its commission; missing = disbursements without one."""
	disbursements = frappe.get_all(
		"Loan Disbursement",
		{"loan_application": app.name, "disbursement_status": "Confirmed"},
		["name", "disbursement_number", "disbursement_date", "current_disbursement_amount"],
		order_by="disbursement_date asc, creation asc",
	)
	lines, missing = [], []
	for d in disbursements:
		calc = frappe.db.get_value(
			"Commission Calculation",
			{"loan_disbursement": d.name, "calculation_status": ("!=", "Reversed")},
			["name", "gross_commission", "commission_percentage"],
			as_dict=True,
		)
		if calc and flt(calc.gross_commission) > 0:
			d.update(commission=flt(calc.gross_commission), calculation=calc.name, percentage=calc.commission_percentage)
			lines.append(d)
		else:
			missing.append(d.disbursement_number)
	return lines, missing


def process(application, manual=False):
	app = frappe.get_doc("Loan Application", application)
	if app.final_status not in ("Disbursed", "Closed"):  # a closed loan was disbursed first
		frappe.throw(_("The invoice is raised only once the application is Disbursed."))
	if not app.sales_invoice or frappe.db.get_value("Sales Invoice", app.sales_invoice, "docstatus") == 2:
		lines, missing = commission_lines(app)
		if missing or not lines:
			_set(app, invoice_status="Awaiting Commission",
			     invoice_error=_("Commission Calculation missing for disbursement(s): {0}").format(", ".join(missing) or "-"))
			if manual:
				frappe.throw(app.invoice_error)
			return app.invoice_status
		point = "dsa_invoice_" + frappe.generate_hash(length=8)
		frappe.db.savepoint(point)
		try:
			invoice = make_sales_invoice(app, lines)
		except Exception as e:
			frappe.db.rollback(save_point=point)
			frappe.log_error(title=f"DSA invoice failed for {app.name}")
			_set(app, invoice_status="Failed", invoice_error=str(e)[:500])
			if manual:
				raise
			frappe.msgprint(_("Could not create the lender invoice: {0}").format(e), indicator="red", alert=True)
			return app.invoice_status
		_set(app, sales_invoice=invoice.name, invoice_amount=invoice.grand_total, invoice_status="Invoice Created", invoice_error=None)
		from dsa_loan.dsa_loan_portal.automation import on_sales_invoice_raised

		on_sales_invoice_raised(app, invoice, lines)
		frappe.msgprint(_("Sales Invoice {0} raised on {1}.").format(invoice.name, app.lender), alert=True)
	return send_invoice_email(app)


def lender_customer(lender_name):
	lender = frappe.get_doc("Lender", lender_name)
	if lender.erpnext_customer and frappe.db.exists("Customer", lender.erpnext_customer):
		return lender.erpnext_customer
	existing = frappe.db.get_value("Customer", {"customer_name": lender.lender_name})
	if not existing:
		group = "Commercial" if frappe.db.exists("Customer Group", "Commercial") else frappe.db.get_value("Customer Group", {"is_group": 0})
		territory = "India" if frappe.db.exists("Territory", "India") else frappe.db.get_value("Territory", {"is_group": 0})
		existing = frappe.get_doc({
			"doctype": "Customer", "customer_name": lender.lender_name, "customer_type": "Company",
			"customer_group": group, "territory": territory, "tax_id": lender.gstin,
		}).insert(ignore_permissions=True).name
	frappe.db.set_value("Lender", lender.name, "erpnext_customer", existing)
	return existing


def make_sales_invoice(app, lines):
	customer_name = frappe.db.get_value("Loan Customer", app.primary_customer, "customer_name")
	si = frappe.new_doc("Sales Invoice")
	si.update({
		"company": app.company,
		"customer": lender_customer(app.lender),
		"posting_date": nowdate(),
		"due_date": add_days(nowdate(), PAYMENT_DAYS),
		"remarks": _("DSA commission for Loan Application {0} ({1}), lender reference {2}").format(
			app.name, customer_name, app.lender_application_number or "-"),
	})
	for d in lines:
		si.append("items", {
			"item_code": ITEM_CODE,
			"qty": 1,
			"rate": d.commission,
			"description": _("Commission{0} on disbursement {1} of {2} dated {3} - {4} ({5})").format(
				f" @ {flt(d.percentage)}%" if d.percentage else "", d.disbursement_number,
				frappe.format(d.current_disbursement_amount, "Currency"), frappe.format(d.disbursement_date, "Date"),
				customer_name, app.name),
		})
	taxes = frappe.db.get_value("Sales Taxes and Charges Template", {"company": app.company, "is_default": 1, "disabled": 0})
	if taxes:
		si.taxes_and_charges = taxes
	si.set_missing_values()
	if taxes:
		si.set_taxes()
	si.flags.ignore_permissions = True
	si.insert()
	si.submit()
	return si


def outgoing_account():
	from frappe.email.doctype.email_account.email_account import EmailAccount

	try:
		return EmailAccount.find_outgoing(match_by_doctype="Sales Invoice")
	except Exception:
		return None


def recipients_for(lender):
	"""Members of the lender's Invoice Email Group. Official Email is used only when no group is set:
	a group that exists but is empty means "nobody yet", never "fall back to the bank's public address"."""
	if lender.invoice_email_group:
		emails = frappe.get_all(
			"Email Group Member", {"email_group": lender.invoice_email_group, "unsubscribed": 0}, pluck="email", order_by="creation"
		)
	else:
		emails = [lender.official_email] if lender.official_email else []
	cc = [e.strip() for e in (lender.invoice_cc or "").replace(";", ",").split(",") if e.strip()]
	return emails, cc


def render_message(app, invoice, lender):
	template = frappe.get_doc("Email Template", lender.invoice_email_template or DEFAULT_TEMPLATE)
	lines, _missing = commission_lines(app)
	ctx = {
		"app": app, "invoice": invoice, "lender": lender, "disbursements": lines,
		"customer": frappe.get_doc("Loan Customer", app.primary_customer),
	}
	body = template.response_html if template.use_html else template.response
	return frappe.render_template(template.subject, ctx), frappe.render_template(body or "", ctx), template.name


def send_invoice_email(app):
	from frappe.core.doctype.communication.email import _make

	lender = frappe.get_doc("Lender", app.lender)
	invoice = frappe.get_doc("Sales Invoice", app.sales_invoice)
	to, cc = recipients_for(lender)
	subject, message, template = render_message(app, invoice, lender)
	account = outgoing_account()
	send = bool(account and to)

	comm = _make(
		doctype="Sales Invoice",
		name=invoice.name,
		subject=subject,
		content=message,
		sender=account.email_id if account else None,
		recipients=to,
		cc=cc,
		send_email=send,
		print_format=frappe.get_meta("Sales Invoice").default_print_format or "Standard",
		email_template=template,
		print_letterhead=True,
	)
	communication = frappe.get_doc("Communication", comm["name"])
	communication.add_link("Loan Application", app.name)
	communication.add_link("Lender", lender.name)
	communication.save(ignore_permissions=True)

	if send:
		_set(app, invoice_status="Emailed", invoice_emailed_on=now_datetime(), invoice_email_recipients=", ".join(to + cc),
		     invoice_communication=communication.name, invoice_error=None)
		frappe.msgprint(_("Invoice {0} emailed to {1}.").format(invoice.name, ", ".join(to)), alert=True)
	else:
		reason = _("No recipients: add members to the lender's Invoice Email Group.") if not to else _(
			"No outgoing Email Account is set up; the message is saved and can be sent later.")
		_set(app, invoice_status="Email Pending", invoice_email_recipients=", ".join(to + cc),
		     invoice_communication=communication.name, invoice_error=reason)
		frappe.msgprint(reason, indicator="orange", alert=True)
	return app.invoice_status


def grant_accounts_access():
	"""DSA Accounts works with the ERPNext invoices and customers this module creates."""
	from frappe.permissions import add_permission, update_permission_property

	rights = {"Sales Invoice": ("read", "write", "create", "submit", "cancel", "print", "email", "report"),
	          "Customer": ("read", "write", "create", "report")}
	for doctype, props in rights.items():
		if not frappe.db.exists("DocType", doctype):
			continue
		if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": "DSA Accounts", "permlevel": 0}):
			add_permission(doctype, "DSA Accounts", 0)
			for p in props:
				update_permission_property(doctype, "DSA Accounts", 0, p, 1, validate=False)


def after_migrate():
	ensure_setup()
	grant_accounts_access()
