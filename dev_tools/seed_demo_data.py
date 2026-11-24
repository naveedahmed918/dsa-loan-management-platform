"""One demo record in every DSA Loan Portal DocType, created through the real flow and KEPT (committed).

Run:  cd ~/frappe/frappe-bench-v15/sites && ../env/bin/python ../tools/seed_demo_data.py dsaloan.localhost
All names are fictional. Refuses to run twice (looks for lender code SHF).
"""
import sys

import frappe
from frappe.utils import add_days, add_months, get_first_day, nowdate

SITE = sys.argv[1] if len(sys.argv) > 1 else "dsaloan.localhost"


def step(text):
	print(f"\n== {text}")


def show(d, *fields):
	vals = ", ".join(f"{f}={d.get(f)}" for f in fields)
	print(f"   {d.doctype:<26} {d.name:<22} {vals}")
	return d


def new(values, *fields):
	return show(frappe.get_doc(values).insert(), *fields)


def run():
	today = nowdate()
	company = frappe.db.get_value("Company", {})
	if frappe.db.exists("Lender", "SHF"):
		print("Demo data already exists (lender SHF). Nothing done.")
		return

	step("1. Masters: lender side")
	lt = new({"doctype": "Lender Type", "lender_type_name": "Housing Finance Company", "type_code": "HFC"}, "type_code")
	group = frappe.get_doc({"doctype": "Email Group", "title": "Sahyadri Home Finance - Invoices"}).insert()
	for email in ("dsa.payments@sahyadrihf.example", "accounts@sahyadrihf.example"):
		frappe.get_doc({"doctype": "Email Group Member", "email_group": group.name, "email": email}).insert()
	lender = new({"doctype": "Lender", "lender_name": "Sahyadri Home Finance", "lender_code": "shf", "lender_type": lt.name,
	              "registered_company_name": "Sahyadri Home Finance Ltd", "pan": "aabcs1234k", "gstin": "27AABCS1234K1Z5",
	              "contact_person": "Ms Anjali Rao", "contact_number": "9822001100", "official_email": "partners@sahyadrihf.example",
	              "invoice_email_group": group.name, "invoice_cc": "dsa.desk@example.com"},
	             "lender_code", "pan", "invoice_email_group")
	lbr = new({"doctype": "Lender Branch", "lender_branch_name": "SHF Pune Camp", "branch_code": "pnq01", "lender": lender.name,
	           "branch_type": "Branch", "address_line_1": "East Street, Camp", "city": "Pune", "state": "Maharashtra",
	           "pincode": "411001", "branch_manager_name": "Mr Vikram Joshi"}, "lender_branch_name")
	prod = new({"doctype": "Loan Product", "lender": lender.name, "product_name": "SHF Home Loan", "product_code": "shfhl",
	            "loan_category": "Home Loan", "minimum_loan_amount": 500000, "maximum_loan_amount": 50000000}, "product_code")
	scheme = new({"doctype": "Loan Scheme", "scheme_name": "Salaried Advantage", "scheme_code": "shfsal", "lender": lender.name,
	              "loan_product": prod.name, "effective_from": add_days(today, -90), "scheme_status": "Active"}, "scheme_status")
	slab = new({"doctype": "Commission Slab Structure", "slab_name": "SHF Home Loan 2026", "lender": lender.name,
	            "loan_product": prod.name, "calculation_basis": "Disbursed Amount", "effective_from": add_days(today, -90),
	            "slab_status": "Active"}, "calculation_basis")
	rule = new({"doctype": "Lender Document Rule", "rule_name": "SHF Sale Agreement", "lender": lender.name,
	            "loan_product": prod.name, "applicant_type": "Primary Applicant", "document_category": "Property",
	            "document_name": "Registered Sale Agreement"}, "document_name")

	step("2. Masters: DSA side")
	fr = new({"doctype": "Franchise", "franchise_name": "Kothrud Loan Point", "franchise_code": "ktd", "franchise_owner": "Mr Rahul Patil",
	          "company": company, "contact_number": "+91 98220 55555", "settlement_percentage": 40}, "settlement_percentage")
	branch = new({"doctype": "DSA Branch", "branch_name": "Kothrud Branch", "branch_code": "ktd01", "company": company,
	              "branch_type": "Franchise Owned", "franchise": fr.name, "address_line_1": "Karve Road, Kothrud",
	              "city": "Pune", "state": "Maharashtra", "pincode": "411038"}, "branch_type", "franchise")
	agent = frappe.get_doc({"doctype": "Employee", "first_name": "Sneha", "last_name": "Kulkarni", "gender": "Female",
	                        "date_of_birth": "1995-06-15", "date_of_joining": "2024-01-10", "company": company,
	                        "status": "Active"}).insert()
	print(f"   Employee (agent)           {agent.name}")
	login = new({"doctype": "Lender Login", "login_title": "SHF partner portal - Sneha", "lender": lender.name,
	             "lender_branch": lbr.name, "portal_name": "SHF Partner LOS", "portal_url": "https://partners.sahyadrihf.example",
	             "login_username": "ktd.sneha", "assigned_employee": agent.name, "access_type": "Individual"}, "access_status")

	step("3. Lead -> Customer")
	lead = new({"doctype": "Loan Lead", "lead_title": "Home loan - 2BHK Baner", "customer_name": "Rohan Shinde",
	            "mobile_number": "+91 97654 32109", "email": "rohan.shinde@example.com", "lead_source": "Walk-in",
	            "loan_type": "Home Loan", "estimated_loan_amount": 4500000, "employment_type": "Salaried",
	            "assigned_company": company, "dsa_branch": branch.name, "customer_consent": 1}, "lead_status", "mobile_number")
	from dsa_loan.dsa_loan_portal.doctype.loan_lead.loan_lead import convert_to_customer

	cust = frappe.get_doc("Loan Customer", convert_to_customer(lead.name))
	cust.update({"date_of_birth": "1990-03-12", "gender": "Male", "marital_status": "Married",
	             "customer_category": "Resident Individual", "employer_business_name": "Infotech Solutions Pvt Ltd",
	             "designation": "Senior Engineer", "monthly_income": 145000, "existing_emi": 8000, "pan": "bksps7788q",
	             "kyc_consent": 1, "consent_mode": "Signed Form", "aadhaar_number": "5678 1234 9087",
	             "cibil_score": 782, "cibil_report_date": add_days(today, -5)})
	cust.save()
	show(cust, "dsa_branch", "aadhaar_number", "cibil_score", "consent_date")

	step("4. Loan Application -> Document Checklist created automatically")
	app = new({"doctype": "Loan Application", "loan_lead": lead.name, "primary_customer": cust.name, "lender": lender.name,
	           "lender_branch": lbr.name, "loan_product": prod.name, "loan_scheme": scheme.name, "loan_type": "Home Loan",
	           "company": company, "franchise": fr.name, "dsa_branch": branch.name, "assigned_agent": agent.name,
	           "requested_loan_amount": 4500000, "requested_tenure_months": 240, "expected_interest_rate": 8.6,
	           "loan_purpose": "Purchase", "property_type": frappe.get_meta("Loan Application").get_field("property_type").options.split("\n")[1],
	           "property_value": 6500000, "property_address": "Flat 702, Green Meadows, Baner", "property_city": "Pune",
	           "property_state": "Maharashtra", "property_pincode": "411045"}, "final_status", "estimated_emi")
	print(f"   Lead status now: {frappe.db.get_value('Loan Lead', lead.name, 'lead_status')}")
	cl = frappe.get_doc("Document Checklist", {"loan_application": app.name})
	show(cl, "applicant", "dsa_branch")
	print(f"   {len(cl.documents)} checklist rows: " + ", ".join(r.document_name for r in cl.documents))

	step("5. Extracted data for the 7 documents (each links itself to its checklist row)")
	base = {"document_checklist": cl.name, "extraction_status": "Verified"}
	new(dict(base, doctype="Aadhaar Card Data", aadhaar_last_4="9087", name_on_card="Rohan Shinde", date_of_birth="1990-03-12",
	         gender="Male", address="Flat 12, Shanti Niwas, Kothrud, Pune 411038"), "aadhaar_last_4")
	new(dict(base, doctype="PAN Card Data", pan_number="BKSPS7788Q", name_on_card="ROHAN SHINDE", father_name="PRAKASH SHINDE",
	         date_of_birth="1990-03-12"), "pan_number")
	new(dict(base, doctype="Address Proof Data", proof_type="Utility Bill", name_on_document="Rohan Shinde",
	         address="Flat 12, Shanti Niwas, Kothrud, Pune 411038", document_date=add_days(today, -20)), "proof_type")
	new(dict(base, doctype="Bank Statement Data", bank_name="Example Co-operative Bank", account_last_4="5566",
	         period_from=get_first_day(add_months(today, -6)), period_to=add_days(get_first_day(today), -1),
	         average_balance=210000, total_credits=870000, total_debits=790000, salary_credits=870000, bounced_cheques=0),
	    "months_covered")
	for m in (1, 2, 3):
		new(dict(base, doctype="Salary Slip Data", employer_name="Infotech Solutions Pvt Ltd",
		         salary_month=get_first_day(add_months(today, -m)), gross_salary=165000, deductions=20000, net_salary=145000),
		    "salary_month")
		if m == 1:
			print("   (one salary slip is enough for 'one record'; adding all 3 so the checklist completes)")
	new(dict(base, doctype="ITR Data", assessment_year="2025-26", total_income=1980000, tax_paid=410000,
	         filing_date="2025-07-28", acknowledgement_number="ACK-DEMO-2025-778899"), "assessment_year")
	new(dict(base, doctype="Form 16 Data", assessment_year="2025-26", employer_name="Infotech Solutions Pvt Ltd",
	         employer_tan="PNEI12345E", employee_pan="BKSPS7788Q", gross_salary=1980000, total_deductions=200000,
	         taxable_income=1780000, tds_deducted=410000, certificate_number="F16-DEMO-001", issue_date="2025-06-10"),
	    "employee_pan")

	cl.reload()
	for r in cl.documents:
		if r.extracted_data:
			r.document_status = "Verified"
		elif r.document_name == "Registered Sale Agreement":
			r.document_status = "Received"
	cl.save()
	counts = {}
	for r in cl.documents:
		counts[r.document_status] = counts.get(r.document_status, 0) + 1
	print(f"   Checklist rows by status: {counts}")

	step("6. Application moves through the lender process")
	app.reload()
	for st in ("Documents Pending", "Ready for Submission"):
		app.final_status = st
		app.save()
	app.update({"final_status": "Submitted", "lender_application_number": "SHF/PNQ/2026/04417",
	            "lender_submission_date": add_days(today, -6)})
	app.save()
	app.update({"final_status": "Sanctioned", "sanction_date": add_days(today, -2), "sanctioned_amount": 4200000,
	            "sanctioned_interest_rate": 8.55, "sanctioned_tenure_months": 240, "sanction_valid_until": add_days(today, 90),
	            "manager_approval": "Approved"})
	app.save()
	show(app, "final_status", "sanctioned_amount", "application_status")

	step("7. Disbursement -> Disbursed -> Commission -> ERPNext Sales Invoice + email (automatic)")
	disb = new({"doctype": "Loan Disbursement", "loan_application": app.name, "disbursement_number": "1",
	            "disbursement_date": today, "disbursement_type": "Full", "disbursement_status": "Confirmed",
	            "current_disbursement_amount": 4200000, "beneficiary_name": "Green Meadows Developers",
	            "payment_mode": "NEFT", "payment_reference": "UTR-DEMO-0001"}, "total_disbursed_amount", "balance_amount")
	print(f"   Application status: {frappe.db.get_value('Loan Application', app.name, ['final_status', 'invoice_status'])}")
	calc = new({"doctype": "Commission Calculation", "loan_application": app.name, "loan_disbursement": disb.name,
	            "commission_percentage": 0.5, "gst_rate": 18, "tds_rate": 10}, "gross_commission", "gst_amount", "net_commission")
	app.reload()
	show(app, "invoice_status", "sales_invoice", "invoice_amount", "invoice_email_recipients")
	print(f"   Note: {app.invoice_error}")

	step("8. Commission & settlement records")
	inv = new({"doctype": "Commission Invoice", "company": company, "lender": lender.name, "invoice_type": "Commission",
	           "invoice_number": "KTD/26-27/001", "taxable_amount": calc.gross_commission,
	           "cgst_amount": calc.gross_commission * 0.09, "sgst_amount": calc.gross_commission * 0.09}, "invoice_total")
	lps = new({"doctype": "Lender Payout Statement", "statement_number": "SHF-PO-2026-11", "lender": lender.name,
	           "statement_date": today, "period_from": get_first_day(today), "period_to": today,
	           "total_lender_commission": calc.gross_commission, "total_tds": calc.tds_amount,
	           "actual_received_amount": calc.gross_commission - calc.tds_amount}, "reconciliation_status", "net_payable")
	cb = new({"doctype": "Commission Clawback", "commission_calculation": calc.name, "commission_invoice": inv.name,
	          "clawback_reason": "Loan Closure", "clawback_percentage": 10, "recovery_amount": 0}, "clawback_amount", "recovery_status")
	fs = new({"doctype": "Franchise Settlement", "settlement_number": "KTD-SET-2026-11", "franchise": fr.name,
	          "settlement_period_from": get_first_day(today), "settlement_period_to": today, "tds_amount": 840},
	         "total_gross_commission", "franchise_share_amount", "net_payable")

	frappe.db.commit()
	step("Done - all records committed")
	print(f"   Open: http://dsaloan.localhost:8001/app/loan-application/{app.name}")


frappe.init(site=SITE, sites_path=".")
frappe.connect()
frappe.set_user("Administrator")
try:
	run()
except Exception:
	frappe.db.rollback()
	raise
finally:
	frappe.destroy()
