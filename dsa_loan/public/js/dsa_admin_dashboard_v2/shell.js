// Top bar and sidebar of the DSA Admin Dashboard.
import { icon, LOGO, esc, go, open_doc, store, initials, debounce, pill, when } from "./util";

const API = "dsa_loan.dashboard_v2.api.";

export class Shell {
	constructor(root, ctx, hooks) {
		this.root = root;
		this.ctx = ctx;
		this.hooks = hooks; // { scroll_to(anchor) }
		this.expanded = new Set(store("expanded") || ["overview", "loans"]);
		this.active = "top";
		this.render_top();
		this.render_side();
		this.bind_global();
		this.refresh_notification_badge();
		if (store("collapsed")) this.set_collapsed(true);
	}

	// ------------------------------------------------------------ top bar
	render_top() {
		const c = this.ctx;
		const avatar = c.image ? `<img src="${esc(c.image)}" alt="">` : initials(c.full_name);
		this.top = this.root.querySelector(".dl-top");
		const pop = (name, label, ic, extra = "") =>
			`<div class="dl-anchor ${extra}"><button class="dl-top-btn" data-toggle="${name}" title="${esc(label)}" aria-label="${esc(label)}">${icon(ic)}<span class="dl-badge" data-badge="${name}" hidden></span></button><div class="dl-pop" data-pop="${name}"></div></div>`;
		this.top.innerHTML = `
			<button class="dl-top-btn dl-burger" data-act="drawer" aria-label="${__("Menu")}">${icon("menu")}</button>
			<a class="dl-brand" href="/app/${esc(c.page)}" aria-label="DSA Loan Portal">
				<span class="dl-logo">${LOGO}</span>
				<span class="dl-brand-text"><b>DSA Loan Portal</b><small>${__("Admin console")}</small></span>
			</a>
			<div class="dl-search">
				<label class="dl-search-box">${icon("search")}
					<input type="search" placeholder="${__("Search customers, applications, lenders, products…")}" aria-label="${__("Search")}" autocomplete="off">
					<kbd>Ctrl K</kbd>
				</label>
				<div class="dl-pop dl-pop-wide" data-pop="search" role="listbox"></div>
			</div>
			<div class="dl-top-actions">
				<div class="dl-anchor"><button class="dl-quick" data-toggle="quick">${icon("plus")}<span>${__("Quick create")}</span></button><div class="dl-pop" data-pop="quick"></div></div>
				${pop("tasks", __("Pending tasks"), "tasks")}
				${pop("notif", __("Notifications"), "bell")}
				${pop("help", __("Help and support"), "help", "dl-hide-sm")}
				${pop("settings", __("Settings"), "settings", "dl-hide-sm")}
				<div class="dl-anchor"><button class="dl-user" data-toggle="user" aria-label="${__("Account")}"><span class="dl-avatar">${avatar}</span><span class="dl-user-name">${esc(c.full_name)}</span></button><div class="dl-pop" data-pop="user"></div></div>
			</div>`;
		this.fill_static_pops();
		const input = (this.search_input = this.top.querySelector(".dl-search input"));
		input.addEventListener("input", debounce(() => this.search(input.value), 220));
		input.addEventListener("focus", () => input.value.trim().length >= 2 && this.search(input.value));
		input.addEventListener("keydown", (e) => this.search_keys(e));
		this.top.addEventListener("click", (e) => {
			const t = e.target.closest("[data-toggle]");
			if (t) {
				e.stopPropagation();
				this.toggle(t.dataset.toggle);
				return;
			}
			const a = e.target.closest('[data-act="drawer"]');
			if (a) {
				e.stopPropagation();
				this.root.classList.toggle("dl-drawer");
			}
		});
	}

	pop(name) {
		return this.top.querySelector(`[data-pop="${name}"]`);
	}

