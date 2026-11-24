// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Form 16 Data", {
	refresh(frm) {
		if (frm.is_new() || !frm.doc.document_checklist) return;
		frm.add_custom_button(__("Back to Checklist"), () =>
			frappe.set_route("Form", "Document Checklist", frm.doc.document_checklist)).addClass("btn-primary");
		if (frm.doc.loan_application) {
			frm.add_custom_button(__("Loan Application"), () => frappe.set_route("Form", "Loan Application", frm.doc.loan_application), __("Go to"));
		}
	},
});
