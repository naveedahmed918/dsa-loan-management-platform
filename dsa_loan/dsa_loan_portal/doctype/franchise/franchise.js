// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Franchise", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("New DSA Branch"), () => frappe.new_doc("DSA Branch", {
			franchise: frm.doc.name, company: frm.doc.company, branch_type: "Franchise Owned" }));
		frm.add_custom_button(__("New Settlement"), () => frappe.new_doc("Franchise Settlement", { franchise: frm.doc.name }));
	},
});
