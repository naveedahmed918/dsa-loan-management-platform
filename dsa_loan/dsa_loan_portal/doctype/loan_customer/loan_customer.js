// Copyright (c) 2026
// For license information, please see license.txt

frappe.ui.form.on("Loan Customer", {
	refresh(frm) {
		if (frm.is_new()) return;
		if (!frm.doc.kyc_consent) {
			frm.set_intro(__("Consent is missing: tick <b>KYC & Credit Check Consent</b> and choose the Consent Mode before "
				+ "the application can go to the lender, and before Aadhaar or CIBIL can be saved."), "orange");
		}
		frm.add_custom_button(__("New Loan Application"), () =>
			frappe.db.get_value("Loan Lead", { mobile_number: frm.doc.mobile_number, lead_status: ["!=", "Converted"] },
				["name", "loan_type", "estimated_loan_amount", "assigned_company", "assigned_agent"]).then((r) => {
				const lead = r.message || {};
				frappe.new_doc("Loan Application", {
					primary_customer: frm.doc.name,
					dsa_branch: frm.doc.dsa_branch,
					loan_lead: lead.name,
					loan_type: lead.loan_type,
					requested_loan_amount: lead.estimated_loan_amount,
					company: lead.assigned_company || frappe.defaults.get_default("company"),
					assigned_agent: lead.assigned_agent,
				});
			}));
	},
});
