(() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropSymbols = Object.getOwnPropertySymbols;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __propIsEnum = Object.prototype.propertyIsEnumerable;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __spreadValues = (a, b) => {
    for (var prop in b || (b = {}))
      if (__hasOwnProp.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    if (__getOwnPropSymbols)
      for (var prop of __getOwnPropSymbols(b)) {
        if (__propIsEnum.call(b, prop))
          __defNormalProp(a, prop, b[prop]);
      }
    return a;
  };

  // ../dsa_loan/dsa_loan/public/js/dsa_admin_dashboard_v2/util.js
  var P = {
    grid: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9"/><path d="M16 3.1a4 4 0 0 1 0 7.8"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>',
    "user-plus": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6M22 11h-6"/>',
    bank: '<path d="M3 21h18"/><path d="M5 21V10M10 21V10M14 21V10M19 21V10"/><path d="M12 3 21 8H3z"/>',
    file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    "file-plus": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M12 12v6M9 15h6"/>',
    send: '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
    wallet: '<path d="M20 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    percent: '<path d="M19 5 5 19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    mail: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    chart: '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/>',
    settings: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    bell: '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a2 2 0 0 0 3.4 0"/>',
    tasks: '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
    help: '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',
    chevron: '<path d="m6 9 6 6 6-6"/>',
    menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
    panel: '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 3v18"/>',
    box: '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
    receipt: '<path d="M4 2v20l3-2 3 2 2-2 2 2 3-2 3 2V2l-3 2-3-2-2 2-2-2-3 2z"/><path d="M8 9h8M8 13h6"/>',
    rupee: '<path d="M6 3h12M6 8h12M6 13l8.5 8M6 13h3a5 5 0 0 0 0-10"/>',
    logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5M21 12H9"/>',
    refresh: '<path d="M21 12a9 9 0 1 1-2.6-6.4L21 8"/><path d="M21 3v5h-5"/>',
    calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    alert: '<path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>',
    clock: '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
    keyboard: '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M7 14h10"/>',
    inbox: '<path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5.1 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.5-6.9A2 2 0 0 0 16.8 4H7.2a2 2 0 0 0-1.7 1.1z"/>',
    lock: '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    trend: '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
    building: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>'
  };
  function icon(name, cls = "") {
    return `<svg class="dl-i ${cls}" viewBox="0 0 24 24" aria-hidden="true">${P[name] || P.grid}</svg>`;
  }
  var LOGO = `<svg viewBox="0 0 32 32" aria-hidden="true">
	<defs><linearGradient id="dl-lg" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#0F766E"/><stop offset="1" stop-color="#6FD3B4"/></linearGradient></defs>
	<circle cx="16" cy="16" r="14" fill="#E3F3EC"/>
	<path d="M6.5 21.5c4-.5 6.5-3.2 8-7 1.2-3 3.4-5 7.5-5.5" fill="none" stroke="url(#dl-lg)" stroke-width="3.2" stroke-linecap="round"/>
	<circle cx="22.8" cy="9.2" r="2.6" fill="#123C3A"/>
</svg>`;
  var esc = (v) => frappe.utils.escape_html(v == null ? "" : String(v));
  var currency = "INR";
  function set_currency(c) {
    currency = c || "INR";
  }
  var trim = (x) => x.toFixed(2).replace(/\.?0+$/, "");
  var SYM = { INR: "\u20B9", USD: "$", EUR: "\u20AC", GBP: "\xA3" };
  function money(v, compact = true) {
    if (v == null)
      return "\u2014";
    const n = Number(v) || 0;
    const sym = SYM[currency] || currency + " ";
    const a = Math.abs(n);
    const sign = n < 0 ? "-" : "";
    if (compact && currency === "INR") {
      if (a >= 1e7)
        return `${sign}${sym}${trim(a / 1e7)} Cr`;
      if (a >= 1e5)
        return `${sign}${sym}${trim(a / 1e5)} L`;
    }
    if (compact && currency !== "INR" && a >= 1e6)
      return `${sign}${sym}${trim(a / 1e6)}M`;
    return `${sign}${sym}${a.toLocaleString(currency === "INR" ? "en-IN" : void 0, { maximumFractionDigits: 0 })}`;
  }
  function money_full(v) {
    if (v == null)
      return "\u2014";
    const n = Number(v) || 0;
    return `${SYM[currency] || currency + " "}${n.toLocaleString(currency === "INR" ? "en-IN" : void 0, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
  function num(v) {
    if (v == null)
      return "\u2014";
    return (Number(v) || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 });
  }
  function clone(o) {
    return o ? JSON.parse(JSON.stringify(o)) : o;
  }
  function go(spec) {
    if (!spec)
      return;
    if (spec.doctype && !spec.route) {
      frappe.route_options = clone(spec.filters || {});
      frappe.set_route("List", spec.doctype);
      return;
    }
    if (spec.filters)
      frappe.route_options = clone(spec.filters);
    frappe.set_route(...spec.route);
  }
  var open_doc = (doctype, name) => frappe.set_route("Form", doctype, name);
  function pill(status) {
    if (!status)
      return "";
    const s = String(status);
    let c = "dl-info";
    if (/^(Disbursed|Paid|Processed|Approved|Sanctioned|Active|Completed|Receive)$/.test(s))
      c = "dl-ok";
    else if (/(Reject|Cancel|Fail|Overdue|Suspend|Terminat|Withdraw)/.test(s))
      c = "dl-bad";
    else if (/(Pending|Draft|Unpaid|Partial|Invoiced|Required|On Hold|Inactive|Expired|Review|Submitted)/.test(s))
      c = "dl-warn";
    return `<span class="dl-pill ${c}">${esc(__(s))}</span>`;
  }
  function store(key, value) {
    try {
      if (value === void 0)
        return JSON.parse(localStorage.getItem("dsa_dash_" + key));
      localStorage.setItem("dsa_dash_" + key, JSON.stringify(value));
    } catch (e) {
      return null;
    }
  }
  function initials(name) {
    const parts = String(name || "?").trim().split(/\s+/);
    return (esc(((parts[0] || "")[0] || "") + ((parts[1] || "")[0] || "")) || "?").toUpperCase();
  }
  function debounce(fn, ms) {
    let t;
    return (...a) => {
      clearTimeout(t);
      t = setTimeout(() => fn(...a), ms);
    };
  }
  var empty = (msg, ic = "inbox") => `<div class="dl-empty">${icon(ic)}<span>${esc(msg)}</span></div>`;
  var allzero = (arrs) => arrs.every((a) => (a || []).every((v) => !v));
  function when(ts) {
    if (!ts)
      return "";
    try {
      return frappe.datetime.prettyDate(ts, true);
    } catch (e) {
      return String(ts);
    }
  }

  // ../dsa_loan/dsa_loan/public/js/dsa_admin_dashboard_v2/shell.js
  var API = "dsa_loan.dashboard_v2.api.";
  var Shell = class {
    constructor(root, ctx, hooks) {
      this.root = root;
      this.ctx = ctx;
      this.hooks = hooks;
      this.expanded = new Set(store("expanded") || ["overview", "loans"]);
      this.active = "top";
      this.render_top();
      this.render_side();
      this.bind_global();
      this.refresh_notification_badge();
      if (store("collapsed"))
        this.set_collapsed(true);
    }
    render_top() {
      const c = this.ctx;
      const avatar = c.image ? `<img src="${esc(c.image)}" alt="">` : initials(c.full_name);
      this.top = this.root.querySelector(".dl-top");
      const pop = (name, label, ic, extra = "") => `<div class="dl-anchor ${extra}"><button class="dl-top-btn" data-toggle="${name}" title="${esc(label)}" aria-label="${esc(label)}">${icon(ic)}<span class="dl-badge" data-badge="${name}" hidden></span></button><div class="dl-pop" data-pop="${name}"></div></div>`;
      this.top.innerHTML = `
			<button class="dl-top-btn dl-burger" data-act="drawer" aria-label="${__("Menu")}">${icon("menu")}</button>
			<a class="dl-brand" href="/app/${esc(c.page)}" aria-label="DSA Loan Portal">
				<span class="dl-logo">${LOGO}</span>
				<span class="dl-brand-text"><b>DSA Loan Portal</b><small>${__("Admin console")}</small></span>
			</a>
			<div class="dl-search">
				<label class="dl-search-box">${icon("search")}
					<input type="search" placeholder="${__("Search customers, applications, lenders, products\u2026")}" aria-label="${__("Search")}" autocomplete="off">
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
      const input = this.search_input = this.top.querySelector(".dl-search input");
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
      q.innerHTML = `<div class="dl-pop-head">${__("Create new")}</div>` + (c.quick_actions.length ? c.quick_actions.map((a, i) => `<button class="dl-pop-item" data-qa="${i}">${icon(a.icon)}${esc(__(a.label))}</button>`).join("") : `<div class="dl-pop-empty">${__("You cannot create records here")}</div>`);
      q.addEventListener("click", (e) => {
        const b = e.target.closest("[data-qa]");
        if (!b)
          return;
        this.close_pops();
        const a = c.quick_actions[b.dataset.qa];
        if (a.doctype)
          frappe.new_doc(a.doctype);
        else
          go({ route: a.route });
      });
      this.menu("help", __("Help & support"), [
        ["keyboard", __("Keyboard shortcuts"), () => frappe.ui.keys && frappe.ui.keys.show_keyboard_shortcut_dialog && frappe.ui.keys.show_keyboard_shortcut_dialog()],
        ["book", __("ERPNext documentation"), () => window.open("https://docs.erpnext.com", "_blank", "noopener")],
        ["help", __("About"), () => frappe.ui.misc && frappe.ui.misc.about && frappe.ui.misc.about()]
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
        ["logout", __("Log out"), () => frappe.app.logout()]
      ]);
    }
    toggle(name) {
      const el = this.pop(name);
      const open = el.classList.contains("dl-open");
      this.close_pops();
      if (open)
        return;
      el.classList.add("dl-open");
      if (name === "notif")
        this.load_notifications();
      if (name === "tasks")
        this.draw_tasks();
    }
    close_pops() {
      this.top.querySelectorAll(".dl-pop.dl-open").forEach((p) => p.classList.remove("dl-open"));
    }
    async search(txt) {
      const el = this.pop("search");
      txt = (txt || "").trim();
      if (txt.length < 2)
        return el.classList.remove("dl-open");
      this.close_pops();
      el.classList.add("dl-open");
      el.innerHTML = `<div class="dl-pop-empty">${__("Searching\u2026")}</div>`;
      const seq = this.sseq = (this.sseq || 0) + 1;
      let rows = [];
      try {
        rows = await frappe.xcall(API + "search", { txt });
      } catch (e) {
        el.innerHTML = `<div class="dl-pop-empty">${__("Search failed")}</div>`;
        return;
      }
      if (seq !== this.sseq)
        return;
      this.results = rows;
      if (!rows.length) {
        el.innerHTML = `<div class="dl-pop-empty">${__("No matching records you can open")}</div>`;
        return;
      }
      let last = "";
      el.innerHTML = rows.map((r, i) => {
        const head = r.doctype !== last ? `<div class="dl-pop-head">${esc(__(r.doctype))}</div>` : "";
        last = r.doctype;
        return `${head}<button class="dl-pop-item dl-res" data-res="${i}"><span><b>${esc(r.title)}</b>${r.title !== r.name ? `<small>${esc(r.name)}</small>` : ""}</span>${r.sub ? `<em>${esc(r.sub)}</em>` : ""}</button>`;
      }).join("");
      this.sel = -1;
    }
    search_keys(e) {
      const items = [...this.pop("search").querySelectorAll("[data-res]")];
      if (e.key === "Escape") {
        this.close_pops();
        e.target.blur();
      } else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        if (!items.length)
          return;
        e.preventDefault();
        this.sel = (this.sel + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items.forEach((b, i) => b.classList.toggle("dl-sel", i === this.sel));
        items[this.sel].scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter") {
        const r = this.results && this.results[items[this.sel] ? items[this.sel].dataset.res : 0];
        if (r)
          this.open_result(r);
      }
    }
    open_result(r) {
      this.close_pops();
      this.search_input.value = "";
      open_doc(r.doctype, r.name);
    }
    async load_notifications() {
      const el = this.pop("notif");
      el.innerHTML = `<div class="dl-pop-head">${__("Notifications")}</div><div class="dl-pop-empty">${__("Loading\u2026")}</div>`;
      try {
        const n = await frappe.xcall(API + "get_notifications");
        this.badge("notif", n.unread);
        el.innerHTML = `<div class="dl-pop-head">${__("Notifications")}</div>` + (n.items.length ? n.items.map((i) => `<button class="dl-pop-item dl-note ${i.read ? "" : "dl-unread"}" data-dt="${esc(i.document_type)}" data-dn="${esc(i.document_name)}"><span>${esc(i.subject)}<small>${esc(when(i.creation))}</small></span></button>`).join("") : `<div class="dl-pop-empty">${__("You are all caught up")}</div>`);
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
      }
    }
    badge(name, n) {
      const b = this.top.querySelector(`[data-badge="${name}"]`);
      if (!b)
        return;
      b.textContent = n > 99 ? "99+" : n;
      b.hidden = !n;
    }
    set_tasks(tasks) {
      this.tasks = tasks || [];
      this.badge("tasks", this.tasks.length);
      const b = this.top.querySelector('[data-badge="tasks"]');
      if (b)
        b.classList.toggle("dl-hot", this.tasks.some((t) => t.priority === "High"));
    }
    draw_tasks() {
      const el = this.pop("tasks");
      const t = this.tasks || [];
      el.innerHTML = `<div class="dl-pop-head">${__("Pending tasks")}</div>` + (t.length ? t.map((x, i) => `<button class="dl-pop-item" data-task="${i}"><i class="dl-dot dl-p-${x.priority.toLowerCase()}"></i><span>${esc(__(x.label))}</span><em>${x.count}</em></button>`).join("") : `<div class="dl-pop-empty">${__("Nothing needs attention")}</div>`);
      el.onclick = (e) => {
        const b = e.target.closest("[data-task]");
        if (b) {
          this.close_pops();
          go(t[b.dataset.task].route);
        }
      };
    }
    render_side() {
      this.side = this.root.querySelector(".dl-side");
      this.side.innerHTML = `
			<div class="dl-side-head"><label class="dl-find">${icon("search")}<input type="search" placeholder="${__("Find a page\u2026")}" aria-label="${__("Find a page")}"></label>
			<button class="dl-collapse" data-act="collapse" title="${__("Collapse sidebar")}" aria-label="${__("Collapse sidebar")}">${icon("panel")}</button></div>
			<nav class="dl-nav"></nav>`;
      this.nav = this.side.querySelector(".dl-nav");
      this.find = this.side.querySelector(".dl-find input");
      this.find.addEventListener("input", debounce(() => this.draw_nav(), 120));
      this.draw_nav();
      this.side.addEventListener("click", (e) => {
        if (e.target.closest('[data-act="collapse"]'))
          return this.set_collapsed(!this.root.classList.contains("dl-collapsed"));
        const g = e.target.closest("[data-group]");
        if (g) {
          if (this.root.classList.contains("dl-collapsed"))
            this.set_collapsed(false);
          const k = g.dataset.group;
          this.expanded.has(k) ? this.expanded.delete(k) : this.expanded.add(k);
          store("expanded", [...this.expanded]);
          return this.draw_nav();
        }
        const it = e.target.closest("[data-item]");
        if (!it)
          return;
        const [gi, ii] = it.dataset.item.split(":").map(Number);
        const item = this.ctx.sidebar[gi].items[ii];
        this.root.classList.remove("dl-drawer");
        if (item.anchor) {
          this.active = item.anchor;
          this.draw_nav();
          this.hooks.scroll_to(item.anchor);
        } else
          go(item);
      });
    }
    draw_nav() {
      const q = (this.find ? this.find.value : "").trim().toLowerCase();
      this.nav.innerHTML = this.ctx.sidebar.map((g, gi) => {
        const items = g.items.map((it, ii) => ({ it, ii })).filter(({ it }) => !q || it.label.toLowerCase().includes(q) || g.label.toLowerCase().includes(q));
        if (!items.length)
          return "";
        const open = q || this.expanded.has(g.key);
        return `<div class="dl-group ${open ? "dl-open" : ""}">
					<button class="dl-group-btn" data-group="${esc(g.key)}" title="${esc(__(g.label))}">${icon(g.icon)}<span>${esc(__(g.label))}</span>${icon("chevron", "dl-chev")}</button>
					<div class="dl-group-items">${items.map(({ it, ii }) => `<button class="dl-item ${it.anchor && it.anchor === this.active ? "dl-on" : ""}" data-item="${gi}:${ii}">${esc(__(it.label))}</button>`).join("")}</div></div>`;
      }).join("");
      if (!this.nav.innerHTML)
        this.nav.innerHTML = `<div class="dl-pop-empty">${__("No pages match")}</div>`;
    }
    set_collapsed(on) {
      this.root.classList.toggle("dl-collapsed", !!on);
      store("collapsed", !!on);
    }
    bind_global() {
      this.root.querySelector(".dl-scrim").addEventListener("click", () => this.root.classList.remove("dl-drawer"));
      this.top.querySelector(".dl-pop[data-pop=search]").addEventListener("click", (e) => {
        const b = e.target.closest("[data-res]");
        if (b)
          this.open_result(this.results[b.dataset.res]);
      });
      this.on_doc_click = (e) => {
        if (!this.root.isConnected)
          return document.removeEventListener("click", this.on_doc_click);
        if (!e.target.closest(".dl-anchor, .dl-search"))
          this.close_pops();
      };
      document.addEventListener("click", this.on_doc_click);
      this.on_key = (e) => {
        if (!this.root.isConnected)
          return document.removeEventListener("keydown", this.on_key);
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k" && document.body.classList.contains("dl-active")) {
          e.preventDefault();
          this.search_input.focus();
          this.search_input.select();
        } else if (e.key === "Escape")
          this.close_pops();
      };
      document.addEventListener("keydown", this.on_key);
    }
  };

  // ../dsa_loan/dsa_loan/public/js/dsa_admin_dashboard_v2/overview.js
  var PRESET_SHORT = { today: "Today", this_week: "Week", this_month: "Month", last_month: "Last month", this_quarter: "Quarter", this_year: "Year", custom: "Custom" };
  var KPI_ICONS = { lenders: "landmark", active_lenders: "check-circle", applications: "file-text", approved: "badge-check", rejected: "x-circle", disbursed: "wallet", commission: "percent", queries: "message-circle" };
  var dstr = (value) => value ? new Date(`${value}T00:00:00`).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "\u2014";
  var Overview = class {
    constructor(main, ctx, on_change) {
      this.main = main;
      this.ctx = ctx;
      this.on_change = on_change;
      this.tab = "amount";
      const saved = store("lender-dashboard-range") || {};
      const validPreset = (ctx.presets || []).some((item) => item.value === saved.preset);
      this.state = {
        preset: validPreset ? saved.preset : ctx.default_preset || "this_month",
        from: saved.from || "",
        to: saved.to || "",
        lender: (ctx.lenders || []).some((item) => item.value === saved.lender) ? saved.lender : ctx.default_lender || ""
      };
      if (this.state.preset === "custom" && !(this.state.from && this.state.to))
        this.state.preset = ctx.default_preset || "this_month";
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
      store("lender-dashboard-range", __spreadValues({}, this.state));
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
                        <div class="dl-custom" hidden><input type="date" data-from value="${esc(this.state.from)}" aria-label="${__("From date")}"><span>\u2192</span><input type="date" data-to value="${esc(this.state.to)}" aria-label="${__("To date")}"><button class="dl-btn" data-apply>${__("Apply")}</button></div>
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
    skeleton(count, cls = "") {
      return Array.from({ length: count }, () => `<div class="dl-sk ${cls}"></div>`).join("");
    }
    sec(name) {
      return this.main.querySelector(`[data-sec="${name}"]`);
    }
    set_loading(on) {
      this.main.classList.toggle("dl-loading", !!on);
      if (on)
        this.main.querySelector("[data-error]").hidden = true;
    }
    set_error() {
      this.set_loading(false);
      const el = this.main.querySelector("[data-error]");
      el.hidden = false;
      el.innerHTML = `${icon("alert-circle")}<span>${__("Could not load dashboard data.")}</span><button class="dl-btn" data-refresh>${__("Retry")}</button>`;
    }
    sync_custom() {
      const custom = this.main.querySelector(".dl-custom");
      if (custom)
        custom.hidden = this.state.preset !== "custom";
      this.main.querySelectorAll("[data-preset]").forEach((button) => button.classList.toggle("dl-on", button.dataset.preset === this.state.preset));
    }
    on_click(event) {
      const target = event.target.closest("button, [data-route], [data-open]");
      if (!target || !this.main.contains(target))
        return;
      if (target.dataset.preset) {
        this.state.preset = target.dataset.preset;
        this.sync_custom();
        if (this.state.preset !== "custom") {
          this.persist();
          this.on_change();
        }
        return;
      }
      if (target.hasAttribute("data-apply")) {
        const from = this.main.querySelector("[data-from]").value;
        const to = this.main.querySelector("[data-to]").value;
        if (!from || !to)
          return frappe.show_alert({ message: __("Choose both dates."), indicator: "orange" });
        if (from > to)
          return frappe.show_alert({ message: __("From date must be on or before To date."), indicator: "red" });
        this.state.from = from;
        this.state.to = to;
        this.persist();
        return this.on_change();
      }
      if (target.hasAttribute("data-reset")) {
        this.state = { preset: this.ctx.default_preset || "this_month", from: "", to: "", lender: "" };
        const select = this.main.querySelector("[data-lender]");
        if (select)
          select.value = "";
        this.sync_custom();
        this.persist();
        return this.on_change();
      }
      if (target.hasAttribute("data-refresh"))
        return this.on_change();
      if (target.dataset.qa !== void 0) {
        const action = (this.ctx.quick_actions || [])[Number(target.dataset.qa)];
        if (action && action.doctype)
          return frappe.new_doc(action.doctype);
      }
      if (target.dataset.kpi !== void 0)
        return this.show_kpi(Number(target.dataset.kpi));
      if (target.hasAttribute("data-modal-close")) {
        this.main.querySelector("[data-modal-host]").innerHTML = "";
        return;
      }
      if (target.hasAttribute("data-modal-open")) {
        const spec = this.modalRoute;
        if (spec)
          go(spec);
        this.main.querySelector("[data-modal-host]").innerHTML = "";
        return;
      }
      if (target.dataset.route) {
        try {
          return go(JSON.parse(target.dataset.route));
        } catch (error) {
          console.error(error);
        }
      }
      if (target.dataset.open && target.dataset.name)
        return open_doc(target.dataset.open, target.dataset.name);
    }
    on_input(event) {
      if (event.target.matches("[data-lender]")) {
        this.state.lender = event.target.value;
        this.persist();
        this.on_change();
      }
    }
    route_attr(route) {
      return route ? `data-route='${esc(JSON.stringify(route))}'` : "disabled";
    }
    show_kpi(index) {
      var _a;
      const item = (((_a = this.d) == null ? void 0 : _a.kpis) || [])[index];
      if (!item)
        return;
      this.modalRoute = item.route;
      const value = item.format === "Currency" ? money(item.value) : num(item.value);
      this.main.querySelector("[data-modal-host]").innerHTML = `<div class="dl-modal-backdrop" data-modal-close><section class="dl-card dl-modal" role="dialog" aria-modal="true" aria-label="${esc(__(item.label))}"><header><h2>${esc(__(item.label))}</h2><button class="dl-icon-btn" data-modal-close aria-label="${__("Close")}">${icon("x")}</button></header><div class="dl-modal-value">${esc(value)}</div><p>${esc(__(item.preview || "Live records matching the current filters."))}</p><div class="dl-modal-actions"><button class="dl-btn" data-modal-close>${__("Close")}</button><button class="dl-btn dl-btn-primary" data-modal-open>${__("View records")}</button></div></section></div>`;
    }
    render(response) {
      this.resp = response;
      this.d = response.data || {};
      this.set_loading(false);
      this.main.querySelector("[data-range]").innerHTML = `${icon("calendar")}<span>${dstr(response.from_date)} \u2013 ${dstr(response.to_date)}</span><i></i><span>${esc(response.lender || __("All Lenders"))}</span>`;
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
    column(key, trend, series, money_values) {
      const el = this.sec(key);
      if (!trend || allzero(series.map((s) => s.values)))
        return el.innerHTML = empty(__("No records in the last 6 months."), "chart");
      el.innerHTML = `<div class="dl-chart-host"></div>`;
      try {
        new frappe.Chart(el.firstChild, {
          type: "bar",
          height: 230,
          animate: 0,
          colors: ["#0D9488", "#D97706"].slice(0, series.length),
          data: { labels: trend.labels, datasets: series },
          barOptions: { spaceRatio: 0.45 },
          axisOptions: { xIsSeries: 1, shortenYAxisNumbers: 1 },
          tooltipOptions: { formatTooltipY: (v) => money_values ? money_full(v) : num(v) }
        });
      } catch (error) {
        el.innerHTML = empty(__("The chart could not be drawn."), "alert-circle");
      }
    }
    barlist(key, rows, value, side, none) {
      const el = this.sec(key);
      if (!rows || !rows.length)
        return el.innerHTML = empty(none, "inbox");
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
      this.barlist(
        "comm_status",
        c.commission_status,
        (r) => r.amount,
        (r, main) => main ? money(r.amount) : plural(r.count, __("record"), __("records")),
        __("No commission in this range.")
      );
      this.barlist(
        "by_lender",
        c.by_lender,
        (r) => r.amount,
        (r, main) => main ? money(r.amount) : plural(r.count, __("application"), __("applications")),
        __("Nothing disbursed in this range.")
      );
      this.barlist(
        "loan_types",
        c.loan_types,
        (r) => r.count,
        (r, main) => main ? num(r.count) : `${money(r.amount)} ${__("requested")}`,
        __("No applications in this range.")
      );
      this.barlist(
        "branches",
        c.branches,
        (r) => r.amount || r.count,
        (r, main) => main ? money(r.amount) : plural(r.count, __("application"), __("applications")),
        __("No branch activity in this range.")
      );
      this.barlist(
        "documents",
        c.documents,
        (r) => r.count,
        (r, main) => main ? num(r.count) : "",
        __("No documents for applications in this range.")
      );
    }
    render_kpis(items) {
      const el = this.sec("kpis");
      el.innerHTML = items.map((item, index) => `<button class="dl-hero-cell" data-kpi="${index}"><div class="dl-hero-top"><span class="dl-ico">${icon(KPI_ICONS[item.key] || "chart")}</span><span class="dl-hero-label">${esc(__(item.label))}</span></div><div class="dl-hero-value">${esc(item.format === "Currency" ? money(item.value) : num(item.value))}</div><div class="dl-hero-meta">${__("Click for details")}</div></button>`).join("");
    }
    render_pipeline(stages) {
      const el = this.sec("pipeline");
      if (!stages.length)
        return el.innerHTML = empty(__("No application stages found."));
      const max = Math.max(1, ...stages.map((item) => item.count || 0));
      el.innerHTML = `<ul class="dl-bars">${stages.map((item) => `<li><button ${this.route_attr(item.route)}><span class="dl-bar-l">${esc(__(item.label))}</span><span class="dl-bar"><span style="width:${Math.round((item.count || 0) / max * 100)}%;background:#0D9488"></span></span><b>${num(item.count)}</b></button></li>`).join("")}</ul>`;
    }
    render_tasks(tasks) {
      const el = this.sec("tasks");
      if (!tasks.length)
        return el.innerHTML = empty(__("Nothing needs attention right now."), "check-circle");
      el.innerHTML = `<ul class="dl-tasks">${tasks.map((item) => `<li><button ${this.route_attr(item.route)}><i class="dl-dot dl-p-${String(item.priority || "Medium").toLowerCase()}"></i><span class="dl-task-l">${esc(__(item.label))}<small>${esc(__(item.priority || "Medium"))}</small></span><b>${num(item.count)}</b></button></li>`).join("")}</ul>`;
    }
    render_lenders(rows) {
      const el = this.sec("lenders");
      this.main.querySelector('[data-sub="lenders"]').textContent = `${rows.length} ${__("lenders")}`;
      if (!rows.length)
        return el.innerHTML = empty(__("No lender records found."), "landmark");
      el.innerHTML = `<div class="dl-table-wrap"><table class="dl-table"><thead><tr><th>${__("Lender")}</th><th>${__("Status")}</th><th>${__("Type")}</th><th class="r">${__("Applications")}</th><th class="r">${__("Approved")}</th><th class="r">${__("Disbursed")}</th><th class="r">${__("Pending Commission")}</th></tr></thead><tbody>${rows.map((row) => `<tr><td><button class="dl-link dl-strong" data-open="Lender" data-name="${esc(row.lender)}">${esc(row.lender_name)}</button></td><td>${row.status ? pill(row.status) : "\u2014"}</td><td>${esc(row.lender_type || "\u2014")}</td><td class="r">${num(row.applications)}</td><td class="r">${num(row.approved)}</td><td class="r">${money(row.disbursed)}</td><td class="r">${money(row.commission)}</td></tr>`).join("")}</tbody></table></div>`;
    }
    render_disbursements(data) {
      const el = this.sec("disbursements");
      el.innerHTML = `<div class="dl-statline"><div><b>${money(data.amount || 0)}</b><span>${__("Confirmed amount")}</span></div><div><b>${num(data.count || 0)}</b><span>${__("Confirmed records")}</span></div><div><b>${money(data.average || 0)}</b><span>${__("Average disbursement")}</span></div></div><button class="dl-link" data-route='${esc(JSON.stringify({ doctype: "Loan Disbursement", filters: { disbursement_status: "Confirmed" } }))}'>${__("View disbursements")}</button>`;
    }
    render_commissions(data) {
      const el = this.sec("commissions");
      el.innerHTML = `<div class="dl-statline"><div><b>${money(data.pending_amount || 0)}</b><span>${__("Not yet paid")}</span></div><div><b>${num(data.pending_count || 0)}</b><span>${__("Open records")}</span></div></div><p class="dl-note">${__("Calculated, approved, invoiced or partly paid commission (gross).")}</p><button class="dl-link" data-route='${esc(JSON.stringify({ doctype: "Commission Calculation", filters: { calculation_status: ["in", ["Calculated", "Approved", "Invoiced", "Partially Paid"]] } }))}'>${__("View commission records")}</button>`;
    }
  };

  // ../dsa_loan/dsa_loan/public/js/dsa_admin_dashboard_v2.bundle.js
  var API2 = "dsa_loan.dashboard_v2.api.";
  var Dashboard = class {
    constructor(wrapper) {
      this.root = document.createElement("div");
      this.root.className = "dl-app";
      this.root.innerHTML = `
			<header class="dl-top"></header>
			<aside class="dl-side"></aside>
			<div class="dl-scrim"></div>
			<main class="dl-main"><div class="dl-boot"><span class="dl-spin"></span>${__("Loading dashboard\u2026")}</div></main>`;
      $(wrapper).empty().append(this.root);
      this.init();
    }
    async init() {
      try {
        this.ctx = await frappe.xcall(API2 + "get_context");
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
      const seq = this.seq = (this.seq || 0) + 1;
      this.overview.set_loading(true);
      try {
        const resp = await frappe.xcall(API2 + "get_overview", this.overview.args());
        if (seq !== this.seq)
          return;
        set_currency(resp.currency);
        this.overview.render(resp);
        this.shell.set_tasks(resp.data.tasks || []);
        this.loaded_at = Date.now();
      } catch (e) {
        if (seq !== this.seq)
          return;
        this.overview.set_error();
      }
    }
    on_show() {
      if (this.loaded_at && Date.now() - this.loaded_at > 60 * 1e3)
        this.load();
      this.shell && this.shell.refresh_notification_badge();
    }
  };
  frappe.provide("dsa_loan.dashboard_v2");
  dsa_loan.dashboard_v2.Dashboard = Dashboard;
})();
//# sourceMappingURL=dsa_admin_dashboard_v2.bundle.3M3WZBJ6.js.map
