(() => {
  // ../dsa_loan/dsa_loan/public/js/dsa_admin_dashboard.bundle.js
  (() => {
    const API = "dsa_loan.dashboard.api.";
    const $ = (sel, root = document) => root.querySelector(sel);
    const esc = (v) => frappe.utils.escape_html(String(v != null ? v : ""));
    const money = (v, currency) => frappe.format(v || 0, { fieldtype: "Currency", options: currency });
    const count = (v) => v == null ? "No access" : String(v);
    const palette = ["#0f766e", "#34a88a", "#d97706", "#64748b", "#2563eb", "#8b5cf6"];
    class AdminDashboard {
      constructor(wrapper) {
        this.wrapper = wrapper;
        this.root = document.createElement("div");
        this.root.className = "dsa-admin";
        wrapper.innerHTML = "";
        wrapper.appendChild(this.root);
        this.preset = "this_month";
        this.company = null;
        this.init();
      }
      async init() {
        try {
          this.ctx = await frappe.xcall(API + "get_context");
          this.company = this.ctx.default_company;
          this.renderShell();
          await this.refresh();
        } catch (e) {
          this.root.innerHTML = `<div class="dsa-error">Unable to load dashboard. Sign in with a System Manager account and refresh.</div>`;
        }
      }
      renderShell() {
        const companyOptions = (this.ctx.companies || []).map((c) => `<option value="${esc(c.name)}">${esc(c.name)}</option>`).join("");
        this.root.innerHTML = `
              <header class="dsa-top"><div class="dsa-brand"><span class="dsa-mark">D</span><div><b>DSA Loan Portal</b><small>Business overview</small></div></div>
              <div class="dsa-top-right"><span class="dsa-user">${esc(this.ctx.full_name)}</span></div></header>
              <div class="dsa-layout"><aside class="dsa-side"><div class="dsa-side-title">WORKSPACE</div><a class="dsa-nav active" href="/app/dsa-admin-dashboard">Overview</a>
              ${(this.ctx.sidebar || []).map((g) => `<div class="dsa-group">${esc(g.label)}</div>${g.items.map((i) => `<a class="dsa-nav" href="/app/${i.route[1].toLowerCase().replace(/ /g, "-")}">${esc(i.label)}</a>`).join("")}`).join("")}
              </aside><main class="dsa-main"><div class="dsa-welcome"><div><div class="dsa-eyebrow">ADMINISTRATION / OVERVIEW</div><h1>Welcome back, ${esc(this.ctx.full_name.split(" ")[0])}</h1><p>Your DSA business at a glance.</p></div>
              <div class="dsa-filters"><select id="dsa-range"><option value="today">Today</option><option value="this_week">This Week</option><option value="this_month" selected>This Month</option><option value="last_month">Last Month</option><option value="this_quarter">This Quarter</option><option value="this_year">This Year</option></select>
              <select id="dsa-company">${companyOptions}</select><button id="dsa-refresh">Refresh</button></div></div>
              <div id="dsa-period" class="dsa-period"></div><div id="dsa-kpis" class="dsa-kpis"></div>
              <div class="dsa-grid"><section class="dsa-card"><div class="dsa-card-head"><div><h3>Application pipeline</h3><p>Customer applications by current status</p></div></div><div id="dsa-status" class="dsa-chart"></div></section>
              <section class="dsa-card"><div class="dsa-card-head"><div><h3>Loan type mix</h3><p>Distribution across loan products</p></div></div><div id="dsa-loantypes" class="dsa-chart"></div></section>
              <section class="dsa-card"><div class="dsa-card-head"><div><h3>Lender portfolio</h3><p>Registered lenders by type</p></div></div><div id="dsa-lendertypes" class="dsa-chart"></div></section>
              <section class="dsa-card"><div class="dsa-card-head"><div><h3>Latest lenders</h3><p>Recently updated lender records</p></div></div><div id="dsa-lenders"></div></section>
              <section class="dsa-card dsa-wide"><div class="dsa-card-head"><div><h3>Recent activity</h3><p>Latest records across your business</p></div></div><div id="dsa-activity"></div></section></div>
              <footer class="dsa-footer">DSA Loan Portal \xB7 Live data from your Frappe site</footer></main></div>`;
        $("#dsa-range", this.root).addEventListener("change", (e) => {
          this.preset = e.target.value;
          this.refresh();
        });
        $("#dsa-company", this.root).value = this.company || "";
        $("#dsa-company", this.root).addEventListener("change", (e) => {
          this.company = e.target.value;
          this.refresh();
        });
        $("#dsa-refresh", this.root).addEventListener("click", () => this.refresh());
      }
      async refresh() {
        if (!this.ctx)
          return;
        $("#dsa-refresh", this.root).disabled = true;
        try {
          const data = await frappe.xcall(API + "get_overview", { preset: this.preset, company: this.company });
          this.data = data;
          this.render(data);
        } catch (e) {
          frappe.msgprint({ title: "Dashboard error", message: "Could not retrieve dashboard data. Check permissions and server logs." });
        } finally {
          $("#dsa-refresh", this.root).disabled = false;
        }
      }
      render(d) {
        const k = d.kpis, c = this.ctx.currency;
        $("#dsa-period", this.root).textContent = `Showing ${d.range.from_date} to ${d.range.to_date}`;
        const cards = [
          ["Customers", k.customers, "Registered customers", "user"],
          ["New customers", k.new_customers, "Created in selected period", "plus"],
          ["Loan applications", k.applications, "All applications", "file"],
          ["Applications in period", k.applications_period, "By application date", "calendar"],
          ["Awaiting action", k.pending_applications, "Draft, submitted or under review", "clock"],
          ["Approved or disbursed", k.approved_applications, "Parent application status", "check"],
          ["Active lenders", k.active_lenders, `${count(k.lenders)} total lenders`, "bank"],
          ["Active products", k.active_products, `${count(k.products)} total products`, "layers"],
          ["Disbursed amount", k.disbursed_amount == null ? null : money(k.disbursed_amount, c), "Processed disbursements", "wallet"],
          ["Commission pending", k.commission_pending == null ? null : money(k.commission_pending, c), "Pending, invoiced or partly paid", "percent"],
          ["Invoice outstanding", k.invoice_outstanding == null ? null : money(k.invoice_outstanding, c), "Submitted sales invoices", "receipt"],
          ["Payments received", k.payments_received == null ? null : money(k.payments_received, c), "Submitted receive entries", "arrow"]
        ];
        $("#dsa-kpis", this.root).innerHTML = cards.map((x, i) => `<div class="dsa-kpi"><div class="dsa-kpi-top"><span>${esc(x[0])}</span><i>${["\u25C9", "+", "\u25A4", "\u25F7", "\u25CC", "\u2713", "\u25A5", "\u25A6", "\u20B9", "%", "\u25A7", "\u2199"][i]}</i></div><strong>${x[1] == null ? "\u2014" : x[1]}</strong><small>${esc(x[2])}</small></div>`).join("");
        const destinations = [
          "DSA Customer",
          "DSA Customer",
          "Loan Application",
          "Loan Application",
          "Loan Application",
          "Loan Application",
          "Lender",
          "Lender Loan Product",
          "Lender Disbursement",
          "Lender Commission Record",
          "Sales Invoice",
          "Payment Entry"
        ];
        $("#dsa-kpis", this.root).querySelectorAll(".dsa-kpi").forEach((card, index) => {
          card.style.cursor = "pointer";
          card.setAttribute("role", "button");
          card.setAttribute("tabindex", "0");
          card.title = "Open " + destinations[index];
          const openList = () => frappe.set_route("List", destinations[index]);
          card.addEventListener("click", openList);
          card.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              openList();
            }
          });
        });
        this.renderBars("#dsa-status", d.application_status);
        this.renderBars("#dsa-loantypes", d.loan_types);
        this.renderBars("#dsa-lendertypes", d.lender_types);
        $("#dsa-lenders", this.root).innerHTML = (d.lenders || []).length ? `<div class="dsa-table-wrap"><table><thead><tr><th>Lender</th><th>Type</th><th>Status</th></tr></thead><tbody>${d.lenders.map((r) => `<tr><td><a href="${frappe.utils.get_form_link("Lender", r.name)}">${esc(r.lender_name || r.name)}</a></td><td>${esc(r.lender_type)}</td><td><span class="dsa-pill">${esc(r.lender_status)}</span></td></tr>`).join("")}</tbody></table></div>` : `<div class="dsa-empty">No lender records available.</div>`;
        const acts = d.activities || [];
        $("#dsa-activity", this.root).innerHTML = acts.length ? `<div class="dsa-table-wrap"><table><thead><tr><th>Record</th><th>Type</th><th>Reference</th><th>Date</th></tr></thead><tbody>${acts.map((r) => `<tr><td>${esc(r.customer_name || r.customer || r.lender || r.name)}</td><td>${esc(r.doctype)}</td><td>${esc(r.name)}</td><td>${esc(r.application_date || r.disbursement_date || r.posting_date || r.creation || "\u2014")}</td></tr>`).join("")}</tbody></table></div>` : `<div class="dsa-empty">No recent activity to display.</div>`;
      }
      renderBars(selector, rows) {
        const el = $(selector, this.root);
        if (rows === null) {
          el.innerHTML = '<div class="dsa-empty">You do not have permission to view this data.</div>';
          return;
        }
        if (!rows || !rows.length) {
          el.innerHTML = '<div class="dsa-empty">No records available yet.</div>';
          return;
        }
        const max = Math.max(1, ...rows.map((r) => Number(r.value) || 0));
        el.innerHTML = rows.map((r, i) => `<div class="dsa-bar-row"><div class="dsa-bar-label"><span>${esc(r.label)}</span><b>${frappe.format(r.value, { fieldtype: "Int" })}</b></div><div class="dsa-bar-track"><div class="dsa-bar-fill" style="width:${Math.max(0, Math.min(100, r.value / max * 100))}%;background:${palette[i % palette.length]}"></div></div></div>`).join("");
      }
    }
    frappe.provide("dsaLoanPortal");
    dsaLoanPortal.AdminDashboard = AdminDashboard;
  })();
})();
//# sourceMappingURL=dsa_admin_dashboard.bundle.SW7MBMY3.js.map
