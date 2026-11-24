// Lender-focused Overview for the existing DSA Admin Dashboard V2 shell.
import { icon, esc, go, open_doc, store, fmt, money, money_full, num, pill, empty, unavailable, allzero } from "./util";

const PRESET_SHORT = { today: "Today", this_week: "Week", this_month: "Month", last_month: "Last month", this_quarter: "Quarter", this_year: "Year", custom: "Custom" };
const KPI_ICONS = { lenders: "landmark", active_lenders: "check-circle", applications: "file-text", approved: "badge-check", rejected: "x-circle", disbursed: "wallet", commission: "percent", queries: "message-circle" };
const dstr = (value) => value ? new Date(`${value}T00:00:00`).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "—";

export class Overview {
    constructor(main, ctx, on_change) {
        this.main = main;
        this.ctx = ctx;
        this.on_change = on_change;
        this.tab = "amount";
        const saved = store("lender-dashboard-range") || {};
        const validPreset = (ctx.presets || []).some((item) => item.value === saved.preset);
        this.state = {
            preset: validPreset ? saved.preset : (ctx.default_preset || "this_month"),
            from: saved.from || "",
            to: saved.to || "",
            lender: (ctx.lenders || []).some((item) => item.value === saved.lender) ? saved.lender : (ctx.default_lender || ""),
        };
        if (this.state.preset === "custom" && !(this.state.from && this.state.to)) this.state.preset = ctx.default_preset || "this_month";
        this.render_frame();
        this.main.addEventListener("click", (event) => this.on_click(event));
        this.main.addEventListener("change", (event) => this.on_input(event));
    }

    args() {
        const args = { preset: this.state.preset, lender: this.state.lender };
        if (this.state.preset === "custom") {
            args.from_date = this.state.from;
            args.to_date = this.state.to;
        }
        return args;
    }

    persist() {
        store("lender-dashboard-range", { ...this.state });
    }

