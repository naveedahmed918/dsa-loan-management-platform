// Copyright (c) 2026
// For license information, please see license.txt

// Guided flow: a progress bar at the top, one primary "next step" button (with a dialog for the fields that
// step needs), the other outcomes under "Set Status", and direct links to checklists, customers and invoices.
const FLOW = "dsa_loan.dsa_loan_portal.flow.";
const PATH = ["Draft", "Documents Pending", "Ready for Submission", "Submitted", "Under Review", "Sanctioned",
	"Partially Disbursed", "Disbursed"];

frappe.ui.form.on("Loan Application", {
	setup(frm) {
		frm.set_query("lender_branch", () => ({ filters: { lender: frm.doc.lender, is_active: 1 } }));
		frm.set_query("loan_product", () => ({ filters: { lender: frm.doc.lender, is_active: 1 } }));
		frm.set_query("loan_scheme", () => ({
			filters: { loan_product: frm.doc.loan_product, scheme_status: "Active" },
		}));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		frappe.call({ method: FLOW + "application_flow", args: { application: frm.doc.name } }).then((r) => {
			const info = r.message || {};
			show_progress(frm, info);
			add_next_step(frm, info);
			add_documents(frm, info);
			add_other_outcomes(frm);
			add_invoice_buttons(frm);
		});
	},
	lender(frm) {
		frm.set_value({ lender_branch: "", loan_product: "", loan_scheme: "" });
	},
	loan_product(frm) {
		frm.set_value("loan_scheme", "");
	},
});

function money(v) {
	return format_currency(v || 0, "INR", 0);
}

function show_progress(frm, info) {
	const at = PATH.indexOf(frm.doc.final_status);
	const steps = PATH.map((s, i) => {
		const style = i < at ? "color: var(--green-600)" : i === at ? "font-weight: 700; color: var(--text-color)" : "color: var(--text-muted)";
		return `<span style="${style}">${i < at ? "&#10003; " : ""}${__(s)}</span>`;
	}).join(' <span class="text-muted">&rsaquo;</span> ');
	const lines = [at >= 0 ? steps : `<b>${__(frm.doc.final_status)}</b>`];

	const docs = (info.checklists || []).map((c) => {
		const done = c.total && c.verified === c.total;
		const flag = c.attention ? ` <span style="color: var(--red-500)">(${c.attention} to fix)</span>` : "";
		return `<a href="/app/document-checklist/${c.name}">${frappe.utils.escape_html(c.customer_name)}</a>: `
			+ `<span style="color: var(--${done ? "green-600" : "orange-500"})">${c.verified}/${c.total} verified</span>${flag}`;
	});
	if (docs.length) lines.push(`<b>${__("Documents")}</b> &nbsp;${docs.join(" &nbsp;|&nbsp; ")}`);

	if ((info.consent_missing || []).length) {
		lines.push(`<b>${__("Consent missing")}</b> &nbsp;` + info.consent_missing.map((c) =>
			`<a href="/app/loan-customer/${c.name}" style="color: var(--red-500)">${frappe.utils.escape_html(c.customer_name)}</a>`).join(", ")
			+ ` <span class="text-muted">${__("(tick KYC & Credit Check Consent on the customer)")}</span>`);
	}
	if (frm.doc.sanctioned_amount) {
		const comm = (info.commissions || []).reduce((t, c) => t + (c.gross_commission || 0), 0);
		lines.push(`<b>${__("Money")}</b> &nbsp;${__("Sanctioned")} ${money(frm.doc.sanctioned_amount)} &nbsp;|&nbsp; `
			+ `${__("Disbursed")} ${money(info.disbursed)} &nbsp;|&nbsp; ${__("Commission")} ${money(comm)}`
			+ (frm.doc.invoice_status ? ` &nbsp;|&nbsp; ${__("Invoice")}: <b>${__(frm.doc.invoice_status)}</b>` : ""));
	}
	frm.set_intro(lines.join("<br>"), "blue");
}

function set_status(frm, status, values) {
	// Saved on the server through the controller, so every rule still applies.
	const go = () => frappe.db.set_value("Loan Application", frm.doc.name, Object.assign({}, values || {}, { final_status: status }))
		.then(() => frm.reload_doc(), () => frm.reload_doc());
	if (frm.is_dirty()) {
		frappe.msgprint(__("Save your changes first."));
		return;
	}
	go();
}

