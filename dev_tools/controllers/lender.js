// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Lender", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (frm.doc.invoice_email_group) {
			frm.add_custom_button(__("Invoice Email Group members"), () => frappe.set_route("List", "Email Group Member",
				{ email_group: frm.doc.invoice_email_group }), __("Go to"));
		}
		frm.add_custom_button(__("New Loan Product"), () => frappe.new_doc("Loan Product", { lender: frm.doc.name }), __("New"));
		frm.add_custom_button(__("New Commission Slab"), () => frappe.new_doc("Commission Slab Structure", { lender: frm.doc.name }), __("New"));
		frm.add_custom_button(__("New Document Rule"), () => frappe.new_doc("Lender Document Rule", { lender: frm.doc.name }), __("New"));
	},
});