    render_frame() {
        const today = new Date();
        const dateLabel = today.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
        const presets = (this.ctx.presets || []).map((item) => `<button class="${item.value === this.state.preset ? "dl-on" : ""}" data-preset="${esc(item.value)}">${esc(__(PRESET_SHORT[item.value] || item.label))}</button>`).join("");
        const lenders = (this.ctx.lenders || []).map((item) => `<option value="${esc(item.value)}" ${item.value === this.state.lender ? "selected" : ""}>${esc(item.label)}</option>`).join("");
        const quick = (this.ctx.quick_actions || []).slice(0, 5).map((item, index) => `<button class="dl-chip" data-qa="${index}">${icon(item.icon || "plus")}${esc(__(item.label))}</button>`).join("");
        this.main.innerHTML = `
            <div class="dl-wrap">
                <section class="dl-head" data-anchor="top">
                    <div><div class="dl-eyebrow">${esc(dateLabel)}</div><h1>${__("Lender Operations Overview")}</h1><p>${__("Monitor lender relationships, applications, queries and disbursements.")}</p></div>
                    <div class="dl-controls">
                        <label class="dl-select" title="${__("Filter by lender")}">${icon("landmark")}<select data-lender>${lenders}</select></label>
                        <div class="dl-seg" role="group" aria-label="${__("Date range")}">${presets}</div>
                        <div class="dl-custom" hidden><input type="date" data-from value="${esc(this.state.from)}" aria-label="${__("From date")}"><span>→</span><input type="date" data-to value="${esc(this.state.to)}" aria-label="${__("To date")}"><button class="dl-btn" data-apply>${__("Apply")}</button></div>
                        <button class="dl-icon-btn" data-reset title="${__("Reset filters")}" aria-label="${__("Reset filters")}">${icon("x")}</button>
                        <button class="dl-icon-btn" data-refresh title="${__("Refresh")}" aria-label="${__("Refresh")}">${icon("refresh")}</button>
                    </div>
                </section>
                <div class="dl-range-line" data-range></div>
                <div class="dl-alert" data-error hidden></div>
                <div class="dl-quick-row" data-quickrow><span class="dl-quick-label">${__("Quick actions")}</span>${quick}</div>
                <section class="dl-hero" data-sec="kpis">${this.skeleton(8)}</section>
                <div class="dl-grid dl-g-pipe" data-anchor="pipeline">
                    <section class="dl-card"><header><h2>${__("Application Pipeline")}</h2></header><div data-sec="pipeline">${this.skeleton(1, "dl-sk-lg")}</div></section>
                    <section class="dl-card"><header><h2>${__("Needs Attention")}</h2></header><div data-sec="tasks">${this.skeleton(1, "dl-sk-lg")}</div></section>
                </div>
                <div class="dl-grid dl-g-2" data-anchor="trends">
                    ${this.card("trend_apps", __("Applications vs Sanctioned"), __("Last 6 months"))}
                    ${this.card("trend_disb", __("Disbursed Amount"), __("Last 6 months, confirmed"))}
                </div>
                <div class="dl-grid dl-g-2">
                    ${this.card("trend_comm", __("Commission Calculated vs Paid"), __("Last 6 months, gross"))}
                    ${this.card("comm_status", __("Commission by Status"), __("Selected range"))}
                </div>
                <div class="dl-grid dl-g-2">
                    ${this.card("by_lender", __("Disbursed by Lender"), __("Selected range"))}
                    ${this.card("loan_types", __("Applications by Loan Type"), __("Selected range"))}
                </div>
                <div class="dl-grid dl-g-2">
                    ${this.card("branches", __("Branch Performance"), __("Applications and disbursed amount"))}
                    ${this.card("documents", __("Document Verification"), __("Documents of applications in range"))}
                </div>
                <section class="dl-card" data-anchor="lenders"><header><h2>${__("Lender Performance")}</h2><span class="dl-sub" data-sub="lenders"></span></header><div data-sec="lenders">${this.skeleton(1, "dl-sk-lg")}</div></section>
                <div class="dl-grid dl-g-2" data-anchor="money">
                    <section class="dl-card"><header><h2>${__("Disbursements")}</h2><span class="dl-sub">${__("Confirmed records")}</span></header><div data-sec="disbursements">${this.skeleton(1, "dl-sk-lg")}</div></section>
                    <section class="dl-card"><header><h2>${__("Commissions")}</h2><span class="dl-sub">${__("Pending invoice status")}</span></header><div data-sec="commissions">${this.skeleton(1, "dl-sk-lg")}</div></section>
                </div>
                <footer class="dl-foot" data-foot>${__("Read-only overview. Operational updates are available on the dedicated pages.")}</footer>
                <div class="dl-modal-host" data-modal-host></div>
            </div>`;
        this.sync_custom();
    }

    skeleton(count, cls = "") { return Array.from({ length: count }, () => `<div class="dl-sk ${cls}"></div>`).join(""); }
    sec(name) { return this.main.querySelector(`[data-sec="${name}"]`); }
    set_loading(on) { this.main.classList.toggle("dl-loading", !!on); if (on) this.main.querySelector("[data-error]").hidden = true; }
    set_error() { this.set_loading(false); const el = this.main.querySelector("[data-error]"); el.hidden = false; el.innerHTML = `${icon("alert-circle")}<span>${__("Could not load dashboard data.")}</span><button class="dl-btn" data-refresh>${__("Retry")}</button>`; }
    sync_custom() {
        const custom = this.main.querySelector(".dl-custom");
        if (custom) custom.hidden = this.state.preset !== "custom";
        this.main.querySelectorAll("[data-preset]").forEach((button) => button.classList.toggle("dl-on", button.dataset.preset === this.state.preset));
    }

