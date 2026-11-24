// Entry point of the DSA Admin Dashboard. Fetches context once, then the overview on every filter change.
import { Shell } from "./dsa_admin_dashboard_v2/shell";
import { Overview } from "./dsa_admin_dashboard_v2/overview";
import { set_currency } from "./dsa_admin_dashboard_v2/util";

const API = "dsa_loan.dashboard_v2.api.";

class Dashboard {
	constructor(wrapper) {
		this.root = document.createElement("div");
		this.root.className = "dl-app";
		this.root.innerHTML = `
			<header class="dl-top"></header>
			<aside class="dl-side"></aside>
			<div class="dl-scrim"></div>
			<main class="dl-main"><div class="dl-boot"><span class="dl-spin"></span>${__("Loading dashboard…")}</div></main>`;
		$(wrapper).empty().append(this.root);
		this.init();
	}

	async init() {
		try {
			this.ctx = await frappe.xcall(API + "get_context");
		} catch (e) {
			this.root.querySelector(".dl-main").innerHTML = `<div class="dl-fatal">${__("The dashboard could not start. Check that you are allowed to open it, then reload.")}</div>`;
			return;
		}
		set_currency(this.ctx.currency);
		this.overview = new Overview(this.root.querySelector(".dl-main"), this.ctx, () => this.load());
		this.shell = new Shell(this.root, this.ctx, { scroll_to: (a) => this.overview.scroll_to(a) });
		await this.load();
	}

	async load() {
		const seq = (this.seq = (this.seq || 0) + 1);
		this.overview.set_loading(true);
		try {
			const resp = await frappe.xcall(API + "get_overview", this.overview.args());
			if (seq !== this.seq) return; // a newer request is in flight; drop this answer
			set_currency(resp.currency);
			this.overview.render(resp);
			this.shell.set_tasks(resp.data.tasks || []);
			this.loaded_at = Date.now();
		} catch (e) {
			if (seq !== this.seq) return;
			this.overview.set_error();
		}
	}

	on_show() {
		if (this.loaded_at && Date.now() - this.loaded_at > 60 * 1000) this.load();
		this.shell && this.shell.refresh_notification_badge();
	}
}

frappe.provide("dsa_loan.dashboard_v2");
dsa_loan.dashboard_v2.Dashboard = Dashboard;
