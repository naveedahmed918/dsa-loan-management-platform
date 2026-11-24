frappe.pages["dsa-admin-dashboard"].on_page_load = function (wrapper) {
    frappe.require("dsa_admin_dashboard.bundle.js", function () {
        wrapper.dsa_admin_dashboard = new dsaLoanPortal.AdminDashboard(wrapper);
    });
};
frappe.pages["dsa-admin-dashboard"].on_page_show = function (wrapper) {
    if (wrapper.dsa_admin_dashboard) wrapper.dsa_admin_dashboard.refresh();
};
