// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Franchise Settlement", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Franchise"), () => frappe.set_route("Form", "Franchise", frm.doc.franchise), __("Go to"));
		frm.add_custom_button(__("Commissions"), () => frappe.set_route("List", "Commission Calculation",
			{ franchise: frm.doc.franchise }), __("Go to"));
	},
});
