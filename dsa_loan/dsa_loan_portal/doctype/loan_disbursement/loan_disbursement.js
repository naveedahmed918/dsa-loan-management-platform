// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Loan Disbursement", {
	refresh(frm) {
		if (frm.is_new()) {
			frm.set_intro(__("Save as <b>Confirmed</b> once the bank has released the money: only Confirmed tranches move the loan "
				+ "forward, create the commission and (when fully disbursed) the lender invoice."), "blue");
			return;
		}
		frm.add_custom_button(__("Back to Loan Application"), () =>
			frappe.set_route("Form", "Loan Application", frm.doc.loan_application)).addClass("btn-primary");
		frappe.db.get_value("Commission Calculation", { loan_disbursement: frm.doc.name }, "name").then((r) => {
			const calc = r.message && r.message.name;
			if (calc) frm.add_custom_button(__("Commission {0}", [calc]), () => frappe.set_route("Form", "Commission Calculation", calc), __("Go to"));
		});
	},
});