function ask(frm, title, fields, status, primary) {
	const d = new frappe.ui.Dialog({
		title,
		fields,
		primary_action_label: primary || __("Save"),
		primary_action(values) {
			d.hide();
			if (status) set_status(frm, status, values);
		},
	});
	d.show();
	return d;
}

function add_next_step(frm, info) {
	const s = frm.doc.final_status;
	const today = frappe.datetime.get_today();
	const steps = {
		"Draft": [__("Next: Documents Pending"), () => set_status(frm, "Documents Pending")],
		"Documents Pending": [__("Next: Ready for Submission"), () => set_status(frm, "Ready for Submission")],
		"Ready for Submission": [__("Next: Submit to Lender"), () => ask(frm, __("Submit to {0}", [frm.doc.lender]), [
			{ fieldname: "lender_application_number", label: __("Lender Application Number"), fieldtype: "Data", reqd: 1,
				default: frm.doc.lender_application_number },
			{ fieldname: "lender_submission_date", label: __("Lender Submission Date"), fieldtype: "Date", reqd: 1, default: today },
			{ fieldname: "manager_approval", label: __("Manager Approval"), fieldtype: "Select",
				options: ["", "Pending", "Approved", "Rejected"], default: "Approved" },
		], "Submitted", __("Submit"))],
		"Submitted": [__("Next: Under Review"), () => set_status(frm, "Under Review")],
		"Query Raised": [__("Query answered: back to Under Review"), () => set_status(frm, "Under Review")],
		"On Hold": [__("Resume: back to Under Review"), () => set_status(frm, "Under Review")],
		"Under Review": [__("Next: Sanctioned"), () => ask(frm, __("Sanction details"), [
			{ fieldname: "sanction_date", label: __("Sanction Date"), fieldtype: "Date", reqd: 1, default: today },
			{ fieldname: "sanctioned_amount", label: __("Sanctioned Amount"), fieldtype: "Currency", reqd: 1,
				default: frm.doc.requested_loan_amount },
			{ fieldname: "sanctioned_interest_rate", label: __("Sanctioned Interest Rate"), fieldtype: "Percent",
				default: frm.doc.expected_interest_rate },
			{ fieldname: "sanctioned_tenure_months", label: __("Sanctioned Tenure (Months)"), fieldtype: "Int",
				default: frm.doc.requested_tenure_months },
			{ fieldname: "sanction_valid_until", label: __("Sanction Valid Until"), fieldtype: "Date",
				default: frappe.datetime.add_days(today, 90) },
		], "Sanctioned", __("Sanction"))],
		"Sanctioned": [__("Record Disbursement"), () => disburse(frm, info)],
		"Partially Disbursed": [__("Record Next Disbursement"), () => disburse(frm, info)],
	};
	const step = steps[s];
	if (step) frm.add_custom_button(step[0], step[1]).addClass("btn-primary");
}

function disburse(frm, info) {
	const first = !(info.tranches || []).some((t) => t.disbursement_status === "Confirmed");
	const d = ask(frm, __("Record disbursement {0}", [info.next_number]), [
		{ fieldname: "help", fieldtype: "HTML", options: `<p class="text-muted">${__(
			"Saved as Confirmed: the bank has released this money. The commission is created now; when the loan is fully "
			+ "disbursed the GST invoice is raised and emailed to the lender's invoice email group.")}</p>` },
		{ fieldname: "amount", label: __("Amount Released"), fieldtype: "Currency", reqd: 1, default: info.balance },
		{ fieldname: "disbursement_type", label: __("Type"), fieldtype: "Select", reqd: 1,
			options: first ? ["Full", "Part"] : ["Part", "Final"], default: first ? "Full" : "Final",
			description: __("Full / Final: the loan becomes Disbursed. Part: Partially Disbursed.") },
		{ fieldname: "disbursement_date", label: __("Disbursement Date"), fieldtype: "Date", reqd: 1,
			default: frappe.datetime.get_today() },
		{ fieldname: "payment_mode", label: __("Payment Mode"), fieldtype: "Select",
			options: ["", "NEFT", "RTGS", "IMPS", "Cheque", "Other"], default: "RTGS" },
		{ fieldname: "payment_reference", label: __("Payment Reference (UTR)"), fieldtype: "Data" },
		{ fieldname: "beneficiary_name", label: __("Beneficiary Name"), fieldtype: "Data" },
	], null, __("Record"));
	d.set_primary_action(__("Record"), (values) => {
		d.hide();
		frappe.call({
			method: FLOW + "record_disbursement",
			args: { application: frm.doc.name, values },
			freeze: true,
			freeze_message: __("Recording disbursement, commission and invoice..."),
		}).then((r) => {
			frappe.show_alert({ message: __("Disbursement {0} recorded", [r.message]), indicator: "green" });
			frm.reload_doc();
		}, () => frm.reload_doc());
	});
}

