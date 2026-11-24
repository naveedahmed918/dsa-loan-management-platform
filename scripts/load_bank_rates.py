"""Load each bank's published home-loan rates, fees and limits (as read on 2026-11-24) and sample commission %.

Policy: a bank's home-loan rate band is used for its housing products (home loan, balance transfer,
home improvement, plot, plot + construction) unless the bank publishes a separate figure; Loan Against
Property gets the bank's LAP figure, or stays blank when none is published. Nothing is invented.

Usage: cd ~/frappe/frappe-bench-v15/sites && ../env/bin/python ../apps/dsa_loan/scripts/load_bank_rates.py dsaloan.localhost
Safe to run again (values are overwritten with the same figures).
"""
import sys

import frappe

TODAY = "2026-11-24"
TENURE_DEFAULT_FOR = ["HOME_LOAN", "BALANCE_TRANSFER", "PLOT_CONSTRUCTION"]  # where banks state "up to 30 years"
HOUSING = ["HOME_LOAN", "BALANCE_TRANSFER", "HOME_IMPROVEMENT", "PLOT_PURCHASE", "PLOT_CONSTRUCTION"]

# product-level figures per bank
BANKS = {
	"SBI": dict(
		rates=(7.50, 8.80), lap=(9.20, 10.75), as_on="2026-10-15", tenure=360,
		fee=(0.35, 5000, 15000), lap_fee=(1.0, 0, 50000),
		src="https://homeloans.sbi.bank.in/downloads/HL_ROI.jpg ; fees: https://homeloans.sbi.bank.in/downloads/Processing-Fee-Card-Rates.pdf",
		note="EBLR-linked (EBLR 8.15%), w.e.f. 15.10.2026. Non-salaried fee max Rs 18,000. +0.10% for non-salaried with CIBIL < 825.",
		skip_rates=["PLOT_PURCHASE"],  # SBI Realty (plot) is not on the rate card
	),
	"HDFC": dict(
		rates=(8.00, 13.45), lap=None, as_on=TODAY, tenure=360, fee=(0.50, 4000, 0),
		src="https://www.hdfc.bank.in/home-loan/interest-rates-and-charges",
		note="Repo-linked: Repo + 2.50% to Repo + 7.95%, worked out at repo 5.50% (not read directly; HDFC blocks automated reading). "
		     "Fee: up to 0.50% or Rs 4,000 whichever is higher, + taxes.",
	),
	"ICICI": dict(
		rates=(8.75, 10.05), lap=(10.85, 12.50), as_on="2026-11-01", tenure=0, fee=(0.50, 0, 0),
		src="https://www.icici.bank.in/personal-banking/loans/home-loan/interest-rates",
		note="Nov 2026 card, valid till 30.11.2026. Salaried 8.75-9.90%, self-employed 8.75-10.05%. "
		     "Fee 0.5% + taxes (service-charges page says up to 2%).",
	),
	"AXIS": dict(
		rates=(8.00, 9.10), lap=None, as_on="2026-11-01", tenure=360, fee=(1.0, 10000, 0), amount=(300000, 100000000),
		src="https://www.axis.bank.in/loans/home-loan/interest-rates-charges",
		note="Repo + 2.50% to + 3.60%: 8.00-8.85% CIBIL 751+, 8.20-9.10% below 750. Fee up to 1% or Rs 10,000 whichever is higher + GST. "
		     "Read from a summary of the page - verify.",
	),
	"LIC_HFL": dict(
		rates=(7.15, 10.25), lap=(8.75, 11.20), as_on="2026-09-30", tenure=0, fee=None,
		src="https://cdn.lichousing.com/2026/10/Interest-Rate-Range-for-Contracted-loans-for-Q2FY27.pdf",
		note="Range of loans actually contracted in Q2 FY2026-27 (not a card rate). LHPLR-linked. Processing fee not published.",
		per_product={"PLOT_PURCHASE": (7.15, 9.90)},  # Griha Bhoomi
		skip_rates=["HOME_IMPROVEMENT"],
	),
	"BOB": dict(
		rates=(7.40, 9.15), lap=None, as_on=TODAY, tenure=360, fee=(0.50, 8500, 15000), amount=(0, 200000000),
		src="https://bankofbaroda.bank.in/loans/home-loan/baroda-home-loan",
		note="BRLLR-linked (BRLLR - 0.75% to + 1.00%); +0.05% without credit insurance. Fee 0.50% (min 8,500, max 15,000) up to 50 lakh; "
		     "0.25% (min 8,500, max 25,000) above 50 lakh; takeover flat Rs 8,500; charges excl. GST. Max loan Rs 20 Cr (Mumbai).",
		fixed_fee={"BALANCE_TRANSFER": 8500},
	),
}

