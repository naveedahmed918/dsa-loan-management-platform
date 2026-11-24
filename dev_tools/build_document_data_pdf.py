"""PDF of the document checklist and the extracted-data fields for each document.

Usage: python build_document_data_pdf.py <dsa_loan_portal module dir> <output.pdf>
Reuses the table builders from build_field_pdf.py.
"""
import os
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(__file__))
MOD, OUT = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], MOD, OUT]  # build_field_pdf reads these at import
import build_field_pdf as B  # noqa: E402

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4, landscape  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402

P = B.P

DOCUMENTS = [
    ("Aadhaar Card Data", "Aadhaar Card", "1",
     "Identity and address. Only the last 4 Aadhaar digits are stored."),
    ("PAN Card Data", "PAN Card", "1",
     "Identity and tax ID. PAN format is checked; the Form 16 PAN must match it."),
    ("Address Proof Data", "Address Proof", "1",
     "Passport, voter ID, driving licence, utility bill or rent agreement."),
    ("Bank Statement Data", "Bank Statement – Last 6 Months", "1",
     "Months covered are calculated from the period; at least 6 are needed to mark it Verified."),
    ("Salary Slip Data", "Salary Slip – Month 1 / 2 / 3", "3",
     "Salaried applicants only. One record per month; the 3 months must be different."),
    ("ITR Data", "ITR – Year 1 / 2 / 3", "3",
     "One record per assessment year; the 3 years must be different."),
    ("Form 16 Data", "Form 16 – Year 1 / 2 / 3", "3",
     "Salaried applicants only. One per assessment year; PAN must match the PAN card; "
     "taxable income is compared with the ITR for the same year."),
]

COMMON = [
    ("document_checklist", "Link → Document Checklist", "Y", "The applicant's checklist this record belongs to"),
    ("loan_application", "Link → Loan Application", "", "Filled from the checklist"),
    ("applicant", "Link → Loan Customer", "", "Filled from the checklist"),
    ("source_file", "Attach", "", "The uploaded document (copied to the checklist row)"),
    ("extraction_status", "Select", "Y", "Pending · Extracted · Verified · Failed"),
    ("extracted_on", "Datetime", "", "Set when status becomes Extracted or Verified"),
]


def styled(rows, widths, header=True):
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), B.NAVY), ("GRID", (0, 0), (-1, -1), 0.4, B.GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, B.ROW]),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def on_page(c, d):
    c.saveState()
    w, h = landscape(A4)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(B.MUTED)
    c.drawString(14 * mm, 8 * mm, "DSA Home Loan System | Document Checklist & Extracted Data Fields | Frappe / ERPNext v16")
    c.drawRightString(w - 14 * mm, 8 * mm, f"Page {d.page}")
    c.setStrokeColor(B.TEAL)
    c.setLineWidth(1.2)
    c.line(14 * mm, h - 10 * mm, w - 14 * mm, h - 10 * mm)
    c.restoreState()


def main():
    docs = B.load()
    count = lambda n: sum(1 for f in docs[n]["fields"] if f["fieldtype"] not in ("Section Break", "Column Break"))

    story = [Spacer(1, 25 * mm), P("DSA Home Loan System", "title"),
             P("Document Checklist &amp; Extracted Data Fields", "title"), Spacer(1, 6),
             P("The fields captured for each of the 7 documents verified per applicant, and how they link "
               "to the Document Checklist.", "sub"), Spacer(1, 8 * mm)]

    # How it works
    story.append(P("How it works", "h"))
    for line in [
        "Saving a <b>Loan Application</b> creates one <b>Document Checklist</b> per applicant (primary applicant and "
        "each co-applicant / guarantor).",
        "Each checklist has a <b>Documents</b> table with <b>13 standard rows</b> for a salaried applicant, plus rows "
        "from matching Lender Document Rules. Salary slips and Form 16 are <b>Not Applicable</b> for non-salaried applicants.",
        "Each row points to a record in one of the <b>7 extracted-data DocTypes</b> below (Extracted Data Type + "
        "Extracted Data). Saving an extracted record links it to the first empty matching row and marks it <b>Received</b>.",
        "A row can only be marked <b>Verified</b> once its extracted record is linked.",
    ]:
        story += [P("• " + line, "body"), Spacer(1, 3)]
    story.append(Spacer(1, 4 * mm))

    rows = [[P(h, "hd") for h in ["#", "Document (checklist row)", "Rows", "Extracted-data DocType", "Fields", "Notes"]]]
    for i, (dt, row_name, n_rows, note) in enumerate(DOCUMENTS, 1):
        rows.append([P(str(i)), P("<b>" + escape(row_name) + "</b>"), P(n_rows), P(escape(dt)), P(str(count(dt))), P(escape(note))])
    rows.append([P(""), P("<b>Total rows per salaried applicant</b>"), P("<b>13</b>"), P(""), P(""), P("")])
    story += [styled(rows, [8 * mm, 62 * mm, 14 * mm, 45 * mm, 14 * mm, 126 * mm]), PageBreak()]

    # Checklist structure
    story.append(P("Part 1: Document Checklist", "part"))
    story += B.section(docs, "Document Checklist", 1)
    story += B.section(docs, "Document Checklist Item", child_of="Document Checklist")
    story.append(PageBreak())

    # Common fields
    story.append(P("Part 2: Extracted Data per Document", "part"))
    story.append(P("Common fields", "h"))
    story.append(P("The first 6 fields of every extracted-data DocType are the same:", "meta"))
    rows = [[P(h, "hd") for h in ["Fieldname", "Type", "Req", "Purpose"]]]
    rows += [[P(escape(a), "code"), P(escape(b)), P("<b>Y</b>" if c else ""), P(escape(d))] for a, b, c, d in COMMON]
    story += [styled(rows, [55 * mm, 60 * mm, 12 * mm, 142 * mm]), Spacer(1, 4 * mm)]
    story.append(P("Each table below lists all fields; the document-specific ones are under <b>EXTRACTED DATA</b>.", "body"))
    story.append(PageBreak())

    for i, (dt, _row, _n, _note) in enumerate(DOCUMENTS, 2):
        B.PURPOSE.setdefault(dt, _note)
        story += B.section(docs, dt, i)

    doc = SimpleDocTemplate(OUT, pagesize=landscape(A4), leftMargin=14 * mm, rightMargin=14 * mm,
                            topMargin=14 * mm, bottomMargin=14 * mm,
                            title="DSA Home Loan System - Document Checklist & Extracted Data Fields",
                            author="DSA Home Loan System")
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
