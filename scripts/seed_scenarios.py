"""Scenario data: every DSA DocType gets 5-20 records and every status / case is covered, through the real controllers.

People and addresses are fictional; lenders, products, schemes and document rules are the master data already on
the site. Run:  cd ~/frappe/frappe-bench-v15/sites && ../env/bin/python ../apps/dsa_loan/scripts/seed_scenarios.py dsaloan.localhost
Refuses to run twice (looks for lead mobile 9811100001). All-or-nothing.

Applications (14) - one per final status:
  N1 Draft                 HDFC   salaried, KYC in progress, no documents yet
  S7 Documents Pending     Axis   plot via franchise, no consent, address proof Rejected
  N2 Ready for Submission  ICICI  salaried, all documents verified
  N3 Submitted             BOB    self-employed
  N4 Under Review          Axis   professional (CA)
  S4 Query Raised          BOB    balance transfer, bank statement Resubmission Required
  N5 Sanctioned            SBI    business owner, tranche Pending + tranche Draft
  S3 Rejected              ICICI  professional, low CIBIL
  S5 On Hold               LIC    salaried + spouse
  S2 Partially Disbursed   HDFC   self-employed + spouse co-applicant + father guarantor, one tranche Failed
  S1 Disbursed             SBI    salaried, single tranche -> Sales Invoice
  S8 Disbursed             SBI    plot + construction via franchise, two tranches -> Sales Invoice
  S6 Withdrawn             Axis   salaried + spouse, withdrew after sanction
  N6 Closed                LIC    salaried + spouse, disbursed, foreclosed -> full commission clawback
"""
import sys

import frappe
from frappe.utils import add_days, add_months, get_first_day, get_last_day, nowdate

D = frappe._dict()  # dates, filled once connected
AY = ["2024-25", "2025-26", "2026-27"]


def say(text):
	print(text)


def new(values):
	return frappe.get_doc(values).insert()


def P(name, mobile, dob, gender, marital, employment, employer, designation, income, emi, pan, aadhaar, cibil, father, address):
	return frappe._dict(name=name, mobile=mobile, email=name.lower().replace("dr ", "").replace(" ", ".") + "@example.com",
	                    dob=dob, gender=gender, marital=marital, employment=employment, employer=employer,
	                    designation=designation, income=income, emi=emi, pan=pan, aadhaar=aadhaar, cibil=cibil, father=father,
	                    address=address, bank="Example Bank", acc=aadhaar[-4:])


PEOPLE = {
	"arjun": P("Arjun Mehta", "9811100001", "1989-04-18", "Male", "Married", "Salaried", "Brightline Software Pvt Ltd",
	           "Lead Engineer", 185000, 12000, "BQXPM4821K", "2345 6789 4821", 788, "RAKESH MEHTA", "Flat 304, Sunshine Residency, Baner, Pune 411045"),
	"neha": P("Neha Shah", "9811100002", "1986-09-02", "Female", "Married", "Self Employed", "Shah Interiors", "Proprietor",
	          240000, 0, "CDRPS5532L", "3456 7890 5532", 771, "MAHESH PAREKH", "12 Sea Breeze, Andheri West, Mumbai 400053"),
	"karan": P("Karan Shah", "9811100003", "1984-01-25", "Male", "Married", "Salaried", "Westcoast Logistics Ltd",
	           "Finance Manager", 160000, 9000, "CDRPS6614M", "4567 8901 6614", 802, "SURESH SHAH", "12 Sea Breeze, Andheri West, Mumbai 400053"),
	"suresh": P("Suresh Shah", "9811100004", "1956-07-11", "Male", "Married", "Business Owner", "Shah Textiles", "Partner",
	            150000, 0, "CDRPS7720N", "5678 9012 7720", 760, "NAVIN SHAH", "7 Shanti Kunj, Vile Parle East, Mumbai 400057"),
	"kavya": P("Dr Kavya Iyer", "9811100005", "1990-12-05", "Female", "Single", "Professional", "Iyer Dental Clinic", "Dentist",
	           210000, 48000, "EFGPI2290P", "6789 0123 2290", 642, "VENKAT IYER", "B-1102, Lake View Towers, Thane West 400601"),
	"imran": P("Imran Shaikh", "9811100006", "1981-03-30", "Male", "Married", "Business Owner", "Shaikh Auto Parts", "Proprietor",
	           175000, 31000, "GHJPS3345Q", "7890 1234 3345", 731, "YUSUF SHAIKH", "Plot 21, College Road, Nashik 422005"),
	"meera": P("Meera Kulkarni", "9811100007", "1992-08-14", "Female", "Married", "Salaried", "Central Hospital Trust",
	           "Senior Nurse", 98000, 0, "JKLPK4456R", "8901 2345 4456", 754, "ANIL KULKARNI", "45 Dharampeth, Nagpur 440010"),
	"ajay": P("Ajay Kulkarni", "9811100011", "1990-05-19", "Male", "Married", "Salaried", "Nagpur Metro Rail", "Engineer",
	          88000, 0, "JKLPK8812A", "3456 1234 8812", 739, "VASANT KULKARNI", "45 Dharampeth, Nagpur 440010"),
	"sanjay": P("Sanjay Rao", "9811100008", "1987-02-27", "Male", "Married", "Salaried", "Deccan Pharma Ltd", "Area Manager",
	            142000, 15000, "LMNPR5567S", "9012 3456 5567", 776, "GOPAL RAO", "9 Kalyani Nagar, Pune 411006"),
	"divya": P("Divya Rao", "9811100012", "1989-10-03", "Female", "Married", "Salaried", "Pune Public School", "Teacher",
	           65000, 0, "LMNPR9923B", "4567 2345 9923", 781, "KRISHNA MURTHY", "9 Kalyani Nagar, Pune 411006"),
	"pooja": P("Pooja Bhosale", "9811100009", "1994-11-09", "Female", "Single", "Salaried", "Sahyadri Schools", "Teacher",
	           72000, 0, "NPQPB6678T", "1234 5678 6678", 748, "DATTA BHOSALE", "17 Paud Road, Kothrud, Pune 411038"),
	"ganesh": P("Ganesh Jadhav", "9811100010", "1983-06-21", "Male", "Married", "Business Owner", "Jadhav Hardware", "Proprietor",
	            190000, 10000, "QRSPJ7789U", "2345 6789 7789", 769, "BALU JADHAV", "5 Karve Nagar, Pune 411052"),
	"vivek": P("Vivek Chavan", "9811100013", "1995-01-30", "Male", "Single", "Salaried", "Orbit Analytics", "Data Analyst",
	           95000, 0, "RSTPC1034C", "5678 3456 1034", 0, "MOHAN CHAVAN", "22 Hadapsar, Pune 411028"),
	"aisha": P("Aisha Siddiqui", "9811100014", "1991-06-12", "Female", "Married", "Salaried", "Coastal Shipping Corp",
	           "HR Manager", 175000, 8000, "STUPS2145D", "6789 4567 2145", 795, "AMAN SIDDIQUI", "301 Palm Court, Bandra West, Mumbai 400050"),
	"harish": P("Harish Menon", "9811100015", "1980-09-09", "Male", "Married", "Self Employed", "Menon Travels", "Proprietor",
	            165000, 12000, "TUVPM3256E", "7890 5678 3256", 744, "GOPI MENON", "8 Ghodbunder Road, Thane 400607"),
	"kiran": P("Kiran Patwardhan", "9811100016", "1988-04-04", "Male", "Married", "Professional", "Patwardhan & Co (CA)",
	           "Chartered Accountant", 230000, 20000, "UVWPP4367F", "8901 6789 4367", 812, "SHRIDHAR PATWARDHAN", "14 Prabhat Road, Pune 411004"),
	"rakesh": P("Rakesh Agarwal", "9811100017", "1978-12-15", "Male", "Married", "Business Owner", "Agarwal Steel Traders",
	            "Director", 420000, 60000, "VWXPA5478G", "9012 7890 5478", 778, "MOTILAL AGARWAL", "9 Peddar Road, Mumbai 400026"),
	"nikhil": P("Nikhil Sawant", "9811100018", "1987-07-22", "Male", "Married", "Salaried", "Vidarbha Power Ltd", "Engineer",
	            110000, 0, "WXYPS6589H", "1234 8901 6589", 765, "PRAKASH SAWANT", "33 Civil Lines, Nagpur 440001"),
	"smita": P("Smita Sawant", "9811100019", "1990-03-08", "Female", "Married", "Salaried", "Nagpur University", "Lecturer",
	           80000, 0, "WXYPS7690J", "2345 9012 7690", 790, "DILIP PATIL", "33 Civil Lines, Nagpur 440001"),
}