# scheme-level overrides: rates, ltv, age
SCHEMES = {
	"SBI_MAXGAIN": dict(rates=(8.00, 9.30)),
	"SBI_HOME_EQUITY": dict(rates=(9.20, 10.75)),
	"AXIS_ASHA_HOME": dict(rates=(10.00, 12.25)),
	"LIC_HFL_GRIHA_SUVIDHA": dict(rates=(7.40, 10.10)),
}
AGE = {"SBI": (18, 70), "BOB": (21, 70)}
LTV = {"BOB": 90}  # BOB publishes the RBI slabs (90/80/75); the app applies the slab by loan size

# SAMPLE commission % - replace with the agreed payout per bank
COMMISSION = {"SBI": 0.40, "HDFC": 0.55, "ICICI": 0.50, "AXIS": 0.60, "LIC_HFL": 0.65, "BOB": 0.45}


def run():
	counts = dict(products=0, schemes=0, slabs=0)
	for lender, b in BANKS.items():
		for p in frappe.get_all("Loan Product", {"lender": lender}, ["name", "loan_category"]):
			suffix = p.name[len(lender) + 1:]
			doc = frappe.get_doc("Loan Product", p.name)
			if suffix == "LAP":
				rates, fee = b.get("lap"), b.get("lap_fee") or b.get("fee")
			elif suffix in HOUSING and suffix not in b.get("skip_rates", []):
				rates, fee = b.get("per_product", {}).get(suffix, b["rates"]), b.get("fee")
			else:
				rates, fee = None, b.get("fee")
			if rates:
				doc.minimum_interest_rate, doc.maximum_interest_rate = rates
				doc.interest_type = "Floating"
			doc.repayment_type = "EMI"
			if suffix in b.get("fixed_fee", {}):
				doc.processing_fee_type, doc.processing_fee = "Fixed", b["fixed_fee"][suffix]
				doc.minimum_processing_fee = doc.maximum_processing_fee = 0
			elif fee:
				doc.processing_fee_type, doc.processing_fee = "Percentage", fee[0]
				doc.minimum_processing_fee, doc.maximum_processing_fee = fee[1], fee[2]
			if b.get("tenure") and not doc.maximum_tenure_months and suffix in TENURE_DEFAULT_FOR:
				doc.maximum_tenure_months = b["tenure"]
			if b.get("amount"):
				doc.minimum_loan_amount, doc.maximum_loan_amount = b["amount"]
			doc.rates_as_on, doc.rate_source = b["as_on"], b["src"][:140]
			base = (doc.product_description or "").split("\n[Rates]")[0]
			doc.product_description = base + "\n[Rates] " + b["note"] + (" Source: " + b["src"] if len(b["src"]) > 140 else "")
			doc.save()
			counts["products"] += 1

	for s in frappe.get_all("Loan Scheme", fields=["name", "lender", "loan_product"]):
		doc = frappe.get_doc("Loan Scheme", s.name)
		prod = frappe.db.get_value("Loan Product", s.loan_product, ["minimum_interest_rate", "maximum_interest_rate"], as_dict=True)
		rates = SCHEMES.get(s.name, {}).get("rates") or (prod.minimum_interest_rate, prod.maximum_interest_rate)
		if rates and rates[1]:
			doc.minimum_interest_rate, doc.maximum_interest_rate = rates
		if s.lender in AGE:
			doc.minimum_age, doc.maximum_age = AGE[s.lender]
		if s.lender in LTV:
			doc.maximum_ltv = LTV[s.lender]
		doc.save()
		counts["schemes"] += 1

	for slab in frappe.get_all("Commission Slab Structure", fields=["name", "lender"]):
		if slab.lender in COMMISSION:
			doc = frappe.get_doc("Commission Slab Structure", slab.name)
			doc.commission_percentage = COMMISSION[slab.lender]
			doc.gst_rate, doc.tds_rate = 18, 2  # GST on DSA services; TDS u/s 194H
			doc.clawback_window_months, doc.clawback_percentage = 6, 100
			doc.remarks = ("Lender-wide default. SAMPLE commission % and SAMPLE clawback rule (100% if closed within 6 months) - "
			               "replace with the terms agreed with the bank.")
			doc.save()
			counts["slabs"] += 1
	print(counts)


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
