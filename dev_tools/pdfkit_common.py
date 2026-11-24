"""Shared look and helpers for the manager PDFs (Segoe UI so Rs and arrows render)."""
import json
import os
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

pdfmetrics.registerFont(TTFont("UI", "C:/Windows/Fonts/segoeui.ttf"))
pdfmetrics.registerFont(TTFont("UI-B", "C:/Windows/Fonts/segoeuib.ttf"))
pdfmetrics.registerFontFamily("UI", normal="UI", bold="UI-B", italic="UI", boldItalic="UI-B")

NAVY = colors.HexColor("#14365c")
TEAL = colors.HexColor("#0f7c74")
ROW = colors.HexColor("#f2f6fa")
GRID = colors.HexColor("#cfd8e3")
MUTED = colors.HexColor("#5b6b7c")
AMBER = colors.HexColor("#b45309")
AUTO_BG = colors.HexColor("#e6f4f1")
WARN_BG = colors.HexColor("#fff4e5")

GROUP_COLOURS = {
	"Lender masters": colors.HexColor("#1d4e89"),
	"DSA & people": colors.HexColor("#6b3fa0"),
	"Customer & application": colors.HexColor("#0f7c74"),
	"Documents": colors.HexColor("#8a5a00"),
	"Money": colors.HexColor("#a33b3b"),
	"Child table": colors.HexColor("#5b6b7c"),
}
GROUPS = {
	"Lender masters": ["Lender Type", "Lender", "Lender Branch", "Loan Product", "Loan Scheme", "Lender Document Rule",
	                   "Commission Slab Structure"],
	"DSA & people": ["Franchise", "DSA Branch", "Lender Login"],
	"Customer & application": ["Loan Lead", "Loan Customer", "Loan Application"],
	"Documents": ["Document Checklist", "Aadhaar Card Data", "PAN Card Data", "Address Proof Data", "Bank Statement Data",
	              "Salary Slip Data", "ITR Data", "Form 16 Data"],
	"Money": ["Loan Disbursement", "Commission Calculation", "Commission Invoice", "Lender Payout Statement",
	          "Commission Clawback", "Franchise Settlement"],
	"Child table": ["Co-Applicant", "Document Checklist Item"],
}
GROUP_OF = {dt: g for g, dts in GROUPS.items() for dt in dts}

S = {
	"title": ParagraphStyle("title", fontName="UI-B", fontSize=24, leading=30, textColor=NAVY),
	"sub": ParagraphStyle("sub", fontName="UI", fontSize=12, leading=17, textColor=MUTED),
	"h1": ParagraphStyle("h1", fontName="UI-B", fontSize=16, leading=21, textColor=NAVY, spaceBefore=4, spaceAfter=6),
	"h2": ParagraphStyle("h2", fontName="UI-B", fontSize=12, leading=16, textColor=TEAL, spaceBefore=8, spaceAfter=4),
	"h3": ParagraphStyle("h3", fontName="UI-B", fontSize=10, leading=13, textColor=NAVY, spaceBefore=6, spaceAfter=2),
	"body": ParagraphStyle("body", fontName="UI", fontSize=9.5, leading=13.5),
	"small": ParagraphStyle("small", fontName="UI", fontSize=8, leading=10.5, textColor=MUTED),
	"cell": ParagraphStyle("cell", fontName="UI", fontSize=8, leading=10.5),
	"hd": ParagraphStyle("hd", fontName="UI-B", fontSize=8, leading=10.5, textColor=colors.white),
	"code": ParagraphStyle("code", fontName="Courier", fontSize=7.5, leading=9.5),
	"bullet": ParagraphStyle("bullet", fontName="UI", fontSize=9.5, leading=13.5, leftIndent=12, bulletIndent=2),
}


def P(text, style="body"):
	return Paragraph(text, S[style])


def E(text):
	return escape(str(text))


def bullets(items, style="bullet"):
	return [Paragraph(t, S[style], bulletText="•") for t in items]


def table(rows, widths, header=True, zebra=True, extra=None):
	data = []
	for i, r in enumerate(rows):
		data.append([c if not isinstance(c, str) else P(c, "hd" if header and i == 0 else "cell") for c in r])
	t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
	style = [("GRID", (0, 0), (-1, -1), 0.4, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"),
	         ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
	         ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
	if header:
		style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
	if zebra:
		style.append(("ROWBACKGROUNDS", (0, 1 if header else 0), (-1, -1), [colors.white, ROW]))
	t.setStyle(TableStyle(style + (extra or [])))
	return t


def box(flowables, bg=AUTO_BG, border=TEAL, width=None):
	t = Table([[flowables]], colWidths=[width] if width else None)
	t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 0.8, border),
	                       ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
	                       ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
	return t


def auto(text):
	"""A teal 'AUTOMATIC' line."""
	return P(f'<font color="#0f7c74"><b>AUTOMATIC</b></font> {text}', "body")


def footer(title):
	def draw(c, d):
		w, h = d.pagesize
		c.saveState()
		c.setFont("UI", 7.5)
		c.setFillColor(MUTED)
		c.drawString(14 * mm, 8 * mm, f"DSA Loan Portal  |  {title}  |  Frappe / ERPNext v16")
		c.drawRightString(w - 14 * mm, 8 * mm, f"Page {d.page}")
		c.setStrokeColor(TEAL)
		c.setLineWidth(1.2)
		c.line(14 * mm, h - 10 * mm, w - 14 * mm, h - 10 * mm)
		c.restoreState()
	return draw


def load_doctypes(module_dir):
	docs = {}
	root = os.path.join(module_dir, "doctype")
	for folder in sorted(os.listdir(root)):
		path = os.path.join(root, folder, folder + ".json")
		if os.path.exists(path):
			with open(path, encoding="utf-8") as fh:
				d = json.load(fh)
			docs[d["name"]] = d
	return docs


def data_fields(doc):
	return [f for f in doc["fields"] if f["fieldtype"] not in ("Section Break", "Column Break", "Tab Break")]


def cover(title, subtitle, lines):
	out = [Spacer(1, 30 * mm), P(title, "title"), Spacer(1, 4), P(subtitle, "sub"), Spacer(1, 10 * mm)]
	out += bullets(lines)
	return out