def customer_details(cust_name, p, consent=True, kyc="Verified", status="Active"):
	doc = frappe.get_doc("Loan Customer", cust_name)
	doc.update({"date_of_birth": p.dob, "gender": p.gender, "marital_status": p.marital, "customer_category": "Resident Individual",
	            "employment_type": p.employment, "employer_business_name": p.employer, "designation": p.designation,
	            "monthly_income": p.income, "existing_emi": p.emi, "pan": p.pan, "kyc_status": kyc, "customer_status": status})
	if consent:
		doc.update({"kyc_consent": 1, "consent_mode": "Signed Form", "aadhaar_number": p.aadhaar})
		if p.cibil:
			doc.update({"cibil_score": p.cibil, "cibil_report_date": add_days(D.today, -7)})
	doc.save()
	return doc


def new_customer(p, branch, **kw):
	doc = new({"doctype": "Loan Customer", "customer_name": p.name, "mobile_number": p.mobile, "email": p.email, "dsa_branch": branch})
	return customer_details(doc.name, p, **kw)


# ----------------------------------------------------------------- documents
def fill_documents(cl_name, p, mode, verify=True, itr_years=3, statuses=None, only=None):
	"""mode: 'salaried' (KYC + bank + 3 salary slips + 3 Form 16; ITR rows Not Applicable, Form 16 accepted),
	'self' (KYC + bank + ITRs), 'kyc' (Aadhaar, PAN, address only; income rows Not Applicable)."""
	base = {"document_checklist": cl_name, "extraction_status": "Verified" if verify else "Extracted"}
	want = only or {"salaried": {"aadhaar", "pan", "address", "bank", "salary", "form16"},
	                "self": {"aadhaar", "pan", "address", "bank", "itr"}, "kyc": {"aadhaar", "pan", "address"}}[mode]
	if "aadhaar" in want:
		new(dict(base, doctype="Aadhaar Card Data", aadhaar_last_4=p.aadhaar[-4:], name_on_card=p.name, date_of_birth=p.dob,
		         gender=p.gender, address=p.address))
	if "pan" in want:
		new(dict(base, doctype="PAN Card Data", pan_number=p.pan, name_on_card=p.name.upper(), father_name=p.father, date_of_birth=p.dob))
	if "address" in want:
		new(dict(base, doctype="Address Proof Data", proof_type="Utility Bill", name_on_document=p.name, address=p.address,
		         document_date=add_days(D.today, -25)))
	if "bank" in want:
		new(dict(base, doctype="Bank Statement Data", bank_name=p.bank, account_last_4=p.acc,
		         period_from=get_first_day(add_months(D.today, -6)), period_to=add_days(D.month_start, -1),
		         average_balance=p.income * 1.4, total_credits=p.income * 6, total_debits=p.income * 6 * 0.85,
		         salary_credits=p.income * 6 if p.employment == "Salaried" else 0, bounced_cheques=0))
	if "salary" in want:
		for m in (1, 2, 3):
			new(dict(base, doctype="Salary Slip Data", employer_name=p.employer, salary_month=get_first_day(add_months(D.today, -m)),
			         gross_salary=round(p.income * 1.15), deductions=round(p.income * 0.15), net_salary=p.income))
	for i, ay in enumerate(AY):
		income = round(p.income * 12 * (0.85 + 0.075 * i))
		if "itr" in want and i >= 3 - itr_years:
			new(dict(base, doctype="ITR Data", assessment_year=ay, total_income=income, tax_paid=round(income * 0.2),
			         filing_date=f"{2024 + i}-07-25", acknowledgement_number=f"ITR-DEMO-{p.acc}-{ay}"))
		if "form16" in want:
			new(dict(base, doctype="Form 16 Data", assessment_year=ay, employer_name=p.employer, employer_tan="PNEX12345E",
			         employee_pan=p.pan, gross_salary=income + 50000, total_deductions=50000, taxable_income=income,
			         tds_deducted=round(income * 0.2), certificate_number=f"F16-{p.acc}-{ay}", issue_date=f"{2024 + i}-06-10"))
	na = {"salaried": {"ITR Data"}, "self": set(), "kyc": {"Bank Statement Data", "Salary Slip Data", "ITR Data", "Form 16 Data"}}[mode]
	cl = frappe.get_doc("Document Checklist", cl_name)
	for row in cl.documents:
		if statuses and row.document_name in statuses:
			row.document_status, row.remarks = statuses[row.document_name]
		elif row.document_status == "Not Applicable":
			continue
		elif row.extracted_data:
			row.document_status = "Verified" if verify else "Received"
		elif row.extracted_data_type in na and not only:
			row.document_status = "Not Applicable"
			row.remarks = "Form 16 accepted instead of ITR" if row.extracted_data_type == "ITR Data" else "Not needed for this applicant"
		elif not row.extracted_data_type:  # lender-rule rows, collected on paper
			row.document_status = "Verified" if verify else "Received"
	cl.save()


