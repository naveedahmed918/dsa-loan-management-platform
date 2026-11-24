"""Build the field-spec PDF from the generated DocType JSON (the source of truth).

Usage: python build_field_pdf.py <dsa_loan_module_dir> <output.pdf>
"""
import json
import os
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

MOD, OUT = sys.argv[1], sys.argv[2]

NAVY = colors.HexColor("#14365c")
TEAL = colors.HexColor("#0f7c74")
ROW = colors.HexColor("#f2f6fa")
GRID = colors.HexColor("#cfd8e3")
MUTED = colors.HexColor("#5b6b7c")

PARTS = [
    ("Part A: Masters", ["Lender Type", "Lender", "Lender Branch", "Loan Product", "Loan Scheme",
                         "Commission Slab Structure", "Lender Document Rule", "DSA Branch", "Franchise"]),
    ("Part B: Loan Work", ["Loan Lead", "Loan Customer", "Loan Application", "Lender Login",
                           "Document Checklist", "Loan Disbursement"]),
    ("Part C: Commission & Settlement", ["Commission Calculation", "Commission Invoice", "Commission Clawback",
                                         "Lender Payout Statement", "Franchise Settlement"]),
    ("Part D: Document Data", ["Aadhaar Card Data", "PAN Card Data", "Address Proof Data", "Bank Statement Data",
                               "Salary Slip Data", "ITR Data", "Form 16 Data"]),
]
PURPOSE = {
    "Lender Type": "Classifies institutions: Public Sector Bank, Private Bank, HFC, NBFC.",
    "Lender": "Main lender master.",
    "Lender Branch": "Lender office and processing locations.",
    "Loan Product": "Loan products offered by the lender, with amount, tenure, rate and fee limits.",
    "Loan Scheme": "Lender schemes and eligibility rules (age, income, credit score, LTV, FOIR).",
    "Commission Slab Structure": "Commission %, basis, GST and TDS rates and clawback rule per lender/product/scheme and period.",
    "Lender Document Rule": "Documents a lender requires per applicant type, employment and property type.",
    "DSA Branch": "DSA operating branches (company or franchise owned).",
    "Franchise": "Franchise ownership, agreement and settlement percentage.",
    "Loan Lead": "Prospective home-loan customers.",
    "Loan Customer": "Reusable customer / applicant information and KYC.",
    "Loan Application": "Main home-loan application: lender, requirement, co-applicants, sanction and workflow.",
    "Document Checklist": "One per applicant per application; a table of documents, each linked to its extracted data.",
    "Aadhaar Card Data": "Data read from the Aadhaar card (last 4 digits only).",
    "PAN Card Data": "Data read from the PAN card.",
    "Address Proof Data": "Data read from an address proof (passport, voter ID, utility bill...).",
    "Bank Statement Data": "Summary of the last 6 months' bank statement.",
    "Salary Slip Data": "One salary slip (3 needed, different months).",
    "ITR Data": "One income tax return (3 needed, different assessment years).",
    "Form 16 Data": "One Form 16 (3 needed); PAN must match the PAN card.",
    "Lender Login": "Lender portal access and the employee authorised to use it (no passwords).",
    "Loan Disbursement": "Full, part and final disbursements against a sanctioned application.",
    "Commission Calculation": "Commission earned on one confirmed disbursement, with GST, TDS and net amount.",
    "Commission Invoice": "Commission invoice raised to a lender; links the ERPNext Sales Invoice.",
    "Commission Clawback": "Commission reversed or recovered by the lender.",
    "Lender Payout Statement": "Reconciles a lender's payout statement for a period with calculated commission.",
    "Franchise Settlement": "Franchise share of commission received in a period, less deductions.",
}
DECISIONS = [
    ("Source", "Fields follow DSA_Home_Loan_Blueprint.pdf (20 parent DocTypes)."),
    ("Child tables", "Co-Applicant (inside Loan Application) and Document Checklist Item (inside Document Checklist). The Blueprint's Commission Slab Detail, Commission Invoice Item, Lender Payout Item and Franchise Settlement Item tables are left out."),
    ("Document checklist", "One checklist per applicant with 13 standard rows (Aadhaar, PAN, address proof, 6-month bank statement, 3 salary slips, 3 ITRs, 3 Form 16s) plus extra rows from Lender Document Rules. Each row links (Dynamic Link) to a record in one of 7 extracted-data DocTypes."),
    ("Lender flow", "One lender per Loan Application: lender, lender application number and sanction details are on the application. Loan Disbursement links to the application."),
    ("Lender Login", "Lender portal access tracking (portal, username, assigned employee). Never stores passwords."),
    ("Employment / Property Type", "Select fields, because those master DocTypes do not exist on the site."),
    ("Field names", "Lower-case snake_case (pan, gstin, rbi_registration_number, aadhaar_number) instead of the Blueprint's PAN / GSTIN / RBI_ / Aadhaar_ spelling."),
    ("Check fields", "Blueprint marks some Check fields required; a checkbox always has a value, so they have defaults instead of a required flag."),
    ("Naming", "Masters are named by their code; transactions use LEAD-, CUST-, LAPP-, DOC-, LLOG-, DISB-, COMM-, CIN-, CLB-, LPS-, FST- with year and number."),
    ("Commission rate", "The slab holds the Commission %, GST and TDS rates; a Commission Calculation is created automatically when a disbursement is Confirmed and copies them (still editable per loan)."),
]
RULES = [
    "Lead: Convert to Customer creates or reuses the Loan Customer and opens a new Loan Application; saving it marks the lead Converted. A lead converts only once.",
    "Loan Application: lender, branch, product and scheme must belong together; EMI is calculated; Sanctioned needs amount and date, Rejected needs a reason.",
    "Saving a Loan Application creates one Document Checklist per applicant with the 13 standard rows (salary slips and Form 16 marked Not Applicable for non-salaried) plus rows from matching Lender Document Rules.",
    "Extracted data links itself to the first empty matching row and marks it Received. Aadhaar and account numbers: last 4 digits only. Bank statement must cover 6 months to be Verified; salary months, ITR and Form 16 years must differ; Form 16 PAN must match the PAN card; a row cannot be Verified without its extracted data.",
    "Disbursement: only on a Sanctioned application; numbers unique per application; total cannot exceed the sanctioned amount; a Confirmed amount is locked.",
    "Confirmed disbursements move the application to Partially Disbursed or Disbursed.",
    "Commission Calculation: one per confirmed disbursement; the Active slab is picked by lender, product, scheme and date; GST, TDS and net are calculated.",
    "Commission Invoice: total GST = CGST + SGST or IGST; invoice total = taxable + GST; invoice number unique per company.",
    "Payout Statement: expected commission comes from the lender's calculations in the period; Matched marks them Paid, Partially Matched marks them Partially Paid.",
    "Clawback: amount and percentage are derived from each other, cannot exceed the commission; recovery status follows the recovered amount.",
    "Franchise Settlement: share = settlement percentage of commission received in the period; periods cannot overlap for a franchise.",
    "Sensitive fields (PAN, Aadhaar, income, document numbers, account reference) are on permission level 1.",
]

