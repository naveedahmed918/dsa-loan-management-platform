"""Make Atharva's Lender Document Rules fit the standard Document Checklist.

1. Deactivate rules that only repeat one of the 13 standard checklist rows (note added in remarks).
2. Property / Legal rules for "All" applicants -> "Property Owner" (the primary applicant gets them,
   co-applicants and guarantors do not).
3. Self Employed, Business Owner and Professional are all self-employed borrowers: copy each lender's
   income / banking / business rules to whichever of the three was missing.

Usage: cd ~/frappe/frappe-bench-v15/sites && ../env/bin/python ../apps/dsa_loan/scripts/fix_atharva_rules.py dsaloan.localhost
Safe to run again: already-fixed rules are skipped.
"""
import sys

import frappe

DUPLICATES = {
	"LDR-00001": "PAN Card", "LDR-00004": "PAN Card",
	"LDR-00002": "Aadhaar Card / PAN Card", "LDR-00005": "Aadhaar Card / PAN Card", "LDR-00007": "Aadhaar Card / PAN Card",
	"LDR-00003": "Address Proof", "LDR-00006": "Address Proof", "LDR-00008": "Address Proof",
	"LDR-00009": "Salary Slip – Month 1/2/3", "LDR-00012": "Salary Slip – Month 1/2/3",
	"LDR-00015": "Salary Slip – Month 1/2/3", "LDR-00018": "Salary Slip – Month 1/2/3",
	"LDR-00010": "Bank Statement – Last 6 Months", "LDR-00014": "Bank Statement – Last 6 Months",
	"LDR-00017": "Bank Statement – Last 6 Months", "LDR-00021": "Bank Statement – Last 6 Months",
	"LDR-00023": "Bank Statement – Last 6 Months",
	"LDR-00011": "Form 16 – Year 1/2/3 and ITR – Year 1/2/3", "LDR-00013": "Form 16 – Year 1/2/3 and ITR – Year 1/2/3",
	"LDR-00016": "Form 16 – Year 1/2/3", "LDR-00019": "Form 16 – Year 1/2/3",
	"LDR-00022": "ITR – Year 1/2/3", "LDR-00024": "ITR – Year 1/2/3", "LDR-00027": "ITR – Year 1/2/3",
	"LDR-00033": "ITR – Year 1/2/3", "LDR-00039": "ITR – Year 1/2/3",
}
SELF_EMPLOYED_PAIR = ("Self Employed", "Business Owner")
SELF_EMPLOYED_ALL = ("Self Employed", "Business Owner", "Professional")
COPY_FIELDS = ["rule_name", "lender", "loan_product", "loan_scheme", "applicant_type", "property_type", "document_category",
               "document_name", "is_mandatory", "verification_required", "accepted_format", "validity_period_days", "is_active"]


def note(doc, text):
	doc.remarks = ((doc.remarks or "").rstrip() + "\n" + text).strip()


def run():
	off = owner = copies = 0
	for name, covered_by in DUPLICATES.items():
		doc = frappe.get_doc("Lender Document Rule", name)
		if doc.is_active:
			doc.is_active = 0
			note(doc, f"[Inactive] Already covered by the standard checklist row: {covered_by}.")
			doc.save()
			off += 1

	for doc in frappe.get_all("Lender Document Rule", {"applicant_type": "All", "document_category": ("in", ["Property", "Legal"])}, pluck="name"):
		doc = frappe.get_doc("Lender Document Rule", doc)
		doc.applicant_type = "Property Owner"
		note(doc, "[Changed] Applicant Type All -> Property Owner: property papers come from the owner, not every co-applicant.")
		doc.save()
		owner += 1

	active = frappe.get_all("Lender Document Rule", {"is_active": 1, "employment_type": ("in", SELF_EMPLOYED_ALL)},
	                        ["name"] + COPY_FIELDS + ["employment_type"], order_by="name")
	existing = {(r.lender, r.loan_product, r.employment_type, r.document_name) for r in active}
	todo = []
	for r in active:
		if r.employment_type == "Professional" or "(" in (r.rule_name or ""):
			continue  # professional-only rules (e.g. qualification) and earlier copies are not copied again
		targets = [e for e in SELF_EMPLOYED_ALL if e != r.employment_type]
		todo += [(r, e) for e in targets]
	for r, other in todo:
		if (r.lender, r.loan_product, other, r.document_name) in existing:
			continue
		data = {f: r.get(f) for f in COPY_FIELDS}
		data.update(doctype="Lender Document Rule", employment_type=other,
		            rule_name=f"{r.rule_name} ({other})"[:140],
		            remarks=f"Copy of {r.name} for {other} applicants; same documents apply to both kinds of self-employed borrower.")
		frappe.get_doc(data).insert()
		existing.add((r.lender, r.loan_product, other, r.document_name))
		copies += 1
	print(f"deactivated duplicates: {off}\nproperty/legal rules -> Property Owner: {owner}\nSelf Employed / Business Owner copies added: {copies}")


frappe.init(site=sys.argv[1] if len(sys.argv) > 1 else "dsaloan.localhost", sites_path=".")
frappe.connect()
frappe.set_user("Administrator")
try:
	run()
	frappe.db.commit()
	print("committed")
except Exception:
	frappe.db.rollback()
	raise
finally:
	frappe.destroy()