def checklist(app, customer):
	return frappe.db.get_value("Document Checklist", {"loan_application": app, "applicant": customer})


def move(app, *statuses, **values):
	for st in statuses:
		app.reload()
		if st == statuses[-1]:
			app.update(values)
		app.final_status = st
		app.save()


def disburse(app, number, kind, amount, status="Confirmed", days_ago=0):
	return new({"doctype": "Loan Disbursement", "loan_application": app, "disbursement_number": number,
	            "disbursement_date": add_days(D.today, -days_ago), "disbursement_type": kind, "disbursement_status": status,
	            "current_disbursement_amount": amount, "beneficiary_name": "Seller / Builder (demo)",
	            "beneficiary_account_reference": "XXXX" + number.zfill(4), "payment_mode": "RTGS",
	            "payment_reference": f"UTR-DEMO-{app[-5:]}-{number}"})


def commission(app, disb):
	"""Confirming a tranche creates its Commission Calculation automatically; fall back to creating it."""
	existing = frappe.db.get_value("Commission Calculation", {"loan_disbursement": disb})
	if existing:
		return frappe.get_doc("Commission Calculation", existing)
	return new({"doctype": "Commission Calculation", "loan_application": app, "loan_disbursement": disb})


def run():
	D.today = nowdate()
	D.month_start, D.month_end = get_first_day(D.today), get_last_day(D.today)
	D.last_start, D.last_end = get_first_day(add_months(D.today, -1)), get_last_day(add_months(D.today, -1))
	today = D.today
	if frappe.db.exists("Loan Lead", {"mobile_number": "9811100001"}):
		print("Scenario data already exists. Nothing done.")
		return
	company = frappe.db.get_value("Company", {})

	# ---------- masters topped up to 5+
	for nm, code, desc in (("Small Finance Bank", "SFB", "RBI-licensed small finance bank."),
	                       ("Non-Banking Financial Company", "NBFC", "RBI-registered NBFC offering home and property loans.")):
		new({"doctype": "Lender Type", "lender_type_name": nm, "type_code": code, "description": desc, "is_active": 1})
	for lender, lender_name in frappe.get_all("Lender", fields=["name", "lender_name"], as_list=True):
		title = f"{lender_name} - Invoices"
		if not frappe.db.exists("Email Group", title):
			frappe.get_doc({"doctype": "Email Group", "title": title}).insert()
		frappe.db.set_value("Lender", lender, "invoice_email_group", title)
	new({"doctype": "Commission Slab Structure", "slab_name": "State Bank of India - FY 2025-26", "lender": "SBI",
	     "calculation_basis": "Disbursed Amount", "commission_percentage": 0.35, "effective_from": "2025-04-01",
	     "effective_to": "2026-03-31", "slab_status": "Expired", "remarks": "Previous year's payout (SAMPLE %)."})
	say("Lender Types +2, empty invoice email groups for all 6 lenders, 1 expired commission slab")

	def employee(first, last, gender, dob):
		return frappe.get_doc({"doctype": "Employee", "first_name": first, "last_name": last, "gender": gender, "date_of_birth": dob,
		                       "date_of_joining": "2025-04-01", "company": company, "status": "Active"}).insert().name
	priya, rahul = employee("Priya", "Nair", "Female", "1985-05-10"), employee("Rahul", "Kulkarni", "Male", "1994-02-14")
	vikram, sneha = employee("Vikram", "Desai", "Male", "1982-09-30"), employee("Sneha", "Joshi", "Female", "1996-07-07")
	anjali, rohit = employee("Anjali", "Patil", "Female", "1993-03-21"), employee("Rohit", "Pawar", "Male", "1990-12-01")
	PUNE, MUM, THN, NSK, NGP = "LFS-PUN-01", "LFS-MUM-HO", "LFS-THN-01", "LFS-NSK-01", "LFS-NGP-01"
	frappe.db.set_value("DSA Branch", PUNE, "branch_manager", priya)
	frappe.db.set_value("DSA Branch", MUM, "branch_manager", vikram)

	fr = {}
	for code, nm, owner, status, pct, start, end in (
		("KLP", "Kothrud Loan Point", "Rohit Pawar", "Active", 40, "2026-04-01", "2029-03-31"),
		("NHD", "Nashik Home Finance Desk", "Sameer Kale", "Active", 35, "2026-01-01", "2028-12-31"),
		("TCL", "Thane City Loans", "Manoj Shetty", "Inactive", 35, "2025-04-01", "2027-03-31"),
		("NLM", "Nagpur Loan Mitra", "Pallavi Deshpande", "Suspended", 30, "2025-10-01", "2027-09-30"),
		("AHH", "Andheri Home Loan Hub", "Farhan Qureshi", "Terminated", 40, "2024-04-01", "2026-03-31")):
		fr[code] = new({"doctype": "Franchise", "franchise_name": nm, "franchise_code": code, "franchise_owner": owner,
		                "owner_employee": rohit if code == "KLP" else None, "company": company,
		                "contact_number": f"98220{55555 + len(fr)}", "email": f"{code.lower()}@example.com",
		                "franchise_status": status, "settlement_percentage": pct, "agreement_start_date": start,
		                "agreement_end_date": end, "gstin": "27AAKFK1234L1Z2" if code == "KLP" else None,
		                "remarks": {"Suspended": "Suspended pending audit of two files.", "Terminated": "Agreement ended 31-03-2026.",
		                            "Inactive": "Owner on leave; no new files."}.get(status)}).name
	kothrud = new({"doctype": "DSA Branch", "branch_name": "Kothrud Franchise Branch", "branch_code": "KLP-PUN-01", "company": company,
	               "branch_type": "Franchise Owned", "franchise": fr["KLP"], "address_line_1": "Karve Road, Kothrud",
	               "city": "Pune", "state": "Maharashtra", "pincode": "411038", "branch_status": "Active"}).name
	new({"doctype": "DSA Branch", "branch_name": "Nashik Franchise Desk", "branch_code": "NHD-NSK-01", "company": company,
	     "branch_type": "Franchise Operated", "franchise": fr["NHD"], "address_line_1": "Gangapur Road", "city": "Nashik",
	     "state": "Maharashtra", "pincode": "422013", "branch_status": "Active"})
	new({"doctype": "DSA Branch", "branch_name": "Thane City Branch (closed)", "branch_code": "TCL-THN-01", "company": company,
	     "branch_type": "Franchise Owned", "franchise": fr["TCL"], "address_line_1": "Naupada", "city": "Thane",
	     "state": "Maharashtra", "pincode": "400602", "branch_status": "Closed"})
	say("6 employees, 5 franchises (Active x2, Inactive, Suspended, Terminated), 3 more DSA branches (8 total)")

	lbr = {}
	for lender, nm, code, city, pin in (("SBI", "SBI RACPC Pune (demo)", "PUNRACPC", "Pune", "411001"),
	                                     ("HDFC", "HDFC Home Loans Andheri (demo)", "MUMAND", "Mumbai", "400053"),
	                                     ("ICICI", "ICICI Home Loans Thane (demo)", "THNHL", "Thane", "400601"),
	                                     ("BOB", "BOB Nashik Main (demo)", "NSKMAIN", "Nashik", "422001"),
	                                     ("LIC_HFL", "LIC HFL Nagpur Area Office (demo)", "NGPAO", "Nagpur", "440001"),
	                                     ("AXIS", "Axis Bank Pune Camp (demo)", "PUNCAMP", "Pune", "411001")):
		lbr[lender] = new({"doctype": "Lender Branch", "lender_branch_name": nm, "branch_code": code, "lender": lender,
		                   "branch_type": "Processing Centre", "address_line_1": "Demo address - replace with branch address",
		                   "city": city, "state": "Maharashtra", "pincode": pin}).name
	for lender, user, emp, status, end in (("SBI", "lfs.rahul", rahul, "Active", None), ("HDFC", "lfs.sneha", sneha, "Active", None),
	                                        ("ICICI", "lfs.anjali", anjali, "Active", None), ("BOB", "lfs.anjali.bob", anjali, "Active", None),
	                                        ("LIC_HFL", "lfs.anjali.lic", anjali, "Active", None), ("AXIS", "lfs.rahul.axis", rahul, "Active", None),
	                                        ("SBI", "lfs.oldagent", rohit, "Active", "2026-03-31"),
	                                        ("AXIS", "lfs.priya.axis", priya, "Locked", None)):
		new({"doctype": "Lender Login", "login_title": f"{lender} portal - {user}", "lender": lender, "lender_branch": lbr[lender],
		     "portal_name": f"{lender} DSA Connect", "login_username": user, "assigned_employee": emp, "access_type": "Individual",
		     "access_status": status, "access_start_date": "2025-04-01", "access_end_date": end,
		     "remarks": "Locked after three wrong passwords." if status == "Locked" else None})
	say("6 lender branches, 8 portal logins (Active, Expired, Locked)")

	from dsa_loan.dsa_loan_portal.doctype.loan_lead.loan_lead import convert_to_customer

	def start(key, branch, agent, bm, lender, product, scheme, loan_type, amount, tenure, rate, purpose, ptype, pvalue,
	          source="Walk-in", franchise=None, consent=True, kyc="Verified", co=()):
		p = PEOPLE[key]
		lead = new({"doctype": "Loan Lead", "lead_title": f"{loan_type} - {p.name}", "customer_name": p.name, "mobile_number": p.mobile,
		            "email": p.email, "city": p.address.rsplit(" ", 1)[0].split(",")[-1].strip(), "lead_status": "Qualified",
		            "customer_consent": 1, "lead_source": source, "loan_type": loan_type, "estimated_loan_amount": amount,
		            "employment_type": p.employment, "assigned_company": company, "dsa_branch": branch, "assigned_agent": agent,
		            "branch_manager": bm})
		cust = customer_details(convert_to_customer(lead.name), p, consent, kyc).name
		app = new({"doctype": "Loan Application", "loan_lead": lead.name, "primary_customer": cust, "lender": lender,
		           "lender_branch": lbr[lender], "loan_product": product, "loan_scheme": scheme, "loan_type": loan_type,
		           "company": company, "franchise": franchise, "dsa_branch": branch, "branch_manager": bm, "assigned_agent": agent,
		           "requested_loan_amount": amount, "requested_tenure_months": tenure, "expected_interest_rate": rate,
		           "loan_purpose": purpose, "property_type": ptype, "property_value": pvalue, "property_address": "Demo property address",
		           "property_city": p.address.rsplit(" ", 1)[0].split(",")[-1].strip(), "property_state": "Maharashtra",
		           "property_pincode": p.address.rsplit(" ", 1)[-1], "co_applicants": list(co)})
		return p, cust, app

	def spouse(key, branch, rel="Spouse", kind="Co-Applicant", income=0):
		c = new_customer(PEOPLE[key], branch).name
		return c, {"applicant": c, "applicant_type": kind, "relationship_with_primary": rel, "is_income_considered": 1 if income else 0,
		           "monthly_income": income, "ownership_percentage": 50 if kind == "Co-Applicant" else 0, "kyc_status": "Verified"}

	def to_submitted(app, ref, days, approve=True):
		move(app, "Documents Pending", "Ready for Submission")
		move(app, "Submitted", lender_application_number=ref, lender_submission_date=add_days(today, -days),
		     manager_approval="Approved" if approve else "Pending")

	def sanction(app, amount, rate, tenure, days):
		move(app, "Sanctioned", sanction_date=add_days(today, -days), sanctioned_amount=amount, sanctioned_interest_rate=rate,
		     sanctioned_tenure_months=tenure, sanction_valid_until=add_days(today, 90))

	apps = {}
	# N1 Draft
	p, cust, app = start("vivek", PUNE, rahul, priya, "HDFC", "HDFC_HOME_LOAN", "HDFC_REGULAR_HOME", "Home Loan", 3500000, 240, 8.5,
	                     "Purchase", "Flat", 5000000, source="Website", consent=False, kyc="In Progress")
	apps["Draft"] = app.name
	# S7 Documents Pending (franchise, no consent, rejected address proof)
	p, cust, app = start("pooja", kothrud, rohit, None, "AXIS", "AXIS_PLOT_PURCHASE", "AXIS_LAND_PURCHASE", "Plot Purchase", 2500000,
	                     180, 8.6, "Purchase", "Plot", 4000000, source="Partner", franchise=fr["KLP"], consent=False, kyc="Pending")
	fill_documents(checklist(app.name, cust), p, "kyc", verify=False, only={"aadhaar", "pan", "address"},
	               statuses={"Address Proof": ("Rejected", "Electricity bill older than 3 months; ask for a recent one.")})
	move(app, "Documents Pending", application_remarks="Waiting for signed KYC consent, bank statement, salary slips and Form 16.")
	apps["Documents Pending"] = app.name
	# N2 Ready for Submission
	p, cust, app = start("aisha", MUM, sneha, vikram, "ICICI", "ICICI_HOME_LOAN", "ICICI_REGULAR_HOME", "Home Loan", 7000000, 300,
	                     8.9, "Purchase", "Flat", 10000000, source="Referral")
	fill_documents(checklist(app.name, cust), p, "salaried")
	move(app, "Documents Pending", "Ready for Submission")
	apps["Ready for Submission"] = app.name
	# N3 Submitted
	p, cust, app = start("harish", THN, anjali, None, "BOB", "BOB_HOME_LOAN", "BOB_REGULAR_HOME", "Home Loan", 4000000, 240, 8.1,
	                     "Purchase", "Independent House", 6000000, source="Advertisement")
	fill_documents(checklist(app.name, cust), p, "self")
	to_submitted(app, "BOB/THN/2026/1188", 2, approve=False)
	apps["Submitted"] = app.name
	# N4 Under Review
	p, cust, app = start("kiran", PUNE, rahul, priya, "AXIS", "AXIS_HOME_LOAN", "AXIS_FAST_FORWARD", "Home Loan", 5000000, 240, 8.2,
	                     "Construction", "Villa", 7500000, source="Referral")
	fill_documents(checklist(app.name, cust), p, "self")
	to_submitted(app, "AXIS/PUN/26/4602", 6)
	move(app, "Under Review", application_remarks="Axis credit team reviewing CA practice income.")
	apps["Under Review"] = app.name
	# S4 Query Raised
	p, cust, app = start("imran", NSK, anjali, None, "BOB", "BOB_BALANCE_TRANSFER", "BOB_HOME_TAKEOVER", "Balance Transfer", 3000000,
	                     180, 7.9, "Balance Transfer", "Independent House", 5500000, source="Advertisement")
	fill_documents(checklist(app.name, cust), p, "self", statuses={
		"Bank Statement – Last 6 Months": ("Resubmission Required", "Lender wants the business current account, not savings.")})
	to_submitted(app, "BOB/NSK/2026/0912", 8)
	move(app, "Query Raised", application_remarks="BOB query: current-account statement and existing lender's foreclosure letter.")
	apps["Query Raised"] = app.name
	# N5 Sanctioned, tranche Pending + Draft
	p, cust, app = start("rakesh", MUM, sneha, vikram, "SBI", "SBI_HOME_LOAN", "SBI_MAXGAIN", "Home Loan", 12000000, 240, 8.2,
	                     "Purchase", "Flat", 20000000, source="Partner")
	fill_documents(checklist(app.name, cust), p, "self")
	to_submitted(app, "SBI/MUM/2026/30455", 15)
	move(app, "Under Review")
	sanction(app, 12000000, 8.25, 240, 4)
	disburse(app.name, "1", "Part", 8000000, status="Pending")
	disburse(app.name, "2", "Final", 4000000, status="Draft")
	apps["Sanctioned"] = app.name
	# S3 Rejected
	p, cust, app = start("kavya", THN, anjali, None, "ICICI", "ICICI_HOME_LOAN", "ICICI_REGULAR_HOME", "Home Loan", 6000000, 240,
	                     9.1, "Purchase", "Flat", 8000000, source="Website")
	fill_documents(checklist(app.name, cust), p, "self", itr_years=2, statuses={
		"ITR – Year 1": ("Not Applicable", "Practice started in FY 2024-25; only 2 returns filed.")})
	to_submitted(app, "ICICI/THN/26/7781", 15)
	move(app, "Under Review")
	move(app, "Rejected", rejection_reason="CIBIL 642 is below ICICI's cut-off and existing EMIs of Rs 48,000 push FOIR over the limit.",
	     application_remarks="Advise closing one personal loan and re-applying after 6 months.")
	apps["Rejected"] = app.name
	# S5 On Hold (+ spouse co-applicant)
	ajay, row = spouse("ajay", NGP)
	p, cust, app = start("meera", NGP, anjali, None, "LIC_HFL", "LIC_HFL_HOME_LOAN", "LIC_HFL_REGULAR_HOME", "Home Loan", 3800000,
	                     300, 7.6, "Purchase", "Flat", 5000000, co=[row])
	fill_documents(checklist(app.name, cust), p, "salaried")
	fill_documents(checklist(app.name, ajay), PEOPLE["ajay"], "kyc")
	to_submitted(app, "LICHFL/NGP/26/3307", 18)
	move(app, "Under Review")
	move(app, "On Hold", application_remarks="LIC HFL legal team waiting for the society NOC.")
	apps["On Hold"] = app.name
	# S2 Partially Disbursed (+ spouse co-applicant with income, father guarantor), one tranche Failed
	karan, krow = spouse("karan", MUM, income=160000)
	suresh, grow = spouse("suresh", MUM, rel="Parent", kind="Guarantor")
	p, cust, app = start("neha", MUM, sneha, vikram, "HDFC", "HDFC_HOME_LOAN", "HDFC_REGULAR_HOME", "Home Loan", 8500000, 300, 8.4,
	                     "Construction", "Flat", 12000000, source="Agent", co=[krow, grow])
	fill_documents(checklist(app.name, cust), p, "self")
	fill_documents(checklist(app.name, karan), PEOPLE["karan"], "salaried")
	fill_documents(checklist(app.name, suresh), PEOPLE["suresh"], "kyc", verify=False, only={"aadhaar", "pan", "address", "bank"})
	to_submitted(app, "HDFC/MUM/26/55021", 20)
	move(app, "Under Review")
	sanction(app, 8000000, 8.35, 300, 10)
	d = disburse(app.name, "1", "Part", 5000000, days_ago=3)
	commission(app.name, d.name)
	disburse(app.name, "2", "Part", 1500000, status="Failed")
	apps["Partially Disbursed"] = app.name
	# S1 Disbursed, single tranche
	p, cust, app = start("arjun", PUNE, rahul, priya, "SBI", "SBI_HOME_LOAN", "SBI_HOME_LOAN_SCHEME", "Home Loan", 4500000, 240, 7.75,
	                     "Purchase", "Flat", 6500000, source="Referral")
	fill_documents(checklist(app.name, cust), p, "salaried")
	to_submitted(app, "SBI/PUN/2026/11873", 12)
	move(app, "Under Review")
	sanction(app, 4200000, 7.7, 240, 5)
	commission(app.name, disburse(app.name, "1", "Full", 4200000).name)
	s1 = apps["Disbursed (single)"] = app.name
	# S8 Disbursed, two tranches, franchise
	p, cust, app = start("ganesh", kothrud, rohit, None, "SBI", "SBI_PLOT_CONSTRUCTION", "SBI_COMBO_HOME_LOAN", "Plot + Construction",
	                     3500000, 240, 7.8, "Plot + Construction", "Plot", 5500000, source="Partner", franchise=fr["KLP"])
	fill_documents(checklist(app.name, cust), p, "self")
	to_submitted(app, "SBI/PUN/2026/12090", 30)
	sanction(app, 3500000, 7.75, 240, 21)
	commission(app.name, disburse(app.name, "1", "Part", 2000000, days_ago=14).name)
	commission(app.name, disburse(app.name, "2", "Final", 1500000, days_ago=1).name)
	s8 = apps["Disbursed (two tranches)"] = app.name
	# S6 Withdrawn (+ spouse)
	divya, row = spouse("divya", PUNE)
	p, cust, app = start("sanjay", PUNE, rahul, priya, "AXIS", "AXIS_HOME_LOAN", "AXIS_FAST_FORWARD", "Home Loan", 5500000, 240, 8.3,
	                     "Purchase", "Flat", 8000000, source="Partner", co=[row])
	fill_documents(checklist(app.name, cust), p, "salaried")
	fill_documents(checklist(app.name, divya), PEOPLE["divya"], "kyc")
	to_submitted(app, "AXIS/PUN/26/4410", 25)
	sanction(app, 5500000, 8.25, 240, 14)
	move(app, "Withdrawn", application_remarks="Customer dropped the purchase after the builder delayed possession.")
	apps["Withdrawn"] = app.name
	# N6 Closed (+ spouse): disbursed earlier, foreclosed
	smita, row = spouse("smita", NGP)
	p, cust, app = start("nikhil", NGP, anjali, None, "LIC_HFL", "LIC_HFL_HOME_LOAN", "LIC_HFL_REGULAR_HOME", "Home Loan", 2800000,
	                     180, 7.4, "Purchase", "Flat", 4000000, co=[row])
	fill_documents(checklist(app.name, cust), p, "salaried")
	fill_documents(checklist(app.name, smita), PEOPLE["smita"], "kyc")
	to_submitted(app, "LICHFL/NGP/26/2950", 45)
	sanction(app, 2800000, 7.4, 180, 38)
	n6_calc = commission(app.name, disburse(app.name, "1", "Full", 2800000, days_ago=35).name)
	move(app, "Closed", application_remarks="Borrower foreclosed the loan from a bonus within 2 months.")
	frappe.db.set_value("Loan Customer", cust, "customer_status", "Inactive")
	n6 = apps["Closed"] = app.name
	for st, name in apps.items():
		say(f"  {st:<26} {name}")

	# standalone customer: blacklisted
	bl = new({"doctype": "Loan Customer", "customer_name": "Test Fraud Case", "mobile_number": "9811100020", "dsa_branch": THN,
	          "customer_status": "Blacklisted", "kyc_status": "Rejected",
	          "remarks": "Submitted forged salary slips in 2025; do not accept files (demo)."})
	say(f"Blacklisted customer {bl.name}")

	# leads that did not convert
	for n, (who, status, note, follow, src, branch, agent) in enumerate((
		("Rohan Gupta", "New", "Enquiry from website form.", 1, "Website", PUNE, rahul),
		("Farah Khan", "Contacted", "Called once; wants rates for 20 years.", 2, "Referral", MUM, sneha),
		("Aditya Naik", "Interested", "Visiting branch on Saturday with documents.", 3, "Walk-in", THN, anjali),
		("Sonal Gokhale", "Qualified", "Eligible for 40L; collecting documents.", 1, "Partner", kothrud, rohit),
		("Swati More", "Not Interested", "Decided to rent for two more years.", None, "Advertisement", NSK, anjali),
		("Lata Pillai", "Lost", "Took a loan directly from her employer's bank.", None, "Agent", NGP, anjali)), 1):
		new({"doctype": "Loan Lead", "lead_title": f"Home loan enquiry - {who}", "customer_name": who, "mobile_number": f"98111002{n:02d}",
		     "lead_status": status, "next_follow_up_date": add_days(today, follow) if follow else None, "customer_consent": 1,
		     "lead_source": src, "loan_type": "Home Loan", "estimated_loan_amount": 2500000 + n * 500000,
		     "employment_type": "Salaried", "assigned_company": company, "dsa_branch": branch, "assigned_agent": agent, "remarks": note})
	say("6 leads not converted: New, Contacted, Interested, Qualified, Not Interested, Lost")

	# ---------- money
	def calcs(lender):
		return frappe.get_all("Commission Calculation", {"lender": lender}, ["name", "gross_commission", "loan_application"])
	sbi = calcs("SBI")
	sbi_total = sum(c.gross_commission for c in sbi)
	hdfc = calcs("HDFC")[0]
	lic = calcs("LIC_HFL")[0]

	def cinv(lender, number, kind, status, amount, igst=False, sales=None, note=None):
		return new({"doctype": "Commission Invoice", "company": company, "lender": lender, "invoice_type": kind, "invoice_number": number,
		            "due_date": add_days(today, 30), "invoice_status": status, "erpnext_sales_invoice": sales, "taxable_amount": amount,
		            "igst_amount": round(amount * 0.18, 2) if igst else 0, "cgst_amount": 0 if igst else round(amount * 0.09, 2),
		            "sgst_amount": 0 if igst else round(amount * 0.09, 2), "tds_expected": round(amount * 0.10, 2), "remarks": note}).name
	sbi_inv = cinv("SBI", "LFS/26-27/0001", "Commission", "Submitted", sbi_total,
	               note=f"November summary of commission on {s1} and {s8} (the per-loan invoices are created automatically).")
	cinv("HDFC", "LFS/26-27/0002", "Commission", "Pending Approval", hdfc.gross_commission, igst=True,
	     note="Part-disbursement commission; IGST because HDFC bills from another state (demo).")
	lic_ci = frappe.db.get_value("Commission Invoice", {"erpnext_sales_invoice": frappe.db.get_value("Loan Application", n6, "sales_invoice")})
	if lic_ci:
		frappe.db.set_value("Commission Invoice", lic_ci, {"invoice_status": "Paid", "remarks": "Paid by LIC HFL (demo)."})
	cinv("AXIS", "LFS/26-27/0006", "Adjustment", "Cancelled", 1500, note="Raised by mistake on a withdrawn file; cancelled.")
	say("Commission Invoices: one per lender Sales Invoice (automatic, LIC marked Paid), SBI summary Submitted, HDFC Pending "
	    "Approval, Adjustment Cancelled; Debit / Credit Notes follow automatically from payouts and clawbacks")

	def payout(number, lender, claimed, received, status=None, start=None, end=None, note=None):
		values = {"doctype": "Lender Payout Statement", "statement_number": number, "lender": lender, "statement_date": today,
		          "period_from": start or D.month_start, "period_to": end or D.month_end, "total_lender_commission": claimed,
		          "total_tds": round(claimed * 0.10, 2), "actual_received_amount": received, "payment_date": today if received else None,
		          "bank_reference": f"NEFT-DEMO-{lender}" if received else None, "remarks": note}
		if status:
			values["reconciliation_status"] = status
		return new(values)
	payout("SBI-DSA-PO-2026-11", "SBI", sbi_total, round(sbi_total * 0.9, 2), note="Full payout - matches our calculations.")
	short = hdfc.gross_commission - 2000
	payout("HDFC-DSA-11-2026", "HDFC", short, round(short * 0.9, 2), note="HDFC paid Rs 2,000 less than calculated.")
	payout("LICHFL-PO-NOV26", "LIC_HFL", lic.gross_commission, round(lic.gross_commission * 0.9, 2), note="Matched.")
	payout("ICICI-STMT-NOV26", "ICICI", 1500, 0, note="ICICI listed an old adjustment; payment not received yet.")
	payout("AXIS-PO-1126", "AXIS", 5000, 0, status="Disputed", note="Axis shows commission on the withdrawn file; disputed.")
	payout("BOB-PO-OCT26", "BOB", 0, 0, status="Closed", start=D.last_start, end=D.last_end, note="Nil statement for October.")
	say("6 Lender Payout Statements: Matched x2, Partially Matched, Pending Reconciliation, Disputed, Closed")

	s8_calcs = frappe.get_all("Commission Calculation", {"loan_application": s8}, pluck="name", order_by="creation")
	s1_calc = frappe.get_all("Commission Calculation", {"loan_application": s1}, pluck="name")[0]
	for calc, inv, reason, pct, recovered, status, note in (
		(s1_calc, sbi_inv, "Lender Reversal", 25, 1000, None, "SBI reversed 25% after a valuation re-check."),
		(n6_calc.name, None, "Loan Closure", 100, None, None, "Loan foreclosed within 2 months; full commission returned."),
		(hdfc.name, None, "Duplicate Payment", 10, 0, "Waived", "HDFC agreed to waive the duplicate claim."),
		(s8_calcs[0], sbi_inv, "Early Default", 20, 0, "Disputed", "SBI claims an EMI bounce; borrower paid on day 3."),
		(s8_calcs[1], None, "Other", 5, 0, None, "Rounding difference claimed by SBI; awaiting recovery.")):
		values = {"doctype": "Commission Clawback", "commission_calculation": calc, "commission_invoice": inv, "clawback_reason": reason,
		          "clawback_percentage": pct, "remarks": note}
		if recovered is not None:
			values["recovery_amount"] = recovered
		else:  # full recovery
			values["recovery_amount"] = round(frappe.db.get_value("Commission Calculation", calc, "gross_commission") * pct / 100, 2)
			values["recovery_date"] = today
		if status:
			values["recovery_status"] = status
		auto = frappe.db.get_value("Commission Clawback", {"commission_calculation": calc})  # e.g. created on loan closure
		if auto:
			frappe.get_doc("Commission Clawback", auto).update({k: v for k, v in values.items() if k != "doctype"}).save()
		else:
			new(values)
	say("5 Commission Clawbacks: Partially Recovered, Recovered (commission Reversed), Waived, Disputed, Pending")

	auto_klp = frappe.db.get_value("Franchise Settlement", {"franchise": fr["KLP"], "settlement_period_from": D.month_start})
	if auto_klp:  # drafted automatically when the SBI payout was reconciled
		frappe.get_doc("Franchise Settlement", auto_klp).update({"settlement_status": "Approved", "deductions": 500,
			"remarks": "November share on Ganesh Jadhav's loan (drafted automatically, approved)."}).save()
	for number, code, start, end, status, extra, note in (
		("KLP-SET-2026-10", "KLP", D.last_start, D.last_end, "Paid", {"settlement_date": D.last_end, "payment_reference": "NEFT-DEMO-KLP-10"},
		 "October: no disbursements, nil settlement."),
		("NHD-SET-2026-11", "NHD", D.month_start, D.month_end, "Draft", {}, "Prepared, not yet sent for approval."),
		("NLM-SET-2026-10", "NLM", D.last_start, D.last_end, "Cancelled", {}, "Cancelled - franchise suspended."),
		("AHH-SET-2026-03", "AHH", "2026-03-01", "2026-03-31", "Pending Approval", {}, "Final settlement before termination.")):
		if frappe.db.exists("Franchise Settlement", {"franchise": fr[code], "settlement_period_from": start}):
			continue
		new(dict({"doctype": "Franchise Settlement", "settlement_number": number, "franchise": fr[code], "settlement_period_from": start,
		          "settlement_period_to": end, "settlement_status": status, "remarks": note}, **extra))
	say("5 Franchise Settlements: Draft, Pending Approval, Approved, Paid, Cancelled")


frappe.init(site=sys.argv[1] if len(sys.argv) > 1 else "dsaloan.localhost", sites_path=".")
frappe.connect()
frappe.set_user("Administrator")
try:
	run()
	frappe.db.commit()
	print("\ncommitted")
except Exception:
	frappe.db.rollback()
	print("\nROLLED BACK - nothing saved")
	raise
finally:
	frappe.destroy()