	menu(name, title, items) {
		const el = this.pop(name);
		el.innerHTML = (title ? `<div class="dl-pop-head">${esc(title)}</div>` : "") + items.map((it, i) => `<button class="dl-pop-item" data-mi="${i}">${icon(it[0])}${esc(it[1])}</button>`).join("");
		el.addEventListener("click", (e) => {
			const b = e.target.closest("[data-mi]");
			if (b) {
				this.close_pops();
				items[b.dataset.mi][2]();
			}
		});
	}

	fill_static_pops() {
		const c = this.ctx;
		const q = this.pop("quick");
		q.innerHTML =
			`<div class="dl-pop-head">${__("Create new")}</div>` +
			(c.quick_actions.length
				? c.quick_actions.map((a, i) => `<button class="dl-pop-item" data-qa="${i}">${icon(a.icon)}${esc(__(a.label))}</button>`).join("")
				: `<div class="dl-pop-empty">${__("You cannot create records here")}</div>`);
		q.addEventListener("click", (e) => {
			const b = e.target.closest("[data-qa]");
			if (!b) return;
			this.close_pops();
			const a = c.quick_actions[b.dataset.qa];
			if (a.doctype) frappe.new_doc(a.doctype);
			else go({ route: a.route });
		});
		this.menu("help", __("Help & support"), [
			["keyboard", __("Keyboard shortcuts"), () => frappe.ui.keys && frappe.ui.keys.show_keyboard_shortcut_dialog && frappe.ui.keys.show_keyboard_shortcut_dialog()],
			["book", __("ERPNext documentation"), () => window.open("https://docs.erpnext.com", "_blank", "noopener")],
			["help", __("About"), () => frappe.ui.misc && frappe.ui.misc.about && frappe.ui.misc.about()],
		]);
		const st = [["user", __("My settings"), () => frappe.set_route("Form", "User", c.user)], ["moon", __("Switch theme"), () => new frappe.ui.ThemeSwitcher().show()]];
		if (c.is_system_manager) {
			st.push(["building", __("Companies"), () => frappe.set_route("List", "Company")]);
			st.push(["settings", __("System settings"), () => frappe.set_route("Form", "System Settings")]);
		}
		this.menu("settings", __("Settings"), st);
		this.menu("user", c.full_name, [
			["user", __("My profile"), () => frappe.set_route("Form", "User", c.user)],
			["grid", __("Desk home"), () => frappe.set_route("")],
			["logout", __("Log out"), () => frappe.app.logout()],
		]);
	}

	toggle(name) {
		const el = this.pop(name);
		const open = el.classList.contains("dl-open");
		this.close_pops();
		if (open) return;
		el.classList.add("dl-open");
		if (name === "notif") this.load_notifications();
		if (name === "tasks") this.draw_tasks();
	}

	close_pops() {
		this.top.querySelectorAll(".dl-pop.dl-open").forEach((p) => p.classList.remove("dl-open"));
	}

	// ------------------------------------------------------------ search
	async search(txt) {
		const el = this.pop("search");
		txt = (txt || "").trim();
		if (txt.length < 2) return el.classList.remove("dl-open");
		this.close_pops();
		el.classList.add("dl-open");
		el.innerHTML = `<div class="dl-pop-empty">${__("Searching…")}</div>`;
		const seq = (this.sseq = (this.sseq || 0) + 1);
		let rows = [];
		try {
			rows = await frappe.xcall(API + "search", { txt });
		} catch (e) {
			el.innerHTML = `<div class="dl-pop-empty">${__("Search failed")}</div>`;
			return;
		}
		if (seq !== this.sseq) return;
		this.results = rows;
		if (!rows.length) {
			el.innerHTML = `<div class="dl-pop-empty">${__("No matching records you can open")}</div>`;
			return;
		}
		let last = "";
		el.innerHTML = rows
			.map((r, i) => {
				const head = r.doctype !== last ? `<div class="dl-pop-head">${esc(__(r.doctype))}</div>` : "";
				last = r.doctype;
				return `${head}<button class="dl-pop-item dl-res" data-res="${i}"><span><b>${esc(r.title)}</b>${r.title !== r.name ? `<small>${esc(r.name)}</small>` : ""}</span>${r.sub ? `<em>${esc(r.sub)}</em>` : ""}</button>`;
			})
			.join("");
		this.sel = -1;
	}

