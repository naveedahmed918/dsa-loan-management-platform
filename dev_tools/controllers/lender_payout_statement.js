// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Lender Payout Statement", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (["Draft", "Pending Reconciliation"].includes(frm.doc.reconciliation_status)) {
			frm.set_intro(__("Enter what the lender's statement says (commission, TDS) and the <b>Actual Received Amount</b>, then save: "
				+ "the statement reconciles itself and marks the commissions Paid."), "blue");
		}
		frm.add_custom_button(__("Commissions in this statement"), () =>
			frappe.set_route("List", "Commission Calculation", { payout_statement: frm.doc.name }));
		frm.add_custom_button(__("Franchise Settlements"), () => frappe.set_route("List", "Franchise Settlement",
			{ settlement_period_from: frm.doc.period_from }), __("Go to"));
		frm.add_custom_button(__("Lender"), () => frappe.set_route("Form", "Lender", frm.doc.lender), __("Go to"));
	},
});
