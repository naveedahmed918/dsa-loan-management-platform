// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Commission Calculation", {
	refresh(frm) {
		if (frm.is_new()) return;
		const g = __("Go to");
		frm.add_custom_button(__("Loan Application"), () => frappe.set_route("Form", "Loan Application", frm.doc.loan_application), g);
		frm.add_custom_button(__("Disbursement"), () => frappe.set_route("Form", "Loan Disbursement", frm.doc.loan_disbursement), g);
		frm.add_custom_button(__("Commission Slab"), () => frappe.set_route("Form", "Commission Slab Structure", frm.doc.commission_slab), g);
		if (frm.doc.payout_statement) {
			frm.add_custom_button(__("Payout Statement"), () => frappe.set_route("Form", "Lender Payout Statement", frm.doc.payout_statement), g);
		}
		frappe.db.get_value("Loan Application", frm.doc.loan_application, "sales_invoice").then((r) => {
			const si = r.message && r.message.sales_invoice;
			if (si) frm.add_custom_button(__("Sales Invoice"), () => frappe.set_route("Form", "Sales Invoice", si), g);
		});
	},
});