ss = {
    "title": ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=26, leading=31, textColor=NAVY),
    "sub": ParagraphStyle("s", fontName="Helvetica", fontSize=12, leading=16, textColor=MUTED),
    "part": ParagraphStyle("p", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceAfter=6),
    "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=NAVY, spaceBefore=8),
    "meta": ParagraphStyle("m", fontName="Helvetica", fontSize=8.5, leading=11, textColor=MUTED, spaceAfter=4),
    "body": ParagraphStyle("b", fontName="Helvetica", fontSize=9.5, leading=13),
    "cell": ParagraphStyle("c", fontName="Helvetica", fontSize=7.6, leading=9.4, alignment=TA_LEFT),
    "code": ParagraphStyle("cd", fontName="Courier", fontSize=7.6, leading=9.4),
    "hd": ParagraphStyle("hd", fontName="Helvetica-Bold", fontSize=7.8, leading=9.6, textColor=colors.white),
    "sec": ParagraphStyle("sec", fontName="Helvetica-Bold", fontSize=7.6, leading=9.4, textColor=TEAL),
}


def P(t, s="cell"):
    return Paragraph(t, ss[s])


def load():
    docs = {}
    root = os.path.join(MOD, "doctype")
    for d in os.listdir(root):
        p = os.path.join(root, d, d + ".json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                j = json.load(fh)
            docs[j["name"]] = j
    return docs


def cond(expr):
    return (expr.replace("eval:doc.", "").replace("!=", " is not ").replace("==", " = ")
            .replace("'", ""))


def notes(f):
    n = []
    if f.get("read_only"): n.append("Read-only")
    if f.get("fetch_from"): n.append("Fetch: " + f["fetch_from"])
    if f.get("unique"): n.append("Unique")
    if f.get("default"): n.append("Default: " + f["default"])
    if f.get("permlevel"): n.append("Restricted (permlevel 1)")
    if f.get("mandatory_depends_on"):
        n.append("Required when " + cond(f["mandatory_depends_on"]))
    elif f.get("depends_on"):
        n.append("Shown when " + cond(f["depends_on"]))
    if f.get("description"): n.append(f["description"])
    return escape("; ".join(n))


def options(f):
    o = f.get("options") or ""
    if f["fieldtype"] == "Select":
        return escape(", ".join(x for x in o.split("\n") if x))
    if f["fieldtype"] in ("Link", "Table"):
        return "<b>" + escape(o) + "</b>"
    return escape(o)


def field_table(doc):
    widths = [9 * mm, 47 * mm, 42 * mm, 20 * mm, 75 * mm, 10 * mm, 66 * mm]
    rows = [[P(h, "hd") for h in ["#", "Fieldname", "Label", "Type", "Options / Link", "Req", "Notes"]]]
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    i = 0
    for f in doc["fields"]:
        t = f["fieldtype"]
        if t == "Column Break":
            continue
        r = len(rows)
        if t == "Section Break":
            if f.get("label"):
                rows.append([P(escape(f["label"]).upper(), "sec"), "", "", "", "", "", ""])
                style += [("SPAN", (0, r), (-1, r)), ("BACKGROUND", (0, r), (-1, r), colors.HexColor("#e3f1ef"))]
            continue
        i += 1
        rows.append([P(str(i)), P(escape(f["fieldname"]), "code"), P(escape(f.get("label", ""))), P(t),
                     P(options(f)), P("<b>Y</b>" if f.get("reqd") else (
                         "C" if f.get("mandatory_depends_on") else "")), P(notes(f))])
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, r), (-1, r), ROW))
    tbl = Table(rows, colWidths=widths, repeatRows=1)
    tbl.setStyle(TableStyle(style))
    return tbl