function add_documents(frm, info) {
	const lists = info.checklists || [];
	if (lists.length === 1) {
		frm.add_custom_button(__("Document Checklist"), () => frappe.set_route("Form", "Document Checklist", lists[0].name));
	} else {
		lists.forEach((c) => frm.add_custom_button(c.customer_name, () =>
			frappe.set_route("Form", "Document Checklist", c.name), __("Documents")));
	}
	frm.add_custom_button(__("Primary Customer"), () => frappe.set_route("Form", "Loan Customer", frm.doc.primary_customer),
		__("Go to"));
	if (frm.doc.loan_lead) {
		frm.add_custom_button(__("Loan Lead"), () => frappe.set_route("Form", "Loan Lead", frm.doc.loan_lead), __("Go to"));
	}
	(info.tranches || []).forEach((t) => frm.add_custom_button(__("Disbursement {0} ({1})", [t.disbursement_number, __(t.disbursement_status)]),
		() => frappe.set_route("Form", "Loan Disbursement", t.name), __("Go to")));
	(info.commissions || []).forEach((c) => frm.add_custom_button(__("Commission {0}", [c.name]),
		() => frappe.set_route("Form", "Commission Calculation", c.name), __("Go to")));
}

function add_other_outcomes(frm) {
	const s = frm.doc.final_status;
	const remarks = [{ fieldname: "application_remarks", label: __("Remarks"), fieldtype: "Small Text", reqd: 1,
		default: frm.doc.application_remarks }];
	const group = __("Set Status");
	if (["Submitted", "Under Review"].includes(s)) {
		frm.add_custom_button(__("Query Raised"), () => ask(frm, __("Lender's query"), remarks, "Query Raised"), group);
	}
	if (["Documents Pending", "Ready for Submission", "Submitted", "Under Review", "Query Raised", "Sanctioned"].includes(s)) {
		frm.add_custom_button(__("On Hold"), () => ask(frm, __("Put on hold"), remarks, "On Hold"), group);
		frm.add_custom_button(__("Rejected"), () => ask(frm, __("Rejected by lender"), [
			{ fieldname: "rejection_reason", label: __("Rejection Reason"), fieldtype: "Small Text", reqd: 1 }], "Rejected"), group);
		frm.add_custom_button(__("Withdrawn"), () => ask(frm, __("Withdrawn by customer"), remarks, "Withdrawn"), group);
	}
	if (s === "Disbursed") {
		frm.add_custom_button(__("Closed (loan repaid / foreclosed)"), () => ask(frm, __("Close the loan"), [
			{ fieldname: "help", fieldtype: "HTML", options: `<p class="text-muted">${__(
				"If this is within the lender's clawback window, a Commission Clawback and a Credit Note are created.")}</p>` },
			...remarks], "Closed", __("Close Loan")), group);
	}
}

function add_invoice_buttons(frm) {
	if (!["Disbursed", "Closed"].includes(frm.doc.final_status)) return;
	const call = (method, label) =>
		frappe.call({
			method: "dsa_loan.dsa_loan_portal.invoicing." + method,
			args: { application: frm.doc.name },
			freeze: true,
			freeze_message: label,
			callback: () => frm.reload_doc(),
		});
	const group = __("Lender Invoice");
	if (!frm.doc.sales_invoice) {
		frm.add_custom_button(__("Create & Email Invoice"), () => call("create_and_send", __("Raising invoice...")), group);
	} else {
		frm.add_custom_button(__("Open Sales Invoice"), () => frappe.set_route("Form", "Sales Invoice", frm.doc.sales_invoice), group);
		frm.add_custom_button(__("Send Invoice Email"), () => call("resend_email", __("Sending...")), group);
		if (frm.doc.invoice_communication) {
			frm.add_custom_button(__("Open Sent Email"), () => frappe.set_route("Form", "Communication", frm.doc.invoice_communication), group);
		}
	}
	if (frm.doc.invoice_status) {
		const colour = { Emailed: "green", "Invoice Created": "blue", "Email Pending": "orange", "Awaiting Commission": "orange", Failed: "red" };
		frm.dashboard.add_indicator(__("Invoice: {0}", [__(frm.doc.invoice_status)]), colour[frm.doc.invoice_status] || "gray");
	}
}
