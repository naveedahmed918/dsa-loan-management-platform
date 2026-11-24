// DSA Admin Dashboard page. The UI lives in public/js/dsa_admin_dashboard_v2.bundle.js;
// all data comes from dsa_loan.dashboard_v2.api (read-only, permission-aware).
frappe.pages["dsa-admin-dashboard-v2"].on_page_load = function (wrapper) {
	const set_active = (on) => document.body.classList.toggle("dl2-active", on);

	frappe.require("dsa_admin_dashboard_v2.bundle.js", () => {
		wrapper.dsa_dashboard = new dsa_loan.dashboard_v2.Dashboard(wrapper);
	});

	$(wrapper).on("show", () => {
		set_active(true);
		wrapper.dsa_dashboard && wrapper.dsa_dashboard.on_show();
	});
	$(wrapper).on("hide", () => set_active(false));
	set_active(true);

	// safety net: never leave Frappe's own navigation hidden on other screens
	if (!frappe.dsa_dashboard_v2_route_guard) {
		frappe.dsa_dashboard_v2_route_guard = true;
		$(document).on("page-change", () => {
			if (frappe.get_route()[0] !== "dsa-admin-dashboard-v2") document.body.classList.remove("dl2-active");
		});
	}
};