def doc_meta(doc):
    bits = []
    if doc.get("istable"):
        bits.append("Child table")
    else:
        an = doc.get("autoname", "")
        if an.startswith("naming_series"):
            series = next(f["options"] for f in doc["fields"] if f["fieldname"] == "naming_series")
            bits.append("Naming series: " + series)
        elif an.startswith("field:"):
            bits.append("Named by field: " + an[6:])
        else:
            bits.append("Naming: " + an)
        if doc.get("is_submittable"): bits.append("Submittable")
        if doc.get("track_changes"): bits.append("Track changes")
        if doc.get("title_field"): bits.append("Title: " + doc["title_field"])
    n = sum(1 for f in doc["fields"] if f["fieldtype"] not in ("Section Break", "Column Break"))
    bits.append(f"{n} fields")
    return escape("  |  ".join(bits))


def section(docs, name, num=None, child_of=None):
    d = docs[name]
    head = f"{num}. {name}" if num else f"Child table: {name}"
    items = [P(escape(head), "h")]
    if child_of:
        items.append(P(escape(f"Used in {child_of}. ") + doc_meta(d), "meta"))
    else:
        items.append(P(escape(PURPOSE.get(name, "")) + "<br/>" + doc_meta(d), "meta"))
    # Keep the heading with at least the start of its table; long tables then flow across pages.
    return [KeepTogether(items + [Spacer(1, 30 * mm)]), Spacer(1, -30 * mm), field_table(d), Spacer(1, 8)]