    on_click(event) {
        const target = event.target.closest("button, [data-route], [data-open]");
        if (!target || !this.main.contains(target)) return;
        if (target.dataset.preset) {
            this.state.preset = target.dataset.preset;
            this.sync_custom();
            if (this.state.preset !== "custom") { this.persist(); this.on_change(); }
            return;
        }
        if (target.hasAttribute("data-apply")) {
            const from = this.main.querySelector("[data-from]").value;
            const to = this.main.querySelector("[data-to]").value;
            if (!from || !to) return frappe.show_alert({ message: __("Choose both dates."), indicator: "orange" });
            if (from > to) return frappe.show_alert({ message: __("From date must be on or before To date."), indicator: "red" });
            this.state.from = from; this.state.to = to; this.persist(); return this.on_change();
        }
        if (target.hasAttribute("data-reset")) {
            this.state = { preset: this.ctx.default_preset || "this_month", from: "", to: "", lender: "" };
            const select = this.main.querySelector("[data-lender]"); if (select) select.value = "";
            this.sync_custom(); this.persist(); return this.on_change();
        }
        if (target.hasAttribute("data-refresh")) return this.on_change();
        if (target.dataset.qa !== undefined) {
            const action = (this.ctx.quick_actions || [])[Number(target.dataset.qa)];
            if (action && action.doctype) return frappe.new_doc(action.doctype);
        }
        if (target.dataset.kpi !== undefined) return this.show_kpi(Number(target.dataset.kpi));
        if (target.hasAttribute("data-modal-close")) { this.main.querySelector("[data-modal-host]").innerHTML = ""; return; }
        if (target.hasAttribute("data-modal-open")) {
            const spec = this.modalRoute;
            if (spec) go(spec);
            this.main.querySelector("[data-modal-host]").innerHTML = "";
            return;
        }
        if (target.dataset.route) {
            try { return go(JSON.parse(target.dataset.route)); } catch (error) { console.error(error); }
        }
        if (target.dataset.open && target.dataset.name) return open_doc(target.dataset.open, target.dataset.name);
    }

    on_input(event) {
        if (event.target.matches("[data-lender]")) {
            this.state.lender = event.target.value;
            this.persist();
            this.on_change();
        }
    }

    route_attr(route) { return route ? `data-route='${esc(JSON.stringify(route))}'` : "disabled"; }

    show_kpi(index) {
        const item = (this.d?.kpis || [])[index];
        if (!item) return;
        this.modalRoute = item.route;
        const value = item.format === "Currency" ? money(item.value) : num(item.value);
        this.main.querySelector("[data-modal-host]").innerHTML = `<div class="dl-modal-backdrop" data-modal-close><section class="dl-card dl-modal" role="dialog" aria-modal="true" aria-label="${esc(__(item.label))}"><header><h2>${esc(__(item.label))}</h2><button class="dl-icon-btn" data-modal-close aria-label="${__("Close")}">${icon("x")}</button></header><div class="dl-modal-value">${esc(value)}</div><p>${esc(__(item.preview || "Live records matching the current filters."))}</p><div class="dl-modal-actions"><button class="dl-btn" data-modal-close>${__("Close")}</button><button class="dl-btn dl-btn-primary" data-modal-open>${__("View records")}</button></div></section></div>`;
    }

    render(response) {
        this.resp = response;
        this.d = response.data || {};
        this.set_loading(false);
        this.main.querySelector("[data-range]").innerHTML = `${icon("calendar")}<span>${dstr(response.from_date)} – ${dstr(response.to_date)}</span><i></i><span>${esc(response.lender || __("All Lenders"))}</span>`;
        this.render_kpis(this.d.kpis || []);
        this.render_pipeline(this.d.pipeline || []);
        this.render_tasks(this.d.tasks || []);
        this.render_lenders(this.d.lenders || []);
        this.render_disbursements(this.d.disbursements || {});
        this.render_commissions(this.d.commissions || {});
        this.render_charts(this.d.charts || {});
    }

