"""Fill the gaps in the imported master data that can be fixed from facts, not guesses.

1. Loan Product maximum tenure = longest maximum tenure among its own schemes (when the product has none).
2. "Plot + Construction" products for SBI and LIC HFL; their combo / composite schemes move there.
3. One lender-wide Active Commission Slab Structure per lender (the % is still entered per calculation).
4. DSA Branch PIN codes: the city's head post office PIN instead of 000000.
5. SBI home-loan document rules from SBI's published checklist (only documents the standard checklist
   does not already ask for).

Usage: cd ~/frappe/frappe-bench-v15/sites && ../env/bin/python ../apps/dsa_loan/scripts/fix_master_data.py dsaloan.localhost
Safe to run again.
"""
import sys

import frappe

EFFECTIVE = "2026-10-15"  # same effective date Atharva used for every product and scheme
GPO_PIN = {"Mumbai": "400001", "Thane": "400601", "Pune": "411001", "Nashik": "422001", "Nagpur": "440001"}
SBI_SRC = ("Source: SBI home loan pages and application form - https://homeloans.sbi.bank.in/products/view/regular-home-loan, "
           "https://homeloans.sbi.bank.in/products/view/home-loan-to-non-salaried-differential-offerings, "
           "https://sbi.bank.in/webfiles/uploads/files/1317730194453_HOME_LOANS_APPLICATION_FORM.pdf")
NON_SALARIED = ["Self Employed", "Business Owner", "Professional"]
# (rule name, applicant type, employment types, property type, category, document, mandatory)
SBI_RULES = [
	("SBI - Application Form and Photographs", "All", [None], None, "Other",
	 "Completed application Forms A to D, signed, with passport-size photographs", 1),
	("SBI - Balance Sheet and P&L", "Primary Applicant", NON_SALARIED, None, "Income",
	 "Balance Sheet and Profit & Loss account for the last 3 years", 1),
	("SBI - Business Address Proof", "Primary Applicant", NON_SALARIED, None, "Address", "Business address proof", 1),
	("SBI - Business Licence", "Primary Applicant", NON_SALARIED, None, "Employment", "Business licence or equivalent", 1),
	("SBI - TDS Certificate", "Primary Applicant", NON_SALARIED, None, "Income", "TDS certificate (Form 16A), if applicable", 0),
	("SBI - Professional Qualification", "Primary Applicant", ["Professional"], None, "Employment",
	 "Qualification certificate (for CAs, doctors and other professionals)", 1),
	("SBI - Sale Deed or Agreement", "Property Owner", [None], None, "Legal", "Sale deed or agreement for sale", 1),
	("SBI - Title Deed", "Property Owner", [None], None, "Legal", "Title deed", 1),
	("SBI - Encumbrance Certificate", "Property Owner", [None], None, "Legal", "Encumbrance certificate", 1),
	("SBI - Approved Building Plan", "Property Owner", [None], None, "Property", "Approved building plan", 1),
	("SBI - Allotment Letter", "Property Owner", [None], "Flat", "Property", "Allotment letter, if applicable", 0),
	("SBI - Occupancy Certificate", "Property Owner", [None], "Flat", "Property", "Occupancy certificate (ready-to-move property)", 0),
	("SBI - Builder Agreement", "Property Owner", [None], "Flat", "Legal",
	 "Builder's development agreement and construction permission (under-construction property)", 0),
	("SBI - Property Tax and Bills", "Property Owner", [None], None, "Property",
	 "Property tax receipts, maintenance and electricity bills", 1),
]


def run():
	out = {}

	# 1. product tenure from its schemes
	n = 0
	for p in frappe.get_all("Loan Product", {"maximum_tenure_months": ("in", [0, None])}, pluck="name"):
		top = max(frappe.get_all("Loan Scheme", {"loan_product": p}, pluck="maximum_tenure_months") or [0]) or 0
		if top:
			doc = frappe.get_doc("Loan Product", p)
			doc.maximum_tenure_months = top
			doc.save()
			n += 1
	out["products given a maximum tenure"] = n

	# 2. plot + construction
	n = 0
	for lender, name, scheme in (("SBI", "SBI Plot + Construction Loan", "SBI_COMBO_HOME_LOAN"),
	                             ("LIC_HFL", "LIC HFL Plot + Construction Loan", "LIC_HFL_COMPOSITE_PLOT")):
		code = f"{lender}_PLOT_CONSTRUCTION"
		if not frappe.db.exists("Loan Product", code):
			frappe.get_doc({"doctype": "Loan Product", "lender": lender, "product_name": name, "product_code": code,
			                "loan_category": "Plot + Construction", "is_active": 1, "effective_from": EFFECTIVE,
			                "product_description": "Purchase of a residential plot together with construction of a house on it."}).insert()
		doc = frappe.get_doc("Loan Scheme", scheme)
		if doc.loan_product != code:
			doc.loan_product = code
			doc.remarks = (doc.remarks or "") + "\n[Changed] Moved to the Plot + Construction product."
			doc.save()
			n += 1
	out["schemes moved to Plot + Construction"] = n

	# 3. commission slab per lender
	n = 0
	for lender, lender_name in frappe.get_all("Lender", fields=["name", "lender_name"], as_list=True):
		if not frappe.db.exists("Commission Slab Structure", {"lender": lender}):
			frappe.get_doc({"doctype": "Commission Slab Structure", "slab_name": f"{lender_name} - standard",
			                "lender": lender, "calculation_basis": "Disbursed Amount", "effective_from": EFFECTIVE,
			                "slab_status": "Active",
			                "remarks": "Lender-wide default. Enter the agreed commission % on each Commission Calculation."}).insert()
			n += 1
	out["commission slabs added"] = n

	# 4. branch pincodes
	n = 0
	for b in frappe.get_all("DSA Branch", {"pincode": ("in", ["000000", "", None])}, ["name", "city"]):
		if b.city in GPO_PIN:
			frappe.db.set_value("DSA Branch", b.name, "pincode", GPO_PIN[b.city])
			n += 1
	out["branch PIN codes fixed"] = n

	# 5. SBI rules
	n = 0
	for rule_name, who, employments, prop, category, document, mandatory in SBI_RULES:
		for emp in employments:
			title = f"{rule_name} ({emp})" if emp and len(employments) > 1 else rule_name
			if frappe.db.exists("Lender Document Rule", {"lender": "SBI", "rule_name": title}):
				continue
			frappe.get_doc({"doctype": "Lender Document Rule", "rule_name": title, "lender": "SBI",
			                "loan_product": "SBI_HOME_LOAN", "applicant_type": who, "employment_type": emp,
			                "property_type": prop, "document_category": category, "document_name": document,
			                "is_mandatory": mandatory, "verification_required": 1, "is_active": 1, "remarks": SBI_SRC}).insert()
			n += 1
	out["SBI document rules added"] = n

	for k, v in out.items():
		print(f"{k}: {v}")


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
