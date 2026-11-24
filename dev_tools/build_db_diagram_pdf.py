"""PDF 1 - database diagram of the DSA Loan Portal DocTypes, drawn from the DocType JSON files.

Usage (Windows py, has reportlab): py tools/build_db_diagram_pdf.py <module_dir> <output.pdf>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4, landscape  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import Flowable, PageBreak, SimpleDocTemplate, Spacer  # noqa: E402

from pdfkit_common import (GROUP_COLOURS, GROUP_OF, GROUPS, GRID, MUTED, NAVY, TEAL, E, P, bullets, cover, data_fields,  # noqa: E402
                           footer, load_doctypes, table)

MOD, OUT = sys.argv[1], sys.argv[2]
DOCS = load_doctypes(MOD)
LINK_TYPES = ("Link", "Dynamic Link", "Table")
EXTERNAL_NOTE = {"Company": "ERPNext", "Employee": "ERPNext", "Customer": "ERPNext", "Sales Invoice": "ERPNext",
                 "Purchase Invoice": "ERPNext", "Address": "Frappe", "Email Group": "Frappe", "Email Template": "Frappe",
                 "Communication": "Frappe", "Workflow State": "Frappe", "DocType": "Frappe"}


def links(dt):
	"""(fieldname, fieldtype, target) for every link-type field of a DocType."""
	out = []
	for f in DOCS[dt]["fields"]:
		if f["fieldtype"] == "Dynamic Link":
			out.append((f["fieldname"], "Dynamic Link", "(" + f["options"] + ")"))
		elif f["fieldtype"] in ("Link", "Table"):
			out.append((f["fieldname"], f["fieldtype"], f["options"]))
	return out


def key_fields(dt, limit=3):
	pick = []
	for f in data_fields(DOCS[dt]):
		if f["fieldtype"] in LINK_TYPES:
			continue
		n = f["fieldname"]
		if "status" in n or n in ("final_status", "requested_loan_amount", "sanctioned_amount", "gross_commission",
		                          "net_commission", "current_disbursement_amount", "invoice_total", "net_payable",
		                          "clawback_amount", "commission_percentage", "document_name", "customer_name",
		                          "lender_name", "product_name", "scheme_name", "pan_number", "aadhaar_last_4",
		                          "assessment_year", "salary_month", "months_covered", "mobile_number", "applicant_type"):
			pick.append(f)
	return pick[:limit]


def naming(dt):
	d = DOCS[dt]
	if d.get("istable"):
		return "row id (child table)"
	an = d.get("autoname", "")
	if an.startswith("field:"):
		return f"= {an[6:]}"
	return an.replace(".YYYY.", "YYYY").replace(".#####", "#####").replace(".", "")


# ------------------------------------------------------------------ drawing
class Diagram(Flowable):
	"""Cards (DocTypes) in columns, joined by elbow lines from a link field to the card it points to."""

	HEAD, ROWH, W = 15, 9.6, 166

	def __init__(self, width, height, columns, title=None, compact=False, show_external=True):
		super().__init__()
		self.width, self.height, self.columns, self.compact, self.show_external = width, height, columns, compact, show_external
		self.cards = {}
		self.title = title
		if compact:
			self.W = 120

	def card_rows(self, dt, mode):
		if self.compact:
			return []
		rows = [("PK", "name", naming(dt))]
		if DOCS[dt].get("istable"):
			parent = [p for p in DOCS if any(f["fieldtype"] == "Table" and f["options"] == dt for f in DOCS[p]["fields"])]
			rows = [("", "parent", "-> " + ", ".join(parent))]
		if mode == "ref":
			return rows
		for fn, ft, target in links(dt):
			if target in DOCS or target.startswith("(") or self.show_external:
				tag = {"Table": "TAB", "Dynamic Link": "DYN"}.get(ft, "FK")
				ext = f"  [{EXTERNAL_NOTE[target]}]" if target in EXTERNAL_NOTE else ""
				rows.append((tag, fn, target + ext))
		for f in key_fields(dt):
			rows.append(("", f["fieldname"], f["fieldtype"]))
		return rows

	def layout(self):
		ncol = len(self.columns)
		gap = (self.width - ncol * self.W) / max(ncol - 1, 1)
		for ci, col in enumerate(self.columns):
			x = ci * (self.W + gap)
			cards = [(dt, mode, self.card_rows(dt, mode)) for dt, mode in col]
			total = sum(self.HEAD + len(r) * self.ROWH + 4 for _, _, r in cards)
			vgap = max(10, (self.height - total) / max(len(cards), 1)) if len(cards) > 1 else 0
			vgap = min(vgap, 34 if not self.compact else 50)
			y = self.height
			for dt, mode, rows in cards:
				h = self.HEAD + len(rows) * self.ROWH + 4
				self.cards[dt] = dict(x=x, y=y - h, w=self.W, h=h, rows=rows, mode=mode)
				y -= h + vgap
			if y < -2:
				print(f"WARNING: column {ci} overflows by {-y:.0f}pt ({[c[0] for c in col]})")

	def draw(self):
		self.layout()
		c = self.canv
		lane = {}
		# edges first, cards on top
		for dt, card in self.cards.items():
			if self.compact:
				for fn, ft, target in links(dt):
					targets = [t for t in GROUPS["Documents"][1:]] if ft == "Dynamic Link" else [target]
					parents = [] if not DOCS[dt].get("istable") else [p for p in DOCS if any(
						f["fieldtype"] == "Table" and f["options"] == dt for f in DOCS[p]["fields"])]
					for t in [x for x in targets if x in self.cards and x != dt]:
						self.edge(card, 0, self.cards[t], dashed=ft != "Link", lane=lane)
				for p in ([] if not DOCS[dt].get("istable") else [p for p in DOCS if any(
						f["fieldtype"] == "Table" and f["options"] == dt for f in DOCS[p]["fields"])]):
					if p in self.cards:
						self.edge(card, 0, self.cards[p], dashed=True, lane=lane)
				continue
			for i, (tag, fn, target) in enumerate(card["rows"]):
				tgt = target.split("  [")[0]
				targets = []
				if tag in ("FK", "TAB") and tgt in self.cards and tgt != dt:
					targets = [tgt]
				elif tag == "DYN":
					targets = [t for t in GROUPS["Documents"][1:] if t in self.cards]
				elif tag == "" and fn == "parent":
					targets = [t for t in tgt[3:].split(", ") if t in self.cards]
				for t in targets:
					self.edge(card, i, self.cards[t], dashed=tag in ("DYN", "TAB") or fn == "parent", lane=lane)
		for dt, card in self.cards.items():
			self.card(dt, card)

	def edge(self, src, row, dst, dashed, lane):
		c = self.canv
		if self.compact:
			sy = src["y"] + src["h"] / 2
		else:
			sy = src["y"] + src["h"] - self.HEAD - (row + 0.5) * self.ROWH - 2
		ty = dst["y"] + dst["h"] - self.HEAD / 2
		c.saveState()
		col = GROUP_COLOURS[GROUP_OF.get(dst_name(self.cards, dst), "Child table")]
		c.setStrokeColor(col)
		c.setFillColor(col)
		c.setLineWidth(0.7 if not self.compact else 0.6)
		if self.compact:
			c.setStrokeAlpha(0.6)
		if dashed:
			c.setDash(3, 2)
		if dst["x"] > src["x"] + 1:  # target to the right
			x1, x2 = src["x"] + src["w"], dst["x"]
			k = lane.setdefault(("r", round(x1)), [0])
			k[0] += 1
			mx = x1 + 6 + (k[0] % 9) * 3.2
			path = [(x1, sy), (mx, sy), (mx, ty), (x2, ty)]
			head = (x2, ty, 1)
		elif dst["x"] < src["x"] - 1:  # to the left
			x1, x2 = src["x"], dst["x"] + dst["w"]
			k = lane.setdefault(("l", round(x1)), [0])
			k[0] += 1
			mx = x1 - 6 - (k[0] % 9) * 3.2
			path = [(x1, sy), (mx, sy), (mx, ty), (x2, ty)]
			head = (x2, ty, -1)
		else:  # same column: loop out on the right
			x1 = src["x"] + src["w"]
			k = lane.setdefault(("s", round(x1)), [0])
			k[0] += 1
			mx = x1 + 5 + (k[0] % 6) * 3
			path = [(x1, sy), (mx, sy), (mx, ty), (x1, ty)]
			head = (x1, ty, -1)
		p = c.beginPath()
		p.moveTo(*path[0])
		for pt in path[1:]:
			p.lineTo(*pt)
		c.drawPath(p, stroke=1, fill=0)
		c.setDash()
		c.circle(path[0][0], path[0][1], 1.3, stroke=0, fill=1)
		hx, hy, d = head
		a = c.beginPath()
		a.moveTo(hx, hy)
		a.lineTo(hx - 4.5 * d, hy + 2.4)
		a.lineTo(hx - 4.5 * d, hy - 2.4)
		a.close()
		c.drawPath(a, stroke=0, fill=1)
		c.restoreState()

	def card(self, dt, card):
		c = self.canv
		x, y, w, h = card["x"], card["y"], card["w"], card["h"]
		colour = GROUP_COLOURS[GROUP_OF.get(dt, "Child table")]
		ref = card["mode"] == "ref"
		c.saveState()
		c.setFillColor(colors.white)
		c.setStrokeColor(colour if not ref else MUTED)
		c.setLineWidth(0.9)
		if ref:
			c.setDash(2, 1.5)
		c.roundRect(x, y, w, h, 3, stroke=1, fill=1)
		c.setDash()
		c.setFillColor(colour if not ref else colors.HexColor("#8796a6"))
		c.roundRect(x, y + h - self.HEAD, w, self.HEAD, 3, stroke=0, fill=1)
		c.rect(x, y + h - self.HEAD, w, 4, stroke=0, fill=1)
		c.setFillColor(colors.white)
		c.setFont("UI-B", 7.6)
		label = dt + ("  (child)" if DOCS[dt].get("istable") else "") + ("  (ref)" if ref and not self.compact else "")
		c.drawString(x + 4, y + h - self.HEAD + 4.4, label)
		ry = y + h - self.HEAD - self.ROWH + 1
		for tag, fn, info in card["rows"]:
			if tag:
				c.setFillColor({"PK": NAVY, "FK": TEAL, "TAB": colors.HexColor("#6b3fa0"), "DYN": colors.HexColor("#8a5a00")}[tag])
				c.setFont("UI-B", 5.6)
				c.drawString(x + 3, ry + 1.8, tag)
			c.setFillColor(colors.black)
			c.setFont("UI", 6.4)
			c.drawString(x + 19, ry + 1.6, fn)
			c.setFillColor(MUTED)
			c.setFont("UI", 6.0)
			room = w - 19 - c.stringWidth(fn, "UI", 6.4) - 8
			txt = info
			while txt and c.stringWidth(txt, "UI", 6.0) > room:
				txt = txt[:-2]
			if txt != info:
				txt = txt[:-1] + "..."
			c.drawRightString(x + w - 3, ry + 1.6, txt)
			ry -= self.ROWH
		c.restoreState()


def dst_name(cards, dst):
	for k, v in cards.items():
		if v is dst:
			return k
	return ""


class Lifecycle(Flowable):
	STEPS = [("Loan Lead", "enquiry"), ("Loan Customer", "Convert to Customer"), ("Loan Application", "requirement, lender"),
	         ("Document Checklist", "AUTO per applicant"), ("Document data", "Aadhaar, PAN, bank..."),
	         ("Status flow", "Submitted -> Sanctioned"), ("Loan Disbursement", "staff mark Confirmed"),
	         ("Commission Calculation", "AUTO"), ("Sales Invoice + email", "AUTO, ERPNext"), ("Commission Invoice", "AUTO"),
	         ("Lender Payout Statement", "AUTO monthly"), ("Franchise Settlement", "AUTO draft"), ("Clawback + notes", "AUTO on early closure")]

	def __init__(self, width, height=170):
		super().__init__()
		self.width, self.height = width, height

	def draw(self):
		c = self.canv
		per_row = 7
		bw, bh, gap = (self.width - (per_row - 1) * 14) / per_row, 40, 14
		for i, (name, note) in enumerate(self.STEPS):
			r, k = divmod(i, per_row)
			if r % 2:
				k = per_row - 1 - k
			x, y = k * (bw + gap), self.height - bh - r * (bh + 38)
			is_auto = "AUTO" in note
			c.setFillColor(colors.HexColor("#e6f4f1") if is_auto else colors.HexColor("#eef2f7"))
			c.setStrokeColor(TEAL if is_auto else NAVY)
			c.roundRect(x, y, bw, bh, 4, stroke=1, fill=1)
			c.setFillColor(NAVY)
			c.setFont("UI-B", 7.4)
			c.drawCentredString(x + bw / 2, y + 24, name)
			c.setFillColor(TEAL if is_auto else MUTED)
			c.setFont("UI", 6.8)
			c.drawCentredString(x + bw / 2, y + 11, note)
			if i < len(self.STEPS) - 1:
				nr, nk = divmod(i + 1, per_row)
				c.setStrokeColor(MUTED)
				c.setFillColor(MUTED)
				if nr == r:
					d = 1 if r % 2 == 0 else -1
					sx = x + (bw if d == 1 else 0)
					c.line(sx, y + bh / 2, sx + d * (gap - 3), y + bh / 2)
					ax = sx + d * gap
					p = c.beginPath(); p.moveTo(ax, y + bh / 2); p.lineTo(ax - 4 * d, y + bh / 2 + 2.5); p.lineTo(ax - 4 * d, y + bh / 2 - 2.5); p.close()
					c.drawPath(p, stroke=0, fill=1)
				else:
					c.line(x + bw / 2, y, x + bw / 2, y - 34)
					p = c.beginPath(); p.moveTo(x + bw / 2, y - 38); p.lineTo(x + bw / 2 - 2.5, y - 33); p.lineTo(x + bw / 2 + 2.5, y - 33); p.close()
					c.drawPath(p, stroke=0, fill=1)


class Legend(Flowable):
	def __init__(self, width, height=58):
		super().__init__()
		self.width, self.height = width, height

	def draw(self):
		c = self.canv
		x = 0
		c.setFont("UI-B", 8)
		c.setFillColor(NAVY)
		c.drawString(0, self.height - 10, "Colour = area of the system")
		for g, col in GROUP_COLOURS.items():
			c.setFillColor(col)
			c.roundRect(x, self.height - 30, 12, 10, 2, stroke=0, fill=1)
			c.setFillColor(colors.black)
			c.setFont("UI", 8)
			c.drawString(x + 16, self.height - 28, g)
			x += 22 + c.stringWidth(g, "UI", 8) + 14
		y = 8
		c.setStrokeColor(TEAL); c.setFillColor(TEAL); c.setLineWidth(0.8)
		c.circle(2, y + 3, 1.4, stroke=0, fill=1); c.line(2, y + 3, 40, y + 3)
		p = c.beginPath(); p.moveTo(44, y + 3); p.lineTo(39, y + 5.5); p.lineTo(39, y + 0.5); p.close(); c.drawPath(p, stroke=0, fill=1)
		c.setFillColor(colors.black); c.setFont("UI", 8)
		c.drawString(50, y, "Link: many records on the dot side point to one record at the arrow (e.g. many Applications -> one Lender)")
		c.setDash(3, 2); c.setStrokeColor(colors.HexColor("#6b3fa0"))
		c.line(470, y + 3, 508, y + 3); c.setDash()
		c.drawString(516, y, "Child table / Dynamic Link (rows stored inside the parent)")


def overview_columns():
	return [
		[(d, "full") for d in GROUPS["Lender masters"]],
		[(d, "full") for d in GROUPS["DSA & people"] + ["Loan Lead", "Loan Customer"]],
		[(d, "full") for d in ["Loan Application", "Co-Applicant", "Document Checklist", "Document Checklist Item"]],
		[(d, "full") for d in GROUPS["Documents"][1:]],
		[(d, "full") for d in GROUPS["Money"]],
	]


PAGES = [
	("1. Lender masters", "What each bank offers: products, schemes, document rules and the commission slab. Everything else points here.",
	 [[("Lender Type", "full")], [("Lender", "full")], [("Lender Branch", "full"), ("Loan Product", "full"), ("Loan Scheme", "full")],
	  [("Lender Document Rule", "full"), ("Commission Slab Structure", "full")]]),
	("2. Customer journey: lead, customer, application", "One Loan Application joins a customer to a lender, product and scheme, through a DSA branch (and franchise).",
	 [[("Franchise", "full"), ("DSA Branch", "full"), ("Lender Login", "full")], [("Loan Lead", "full"), ("Loan Customer", "full")],
	  [("Loan Application", "full")], [("Co-Applicant", "full"), ("Lender", "ref"), ("Loan Product", "ref"), ("Loan Scheme", "ref"),
	                                    ("Lender Branch", "ref")]]),
	("3. Documents", "One Document Checklist per applicant; each row points (Dynamic Link) to a record in one of the 7 document-data DocTypes.",
	 [[("Loan Application", "ref"), ("Loan Customer", "ref"), ("Lender Document Rule", "ref")],
	  [("Document Checklist", "full"), ("Document Checklist Item", "full")],
	  [("Aadhaar Card Data", "full"), ("PAN Card Data", "full"), ("Address Proof Data", "full"), ("Bank Statement Data", "full")],
	  [("Salary Slip Data", "full"), ("ITR Data", "full"), ("Form 16 Data", "full")]]),
	("4. Money: disbursement to settlement", "Every Confirmed tranche earns one Commission Calculation; invoices, payouts, clawbacks and franchise settlements follow from it.",
	 [[("Loan Application", "ref"), ("Lender", "ref"), ("Commission Slab Structure", "ref"), ("Franchise", "ref")],
	  [("Loan Disbursement", "full"), ("Commission Calculation", "full")],
	  [("Commission Invoice", "full"), ("Lender Payout Statement", "full")],
	  [("Commission Clawback", "full"), ("Franchise Settlement", "full")]]),
]


def main():
	pw, ph = landscape(A4)
	W, H = pw - 28 * mm, ph - 34 * mm
	story = cover("DSA Loan Portal", "Database diagram: all 29 DocTypes and how they link",
	              ["A <b>DocType</b> is Frappe's word for a table plus its form. Every box below is one DocType; every line is a "
	               "<b>Link field</b> (a foreign key) from one DocType to another.",
	               "27 main DocTypes and 2 child tables (Co-Applicant, Document Checklist Item), all in the <b>DSA Loan Portal</b> "
	               "module of the <b>dsa_loan</b> app. They also link to ERPNext/Frappe DocTypes such as Company, Employee, "
	               "Customer, Sales Invoice and Email Group (marked [ERPNext] / [Frappe]).",
	               "Page 2: the whole system on one page. Pages 3-6: each area with its key fields. Page 7: the lifecycle of a loan. "
	               "After that: every relationship in a table, and every DocType with its naming rule.",
	               "Drawn directly from the DocType JSON files in the app, so it matches the running system."])
	story += [Spacer(1, 10 * mm), Legend(W), PageBreak()]

	story += [P("Overview: the whole system", "h1"),
	          P("Columns left to right: lender masters, DSA and people, the application, document data, money. "
	            "Each line is a link between two of the DSA DocTypes (links to ERPNext/Frappe are left out here).", "small"),
	          Spacer(1, 4), Diagram(W, H - 64, overview_columns(), compact=True, show_external=False), PageBreak()]

	for title, note, cols in PAGES:
		story += [P(title, "h1"), P(note + "  <b>PK</b> = primary key (record name), <b>FK</b> = link field, "
		                                  "<b>TAB</b> = child table, <b>DYN</b> = dynamic link. Grey dashed cards marked (ref) are drawn in full on another page.", "small"),
		          Spacer(1, 4), Diagram(W, H - 70, cols), PageBreak()]

	story += [P("5. Lifecycle of one loan", "h1"),
	          P("The order records are created in. Teal boxes are created automatically by the system; the rest are entered by staff.", "small"),
	          Spacer(1, 10), Lifecycle(W), Spacer(1, 14)]
	story += bullets([
		"<b>Lead to customer:</b> the agent records a Loan Lead and clicks Convert to Customer.",
		"<b>Application:</b> saving it creates one Document Checklist per applicant (primary, co-applicants, guarantors).",
		"<b>Documents:</b> each document-data record links itself to its checklist row; staff mark rows Verified.",
		"<b>Disbursement:</b> when staff mark a tranche Confirmed, the system creates the Commission Calculation; when the loan is "
		"fully disbursed it raises the ERPNext Sales Invoice with GST, the Commission Invoice, and emails the lender.",
		"<b>After that:</b> a monthly job prepares the Lender Payout Statement; reconciling it marks commissions Paid and drafts the "
		"Franchise Settlement; closing a loan early creates a Commission Clawback and a Credit Note."])
	story.append(PageBreak())
	if os.environ.get("DIAGRAMS_ONLY"):  # quick visual check of the drawn pages
		story = story[:-1]
		return SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm,
		                         bottomMargin=14 * mm).build(story, onFirstPage=footer("Database Diagram"),
		                                                     onLaterPages=footer("Database Diagram"))

	# relationship table
	rows = [["From DocType", "Field", "Type", "Points to", "Meaning"]]
	for dt in sorted(DOCS):
		for f in DOCS[dt]["fields"]:
			ft = f["fieldtype"]
			if ft not in LINK_TYPES:
				continue
			target = f["options"]
			if ft == "Dynamic Link":
				meaning, target = "One of the 7 document-data DocTypes, chosen by " + f["options"], "(" + f["options"] + ")"
			elif ft == "Table":
				meaning = f"Rows of {target} stored inside each {dt}"
			else:
				meaning = f"Many {dt} -> one {target}" + (" (required)" if f.get("reqd") else "")
				if target in EXTERNAL_NOTE:
					target += f"  [{EXTERNAL_NOTE[target]}]"
				if f.get("fetch_from"):
					meaning += f"; filled from {f['fetch_from']}"
			rows.append([E(dt), E(f["fieldname"]), ft, E(target), E(meaning)])
	story += [P("6. Every relationship", "h1"),
	          P(f"{len(rows) - 1} link fields across the module, read from the DocType JSON.", "small"), Spacer(1, 4),
	          table(rows, [44 * mm, 44 * mm, 22 * mm, 52 * mm, 107 * mm]), PageBreak()]

	rows = [["DocType", "Area", "Record name", "Fields", "Links out", "Links in"]]
	incoming = {}
	for dt in DOCS:
		for _fn, _ft, t in links(dt):
			incoming.setdefault(t, set()).add(dt)
	for g, dts in GROUPS.items():
		for dt in dts:
			rows.append([f"<b>{E(dt)}</b>", g, E(naming(dt)), str(len(data_fields(DOCS[dt]))), str(len(links(dt))),
			             E(", ".join(sorted(incoming.get(dt, []))) or "-")])
	story += [P("7. DocTypes at a glance", "h1"), table(rows, [48 * mm, 34 * mm, 46 * mm, 13 * mm, 15 * mm, 113 * mm])]

	doc = SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=14 * mm, rightMargin=14 * mm, topMargin=14 * mm,
	                        bottomMargin=14 * mm, title="DSA Loan Portal - Database Diagram", author="DSA Loan Portal")
	doc.build(story, onFirstPage=footer("Database Diagram"), onLaterPages=footer("Database Diagram"))
	print("Wrote", OUT)


if __name__ == "__main__":
	main()