	search_keys(e) {
		const items = [...this.pop("search").querySelectorAll("[data-res]")];
		if (e.key === "Escape") {
			this.close_pops();
			e.target.blur();
		} else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
			if (!items.length) return;
			e.preventDefault();
			this.sel = (this.sel + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
			items.forEach((b, i) => b.classList.toggle("dl-sel", i === this.sel));
			items[this.sel].scrollIntoView({ block: "nearest" });
		} else if (e.key === "Enter") {
			const r = this.results && this.results[items[this.sel] ? items[this.sel].dataset.res : 0];
			if (r) this.open_result(r);
		}
	}

	open_result(r) {
		this.close_pops();
		this.search_input.value = "";
		open_doc(r.doctype, r.name);
	}

	// ------------------------------------------------------------ notifications and tasks
	async load_notifications() {
		const el = this.pop("notif");
		el.innerHTML = `<div class="dl-pop-head">${__("Notifications")}</div><div class="dl-pop-empty">${__("Loading…")}</div>`;
		try {
			const n = await frappe.xcall(API + "get_notifications");
			this.badge("notif", n.unread);
			el.innerHTML =
				`<div class="dl-pop-head">${__("Notifications")}</div>` +
				(n.items.length
					? n.items
							.map((i) => `<button class="dl-pop-item dl-note ${i.read ? "" : "dl-unread"}" data-dt="${esc(i.document_type)}" data-dn="${esc(i.document_name)}"><span>${esc(i.subject)}<small>${esc(when(i.creation))}</small></span></button>`)
							.join("")
					: `<div class="dl-pop-empty">${__("You are all caught up")}</div>`);
			el.onclick = (e) => {
				const b = e.target.closest("[data-dt]");
				if (b && b.dataset.dt && b.dataset.dn) {
					this.close_pops();
					open_doc(b.dataset.dt, b.dataset.dn);
				}
			};
		} catch (e) {
			el.innerHTML = `<div class="dl-pop-empty">${__("Could not load notifications")}</div>`;
		}
	}

	async refresh_notification_badge() {
		try {
			const n = await frappe.xcall(API + "get_notifications");
			this.badge("notif", n.unread);
		} catch (e) {
			/* badge is optional */
		}
	}

	badge(name, n) {
		const b = this.top.querySelector(`[data-badge="${name}"]`);
		if (!b) return;
		b.textContent = n > 99 ? "99+" : n;
		b.hidden = !n;
	}

	set_tasks(tasks) {
		this.tasks = tasks || [];
		this.badge("tasks", this.tasks.length);
		const b = this.top.querySelector('[data-badge="tasks"]');
		if (b) b.classList.toggle("dl-hot", this.tasks.some((t) => t.priority === "High"));
	}

	draw_tasks() {
		const el = this.pop("tasks");
		const t = this.tasks || [];
		el.innerHTML =
			`<div class="dl-pop-head">${__("Pending tasks")}</div>` +
			(t.length
				? t.map((x, i) => `<button class="dl-pop-item" data-task="${i}"><i class="dl-dot dl-p-${x.priority.toLowerCase()}"></i><span>${esc(__(x.label))}</span><em>${x.count}</em></button>`).join("")
				: `<div class="dl-pop-empty">${__("Nothing needs attention")}</div>`);
		el.onclick = (e) => {
			const b = e.target.closest("[data-task]");
			if (b) {
				this.close_pops();
				go(t[b.dataset.task].route);
			}
		};
	}

