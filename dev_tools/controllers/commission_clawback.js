// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Commission Clawback", {
	refresh(frm) {
		if (frm.is_new()) return;
		const g = __("Go to");
		frm.add_custom_button(__("Commission"), () => frappe.set_route("Form", "Commission Calculation", frm.doc.commission_calculation), g);
		frm.add_custom_button(__("Loan Application"), () => frappe.set_route("Form", "Loan Application", frm.doc.loan_application), g);
		frm.add_custom_button(__("Credit Note"), () => frappe.set_route("List", "Commission Invoice",
			{ invoice_type: "Credit Note", remarks: ["like", "%" + frm.doc.name + "%"] }), g);
	},
});