def on_page(c, d):
    c.saveState()
    w, h = landscape(A4)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawString(14 * mm, 8 * mm, "DSA Home Loan System | Consolidated DocType Field Specification | Frappe / ERPNext v16")
    c.drawRightString(w - 14 * mm, 8 * mm, f"Page {d.page}")
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.2)
    c.line(14 * mm, h - 10 * mm, w - 14 * mm, h - 10 * mm)
    c.restoreState()


def main():
    docs = load()
    children = {}
    for n, d in docs.items():
        for f in d["fields"]:
            if f["fieldtype"] == "Table":
                children.setdefault(n, []).append(f["options"])
    total_fields = sum(sum(1 for f in d["fields"] if f["fieldtype"] not in ("Section Break", "Column Break"))
                       for d in docs.values())
    n_child = sum(1 for d in docs.values() if d.get("istable"))

    story = [Spacer(1, 30 * mm), P("DSA Home Loan System", "title"),
             P("Consolidated DocType Field Specification", "title"), Spacer(1, 6),
             P("Frappe / ERPNext v16. Final DocTypes of the dsa_loan app (DSA Loan Portal module), as installed on dsaloan.localhost.", "sub"),
             Spacer(1, 10 * mm)]
    big = ParagraphStyle("big", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=NAVY)
    stat_vals = [(len(docs) - n_child, "Main DocTypes"), (n_child, "Child tables"), (total_fields, "Fields"),
                 (3, "Modules")]
    stats = Table([[[Paragraph(str(v), big), P(lbl, "body")] for v, lbl in stat_vals]], colWidths=[60 * mm] * 4)
    stats.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e8f3f1")),
                               ("BOX", (0, 0), (-1, -1), 0.6, TEAL), ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.white),
                               ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                               ("LEFTPADDING", (0, 0), (-1, -1), 12)]))
    story += [stats, Spacer(1, 10 * mm),
              P("<b>Legend.</b> Req: <b>Y</b> = mandatory, <b>C</b> = mandatory only under a condition (see Notes). "
                "Read-only fields are filled by fetch or server code. Restricted fields sit on permission level 1. "
                "Frappe's standard fields (name, owner, creation, modified, docstatus) are not listed.", "body"),
              PageBreak()]

    # Overview
    story.append(P("DocType Overview", "part"))
    rows = [[P(h, "hd") for h in ["#", "DocType", "Module", "Purpose", "Child tables"]]]
    k = 0
    for part, names in PARTS:
        for n in names:
            k += 1
            rows.append([P(str(k)), P("<b>" + escape(n) + "</b>"), P(part.split(": ")[1]),
                         P(escape(PURPOSE[n])), P(escape(", ".join(children.get(n, []))))])
    ov = Table(rows, colWidths=[9 * mm, 50 * mm, 48 * mm, 115 * mm, 47 * mm], repeatRows=1)
    ov.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW])]))
    story += [ov, PageBreak()]

    # Decisions
    story.append(P("Design Decisions", "part"))
    story.append(P("How the Blueprint was applied in the app.", "meta"))
    rows = [[P("Topic", "hd"), P("Decision", "hd")]] + [[P("<b>" + escape(a) + "</b>"), P(escape(b))] for a, b in DECISIONS]
    dt = Table(rows, colWidths=[60 * mm, 209 * mm], repeatRows=1)
    dt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ROW]),
                            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story += [dt, Spacer(1, 6),
              P("<b>Not stored:</b> passwords or portal secrets, a separate accounting ledger (ERPNext's General Ledger "
                "is used), and fields not listed in the Blueprint.", "body"),
              PageBreak()]

    num = 0
    for part, names in PARTS:
        story.append(P(escape(part), "part"))
        for n in names:
            num += 1
            story += section(docs, n, num)
            for ch in children.get(n, []):
                story += section(docs, ch, child_of=n)
        story.append(PageBreak())

    story.append(P("Server-side Rules to Implement", "part"))
    for i, r in enumerate(RULES, 1):
        story.append(P(f"<b>{i}.</b> " + escape(r), "body"))
        story.append(Spacer(1, 3))

    doc = SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=14 * mm, rightMargin=14 * mm,
                            topMargin=14 * mm, bottomMargin=14 * mm,
                            title="DSA Home Loan System - Consolidated Field Specification",
                            author="DSA Home Loan System")
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