	// ------------------------------------------------------------ sidebar
	render_side() {
		this.side = this.root.querySelector(".dl-side");
		this.side.innerHTML = `
			<div class="dl-side-head"><label class="dl-find">${icon("search")}<input type="search" placeholder="${__("Find a page…")}" aria-label="${__("Find a page")}"></label>
			<button class="dl-collapse" data-act="collapse" title="${__("Collapse sidebar")}" aria-label="${__("Collapse sidebar")}">${icon("panel")}</button></div>
			<nav class="dl-nav"></nav>`;
		this.nav = this.side.querySelector(".dl-nav");
		this.find = this.side.querySelector(".dl-find input");
		this.find.addEventListener("input", debounce(() => this.draw_nav(), 120));
		this.draw_nav();
		this.side.addEventListener("click", (e) => {
			if (e.target.closest('[data-act="collapse"]')) return this.set_collapsed(!this.root.classList.contains("dl-collapsed"));
			const g = e.target.closest("[data-group]");
			if (g) {
				if (this.root.classList.contains("dl-collapsed")) this.set_collapsed(false);
				const k = g.dataset.group;
				this.expanded.has(k) ? this.expanded.delete(k) : this.expanded.add(k);
				store("expanded", [...this.expanded]);
				return this.draw_nav();
			}
			const it = e.target.closest("[data-item]");
			if (!it) return;
			const [gi, ii] = it.dataset.item.split(":").map(Number);
			const item = this.ctx.sidebar[gi].items[ii];
			this.root.classList.remove("dl-drawer");
			if (item.anchor) {
				this.active = item.anchor;
				this.draw_nav();
				this.hooks.scroll_to(item.anchor);
			} else go(item);
		});
	}

	draw_nav() {
		const q = (this.find ? this.find.value : "").trim().toLowerCase();
		this.nav.innerHTML = this.ctx.sidebar
			.map((g, gi) => {
				const items = g.items.map((it, ii) => ({ it, ii })).filter(({ it }) => !q || it.label.toLowerCase().includes(q) || g.label.toLowerCase().includes(q));
				if (!items.length) return "";
				const open = q || this.expanded.has(g.key);
				return `<div class="dl-group ${open ? "dl-open" : ""}">
					<button class="dl-group-btn" data-group="${esc(g.key)}" title="${esc(__(g.label))}">${icon(g.icon)}<span>${esc(__(g.label))}</span>${icon("chevron", "dl-chev")}</button>
					<div class="dl-group-items">${items
						.map(({ it, ii }) => `<button class="dl-item ${it.anchor && it.anchor === this.active ? "dl-on" : ""}" data-item="${gi}:${ii}">${esc(__(it.label))}</button>`)
						.join("")}</div></div>`;
			})
			.join("");
		if (!this.nav.innerHTML) this.nav.innerHTML = `<div class="dl-pop-empty">${__("No pages match")}</div>`;
	}

	set_collapsed(on) {
		this.root.classList.toggle("dl-collapsed", !!on);
		store("collapsed", !!on);
	}

	// ------------------------------------------------------------ global listeners
	bind_global() {
		this.root.querySelector(".dl-scrim").addEventListener("click", () => this.root.classList.remove("dl-drawer"));
		this.top.querySelector(".dl-pop[data-pop=search]").addEventListener("click", (e) => {
			const b = e.target.closest("[data-res]");
			if (b) this.open_result(this.results[b.dataset.res]);
		});
		// capture clicks anywhere outside an open popover
		this.on_doc_click = (e) => {
			if (!this.root.isConnected) return document.removeEventListener("click", this.on_doc_click);
			if (!e.target.closest(".dl-anchor, .dl-search")) this.close_pops();
		};
		document.addEventListener("click", this.on_doc_click);
		this.on_key = (e) => {
			if (!this.root.isConnected) return document.removeEventListener("keydown", this.on_key);
			if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k" && document.body.classList.contains("dl-active")) {
				e.preventDefault();
				this.search_input.focus();
				this.search_input.select();
			} else if (e.key === "Escape") this.close_pops();
		};
		document.addEventListener("keydown", this.on_key);
	}
}
