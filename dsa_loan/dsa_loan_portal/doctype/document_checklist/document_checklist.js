// Copyright (c) 2026
// For license information, please see license.txt

const DOCUMENT_DATA_TYPES = [
	"Aadhaar Card Data",
	"PAN Card Data",
	"Address Proof Data",
	"Bank Statement Data",
	"Salary Slip Data",
	"ITR Data",
	"Form 16 Data",
];

frappe.ui.form.on("Document Checklist", {
	setup(frm) {
		frm.set_query("extracted_data_type", "documents", () => ({
			filters: { name: ["in", DOCUMENT_DATA_TYPES] },
		}));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		const rows = (frm.doc.documents || []).filter((r) => r.document_status !== "Not Applicable");
		const verified = rows.filter((r) => r.document_status === "Verified").length;
		const received = rows.filter((r) => r.document_status === "Received").length;
		frm.set_intro(__("{0} of {1} documents verified, {2} received and waiting to be verified. "
			+ "Open a row and use its <b>Create</b> button to enter that document's data.", [verified, rows.length, received]),
			verified === rows.length ? "green" : "blue");
		frm.add_custom_button(__("Back to Loan Application"), () =>
			frappe.set_route("Form", "Loan Application", frm.doc.loan_application));
		frm.add_custom_button(__("Applicant"), () => frappe.set_route("Form", "Loan Customer", frm.doc.applicant), __("Go to"));
		if (received) {
			frm.add_custom_button(__("Mark Received as Verified"), () =>
				frappe.call("dsa_loan.dsa_loan_portal.flow.verify_received", { checklist: frm.doc.name }).then((r) => {
					frappe.show_alert({ message: __("{0} rows verified", [r.message]), indicator: "green" });
					frm.reload_doc();
				}, () => frm.reload_doc())).addClass("btn-primary");
		}
	},
});

frappe.ui.form.on("Document Checklist Item", {
	extracted_data(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.extracted_data && row.document_status === "Pending") {
			frappe.model.set_value(cdt, cdn, "document_status", "Received");
		}
	},
	form_render(frm, cdt, cdn) {
		// Button inside the row editor: create the extracted-data record for this row.
		const row = locals[cdt][cdn];
		const grid_row = frm.fields_dict.documents.grid.grid_rows_by_docname[cdn];
		if (!grid_row || frm.is_new() || !row.extracted_data_type || row.extracted_data) return;
		const wrapper = grid_row.grid_form.wrapper;
		if (wrapper.find(".btn-create-extracted").length) return;
		$('<button class="btn btn-xs btn-primary btn-create-extracted" style="margin: 8px 0">'
			+ __("Create {0}", [row.extracted_data_type]) + "</button>")
			.prependTo(wrapper.find(".grid-form-body"))
			.on("click", () =>
				frappe.new_doc(row.extracted_data_type, {
					document_checklist: frm.doc.name,
					source_file: row.document_file,
				})
			);
	},
});