    card(key, title, sub) {
        return `<section class="dl-card"><header><h2>${esc(title)}</h2><span class="dl-sub">${esc(sub)}</span></header><div data-sec="${key}">${this.skeleton(1, "dl-sk-lg")}</div></section>`;
    }

    // Column chart via frappe.Chart (hover tooltips built in). Series colours: teal / amber (checked for colour-blind separation).
    column(key, trend, series, money_values) {
        const el = this.sec(key);
        if (!trend || allzero(series.map((s) => s.values))) return el.innerHTML = empty(__("No records in the last 6 months."), "chart");
        el.innerHTML = `<div class="dl-chart-host"></div>`;
        try {
            new frappe.Chart(el.firstChild, {
                type: "bar", height: 230, animate: 0,
                colors: ["#0D9488", "#D97706"].slice(0, series.length),
                data: { labels: trend.labels, datasets: series },
                barOptions: { spaceRatio: 0.45 },
                axisOptions: { xIsSeries: 1, shortenYAxisNumbers: 1 },
                tooltipOptions: { formatTooltipY: (v) => money_values ? money_full(v) : num(v) },
            });
        } catch (error) {
            el.innerHTML = empty(__("The chart could not be drawn."), "alert-circle");
        }
    }

    // Horizontal bar list: label, bar scaled to the largest value, value on the right; each row opens its records.
    barlist(key, rows, value, side, none) {
        const el = this.sec(key);
        if (!rows || !rows.length) return el.innerHTML = empty(none, "inbox");
        const max = Math.max(1, ...rows.map(value));
        el.innerHTML = `<ul class="dl-bars">${rows.map((row) => {
            const v = value(row);
            return `<li><button ${this.route_attr(row.route)} title="${esc(row.label)}: ${esc(side(row, true))}"><span class="dl-bar-l">${esc(__(row.label))}<small>${esc(side(row, false))}</small></span><span class="dl-bar"><span style="width:${v ? Math.max(3, Math.round(v / max * 100)) : 0}%;background:#0D9488"></span></span><b>${esc(side(row, true))}</b></button></li>`;
        }).join("")}</ul>`;
    }

    render_charts(c) {
        const t = c.trend;
        this.column("trend_apps", t, t ? [{ name: __("Applications"), values: t.applications }, { name: __("Sanctioned"), values: t.sanctioned }] : [], false);
        this.column("trend_disb", t, t ? [{ name: __("Disbursed"), values: t.disbursed }] : [], true);
        this.column("trend_comm", t, t ? [{ name: __("Calculated"), values: t.commission_earned }, { name: __("Paid"), values: t.commission_paid }] : [], true);
        const plural = (n, one, many) => `${num(n)} ${n === 1 ? one : many}`;
        this.barlist("comm_status", c.commission_status, (r) => r.amount,
            (r, main) => main ? money(r.amount) : plural(r.count, __("record"), __("records")), __("No commission in this range."));
        this.barlist("by_lender", c.by_lender, (r) => r.amount,
            (r, main) => main ? money(r.amount) : plural(r.count, __("application"), __("applications")), __("Nothing disbursed in this range."));
        this.barlist("loan_types", c.loan_types, (r) => r.count,
            (r, main) => main ? num(r.count) : `${money(r.amount)} ${__("requested")}`, __("No applications in this range."));
        this.barlist("branches", c.branches, (r) => r.amount || r.count,
            (r, main) => main ? money(r.amount) : plural(r.count, __("application"), __("applications")), __("No branch activity in this range."));
        this.barlist("documents", c.documents, (r) => r.count,
            (r, main) => main ? num(r.count) : "", __("No documents for applications in this range."));
    }

    render_kpis(items) {
        const el = this.sec("kpis");
        el.innerHTML = items.map((item, index) => `<button class="dl-hero-cell" data-kpi="${index}"><div class="dl-hero-top"><span class="dl-ico">${icon(KPI_ICONS[item.key] || "chart")}</span><span class="dl-hero-label">${esc(__(item.label))}</span></div><div class="dl-hero-value">${esc(item.format === "Currency" ? money(item.value) : num(item.value))}</div><div class="dl-hero-meta">${__("Click for details")}</div></button>`).join("");
    }

