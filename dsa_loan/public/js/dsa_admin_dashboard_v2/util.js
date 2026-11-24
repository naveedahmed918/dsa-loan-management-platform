// Shared helpers for the DSA Admin Dashboard.

const P = {
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
	building: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>',
};

export function icon(name, cls = "") {
	return `<svg class="dl-i ${cls}" viewBox="0 0 24 24" aria-hidden="true">${P[name] || P.grid}</svg>`;
}

// Original mark: a mint coin with a rising emerald arc
export const LOGO = `<svg viewBox="0 0 32 32" aria-hidden="true">
	<defs><linearGradient id="dl-lg" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#0F766E"/><stop offset="1" stop-color="#6FD3B4"/></linearGradient></defs>
	<circle cx="16" cy="16" r="14" fill="#E3F3EC"/>
	<path d="M6.5 21.5c4-.5 6.5-3.2 8-7 1.2-3 3.4-5 7.5-5.5" fill="none" stroke="url(#dl-lg)" stroke-width="3.2" stroke-linecap="round"/>
	<circle cx="22.8" cy="9.2" r="2.6" fill="#123C3A"/>
</svg>`;

export const COLORS = ["#0F766E", "#34A88A", "#D97706", "#71817B", "#123C3A", "#9AD4C0", "#DC2626", "#B7791F"];

export const esc = (v) => frappe.utils.escape_html(v == null ? "" : String(v));

let currency = "INR";
export function set_currency(c) {
	currency = c || "INR";
}

const trim = (x) => x.toFixed(2).replace(/\.?0+$/, "");
const SYM = { INR: "₹", USD: "$", EUR: "€", GBP: "£" };

/** 25000 -> ₹25,000 ; 250000 -> ₹2.5 L ; 12000000 -> ₹1.2 Cr (INR). */
export function money(v, compact = true) {
	if (v == null) return "—";
	const n = Number(v) || 0;
	const sym = SYM[currency] || currency + " ";
	const a = Math.abs(n);
	const sign = n < 0 ? "-" : "";
	if (compact && currency === "INR") {
		if (a >= 1e7) return `${sign}${sym}${trim(a / 1e7)} Cr`;
		if (a >= 1e5) return `${sign}${sym}${trim(a / 1e5)} L`;
	}
	if (compact && currency !== "INR" && a >= 1e6) return `${sign}${sym}${trim(a / 1e6)}M`;
	return `${sign}${sym}${a.toLocaleString(currency === "INR" ? "en-IN" : undefined, { maximumFractionDigits: 0 })}`;
}

export function money_full(v) {
	if (v == null) return "—";
	const n = Number(v) || 0;
	return `${SYM[currency] || currency + " "}${n.toLocaleString(currency === "INR" ? "en-IN" : undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function num(v) {
	if (v == null) return "—";
	return (Number(v) || 0).toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

export const fmt = (v, format) => (format === "Currency" ? money(v) : num(v));
export const full = (v, format) => (v == null ? "" : format === "Currency" ? money_full(v) : num(v));

export function clone(o) {
	return o ? JSON.parse(JSON.stringify(o)) : o;
}

/** Open a route spec: {doctype, filters} -> filtered list; {route:[...], filters} -> that route. */
export function go(spec) {
	if (!spec) return;
	if (spec.doctype && !spec.route) {
		frappe.route_options = clone(spec.filters || {});
		frappe.set_route("List", spec.doctype);
		return;
	}
	if (spec.filters) frappe.route_options = clone(spec.filters);
	frappe.set_route(...spec.route);
}

export const open_doc = (doctype, name) => frappe.set_route("Form", doctype, name);

export function pill(status) {
	if (!status) return "";
	const s = String(status);
	let c = "dl-info";
	if (/^(Disbursed|Paid|Processed|Approved|Sanctioned|Active|Completed|Receive)$/.test(s)) c = "dl-ok";
	else if (/(Reject|Cancel|Fail|Overdue|Suspend|Terminat|Withdraw)/.test(s)) c = "dl-bad";
	else if (/(Pending|Draft|Unpaid|Partial|Invoiced|Required|On Hold|Inactive|Expired|Review|Submitted)/.test(s)) c = "dl-warn";
	return `<span class="dl-pill ${c}">${esc(__(s))}</span>`;
}

export function store(key, value) {
	try {
		if (value === undefined) return JSON.parse(localStorage.getItem("dsa_dash_" + key));
		localStorage.setItem("dsa_dash_" + key, JSON.stringify(value));
	} catch (e) {
		return null;
	}
}

export function initials(name) {
	const parts = String(name || "?").trim().split(/\s+/);
	return (esc(((parts[0] || "")[0] || "") + ((parts[1] || "")[0] || "")) || "?").toUpperCase();
}

export function debounce(fn, ms) {
	let t;
	return (...a) => {
		clearTimeout(t);
		t = setTimeout(() => fn(...a), ms);
	};
}

export const empty = (msg, ic = "inbox") => `<div class="dl-empty">${icon(ic)}<span>${esc(msg)}</span></div>`;
export const unavailable = () =>
	`<div class="dl-empty dl-locked">${icon("lock")}<span>${__("Unavailable")}</span><small>${__("You may not have access, or this module is not set up yet.")}</small></div>`;

export const allzero = (arrs) => arrs.every((a) => (a || []).every((v) => !v));

export function when(ts) {
	if (!ts) return "";
	try {
		return frappe.datetime.prettyDate(ts, true);
	} catch (e) {
		return String(ts);
	}
}

/** Tiny inline sparkline (no axes). */
export function spark(values, color = "#0F766E") {
	const v = (values || []).map((x) => Number(x) || 0);
	if (v.length < 2 || v.every((x) => !x)) return `<svg class="dl-spark" viewBox="0 0 100 28" preserveAspectRatio="none"><line x1="0" y1="26" x2="100" y2="26" stroke="${color}" stroke-opacity=".25" stroke-width="1.5" stroke-dasharray="3 3"/></svg>`;
	const max = Math.max(...v);
	const pts = v.map((x, i) => `${((i / (v.length - 1)) * 100).toFixed(1)},${(25 - (x / max) * 22).toFixed(1)}`);
	return `<svg class="dl-spark" viewBox="0 0 100 28" preserveAspectRatio="none"><polygon points="0,28 ${pts.join(" ")} 100,28" fill="${color}" fill-opacity=".12"/><polyline points="${pts.join(" ")}" fill="none" stroke="${color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>`;
}