    render_pipeline(stages) {
        const el = this.sec("pipeline");
        if (!stages.length) return el.innerHTML = empty(__("No application stages found."));
        const max = Math.max(1, ...stages.map((item) => item.count || 0));
        el.innerHTML = `<ul class="dl-bars">${stages.map((item) => `<li><button ${this.route_attr(item.route)}><span class="dl-bar-l">${esc(__(item.label))}</span><span class="dl-bar"><span style="width:${Math.round((item.count || 0) / max * 100)}%;background:#0D9488"></span></span><b>${num(item.count)}</b></button></li>`).join("")}</ul>`;
    }

    render_tasks(tasks) {
        const el = this.sec("tasks");
        if (!tasks.length) return el.innerHTML = empty(__("Nothing needs attention right now."), "check-circle");
        el.innerHTML = `<ul class="dl-tasks">${tasks.map((item) => `<li><button ${this.route_attr(item.route)}><i class="dl-dot dl-p-${String(item.priority || "Medium").toLowerCase()}"></i><span class="dl-task-l">${esc(__(item.label))}<small>${esc(__(item.priority || "Medium"))}</small></span><b>${num(item.count)}</b></button></li>`).join("")}</ul>`;
    }

    render_lenders(rows) {
        const el = this.sec("lenders");
        this.main.querySelector('[data-sub="lenders"]').textContent = `${rows.length} ${__("lenders")}`;
        if (!rows.length) return el.innerHTML = empty(__("No lender records found."), "landmark");
        el.innerHTML = `<div class="dl-table-wrap"><table class="dl-table"><thead><tr><th>${__("Lender")}</th><th>${__("Status")}</th><th>${__("Type")}</th><th class="r">${__("Applications")}</th><th class="r">${__("Approved")}</th><th class="r">${__("Disbursed")}</th><th class="r">${__("Pending Commission")}</th></tr></thead><tbody>${rows.map((row) => `<tr><td><button class="dl-link dl-strong" data-open="Lender" data-name="${esc(row.lender)}">${esc(row.lender_name)}</button></td><td>${row.status ? pill(row.status) : "—"}</td><td>${esc(row.lender_type || "—")}</td><td class="r">${num(row.applications)}</td><td class="r">${num(row.approved)}</td><td class="r">${money(row.disbursed)}</td><td class="r">${money(row.commission)}</td></tr>`).join("")}</tbody></table></div>`;
    }

    render_disbursements(data) {
        const el = this.sec("disbursements");
        el.innerHTML = `<div class="dl-statline"><div><b>${money(data.amount || 0)}</b><span>${__("Confirmed amount")}</span></div><div><b>${num(data.count || 0)}</b><span>${__("Confirmed records")}</span></div><div><b>${money(data.average || 0)}</b><span>${__("Average disbursement")}</span></div></div><button class="dl-link" data-route='${esc(JSON.stringify({ doctype: "Loan Disbursement", filters: { disbursement_status: "Confirmed" } }))}'>${__("View disbursements")}</button>`;
    }

    render_commissions(data) {
        const el = this.sec("commissions");
        el.innerHTML = `<div class="dl-statline"><div><b>${money(data.pending_amount || 0)}</b><span>${__("Not yet paid")}</span></div><div><b>${num(data.pending_count || 0)}</b><span>${__("Open records")}</span></div></div><p class="dl-note">${__("Calculated, approved, invoiced or partly paid commission (gross).")}</p><button class="dl-link" data-route='${esc(JSON.stringify({ doctype: "Commission Calculation", filters: { calculation_status: ["in", ["Calculated", "Approved", "Invoiced", "Partially Paid"]] } }))}'>${__("View commission records")}</button>`;
    }
}
