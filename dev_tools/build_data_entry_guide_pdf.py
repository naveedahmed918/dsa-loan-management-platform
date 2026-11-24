"""PDF 2 - step-by-step guide to entering data by hand, field tables read from the DocType JSON.

Usage: py tools/build_data_entry_guide_pdf.py <module_dir> <output.pdf>   (PREVIEW=1|2 builds only half, for checking)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import CondPageBreak, KeepTogether, PageBreak, SimpleDocTemplate, Spacer  # noqa: E402

from pdfkit_common import (AMBER, WARN_BG, E, P, auto, box, bullets, cover, data_fields, footer, load_doctypes,  # noqa: E402
                           table)

MOD, OUT = sys.argv[1], sys.argv[2]
DOCS = load_doctypes(MOD)
W = A4[0] - 28 * mm


def label(f):
	return f.get("label") or f["fieldname"]


def kind(f):
	t = f["fieldtype"]
	if t == "Select":
		opts = [o for o in (f.get("options") or "").split("\n") if o]
		return "Choice: " + ", ".join(opts[:8]) + (" ..." if len(opts) > 8 else "")
	if t in ("Link", "Table"):
		return f"{t} to {f['options']}"
	if t == "Dynamic Link":
		return "Link chosen by " + f["options"]
	return {"Check": "Tick box", "Small Text": "Text", "Data": "Text", "Int": "Number", "Currency": "Amount (Rs)",
	        "Percent": "Percent", "Attach": "File"}.get(t, t)


def fields_table(dt, examples, notes=None, skip=()):
	"""Every input field of a DocType, in form order: label (* = required), kind, example / what happens."""
	notes = notes or {}
	rows = [["Field", "Type / choices", "What to enter (example)"]]
	for f in data_fields(DOCS[dt]):
		fn = f["fieldname"]
		if fn in skip or f["fieldtype"] == "Table" and fn not in examples:
			continue
		name = E(label(f)) + (' <font color="#c0392b">*</font>' if f.get("reqd") else "")
		if fn in notes:
			what = notes[fn]
		elif f.get("read_only") or f.get("fetch_from"):
			src = f" from {f['fetch_from'].split('.')[0].replace('_', ' ')}" if f.get("fetch_from") else ""
			what = f'<font color="#0f7c74"><b>AUTO</b></font> filled{E(src)}'
		elif fn in examples:
			what = E(examples[fn])
		elif f.get("default"):
			what = "Ticked by default" if f["fieldtype"] == "Check" and str(f["default"]) == "1" else f"Default: {E(f['default'])}"
		else:
			what = '<font color="#5b6b7c">optional</font>'
		rows.append([name, E(kind(f)), what])
	return table(rows, [48 * mm, 62 * mm, W - 110 * mm])


def step(title, intro, dt=None, examples=None, notes=None, skip=(), autos=(), rules=(), extra=()):
	out = [CondPageBreak(60 * mm), P(title, "h2"), P(intro)]
	if dt:
		out += [Spacer(1, 3), P(f"<b>Where:</b> sidebar <b>DSA Loan Portal &gt; {E(dt)}</b> &gt; <b>+ Add</b>. "
		                         "Fields with a red * are required.", "small"), Spacer(1, 3),
		        fields_table(dt, examples or {}, notes, skip)]
	out += list(extra)
	if autos:
		out += [Spacer(1, 4), box([auto(a) for a in autos], width=W)]
	if rules:
		out += [Spacer(1, 4), box([P('<font color="#b45309"><b>Rules to know</b></font>', "body")] + bullets(rules), bg=WARN_BG,
		                          border=AMBER, width=W)]
	out.append(Spacer(1, 8))
	return out


def part1():
	s = cover("DSA Loan Portal", "Data entry guide: every form, step by step",
	          ["Part A sets up the masters once (lenders, products, schemes, slabs, branches, people).",
	           "Part B takes one home loan from first enquiry to commission, settlement and clawback.",
	           "Part C is a quick reference: statuses, what happens automatically, common messages.",
	           "Field tables are read from the live DocType definitions, so they show exactly the fields on each form.",
	           'Look for <font color="#0f7c74"><b>AUTO</b></font>: things the system does by itself after you save.'])
	s += [Spacer(1, 8 * mm), P("Before you start", "h2")]
	s += bullets(["Open <b>http://dsaloan.localhost:8001</b> and sign in. The app is under <b>DSA Loan Portal</b> in the sidebar.",
	              "Keep <b>bench start</b> running: it sends the queued emails and runs the monthly payout job.",
	              "Each user sees only their own branch's records. Administrator and head-office users see everything.",
	              "Amounts are in rupees. Dates are dd-mm-yyyy. Codes (lender, branch, scheme) are turned into capitals on save.",
	              "The masters for SBI, HDFC, ICICI, Axis, LIC HFL and Bank of Baroda already exist. Part A is only needed for a "
	              "new bank or branch."])
	s.append(PageBreak())

	s += [P("Part A - One-time setup (masters)", "h1")]
	s += step("A1. Lender Type", "The kind of institution. Five exist already (Public Sector Bank, Private Sector Bank, Housing "
	          "Finance Company, Small Finance Bank, NBFC).", "Lender Type",
	          {"lender_type_name": "Private Sector Bank", "type_code": "PVT", "description": "Privately owned bank"})
	s += step("A2. Invoice email group for the lender", "Who receives this lender's invoices. Create it before the Lender.",
	          extra=[Spacer(1, 3), table([["Step", "What to do"],
	                                      ["1", "Search bar: <b>Email Group</b> &gt; <b>+ Add</b>. Title e.g. <b>Kotak Bank - Invoices</b>. Save."],
	                                      ["2", "Search bar: <b>Email Group Member</b> &gt; <b>+ Add</b> for each address: Email Group = the group, "
	                                            "Email = the person's address. To stop someone receiving invoices later, tick <b>Unsubscribed</b> on their row."],
	                                      ["3", "Keep 2-3 people per group. An empty group means the invoice email is saved but sent to nobody."]],
	                                     [14 * mm, W - 14 * mm])])
	s += step("A3. Lender", "The bank or housing finance company.", "Lender",
	          {"lender_name": "Kotak Mahindra Bank", "lender_code": "KOTAK (becomes the record name)", "lender_type": "Private Sector Bank",
	           "registered_company_name": "Kotak Mahindra Bank Limited", "pan": "Bank's PAN (10 characters)",
	           "gstin": "Bank's GSTIN (15 characters) - shown on invoices", "official_email": "Bank's official address",
	           "invoice_email_group": "Kotak Mahindra Bank - Invoices (from A2)", "auto_invoice_on_disbursement": "Leave ticked",
	           "invoice_email_template": "Leave empty (uses DSA Disbursement Invoice)", "invoice_cc": "accounts@yourcompany (optional)"},
	          autos=["Lender code and PAN are turned into capitals. The ERPNext Customer for invoicing is created the first time "
	                 "an invoice is raised."],
	          rules=["PAN and GSTIN must have the right format.", "Lender name and code must be unique."])
	s += step("A4. Lender Branch", "The bank office or processing centre you deal with.", "Lender Branch",
	          {"lender_branch_name": "Kotak Home Loans Pune", "branch_code": "PUNHL", "lender": "KOTAK", "branch_type": "Processing Centre",
	           "address_line_1": "Street address", "city": "Pune", "state": "Maharashtra", "pincode": "411001"},
	          rules=["PIN code: 6 digits, not starting with 0.", "Branch code must be unique within the lender."])
	s += step("A5. Loan Product", "What the bank sells (home loan, plot, balance transfer, LAP...). Rates and fees come from "
	          "the bank's published card.", "Loan Product",
	          {"product_name": "Kotak Home Loan", "product_code": "KOTAK_HOME_LOAN", "lender": "KOTAK", "loan_category": "Home Loan",
	           "minimum_loan_amount": "500000", "maximum_loan_amount": "100000000", "maximum_tenure_months": "360",
	           "minimum_interest_rate": "8.10", "maximum_interest_rate": "9.40", "interest_type": "Floating", "repayment_type": "EMI",
	           "processing_fee_type": "Percentage", "processing_fee": "0.50", "minimum_processing_fee": "5000",
	           "maximum_processing_fee": "25000", "effective_from": "Date of the rate card", "rates_as_on": "Date of the rate card",
	           "rate_source": "Link to the bank's rate page"},
	          rules=["Minimum must not be above maximum (amount, tenure, rate, fee).",
	                 "An application's amount and tenure must stay inside these limits (when filled)."])
	s += step("A6. Loan Scheme", "A named offer under a product (e.g. MaxGain, Reach, Griha Suvidha) with its own limits.",
	          "Loan Scheme",
	          {"scheme_name": "Kotak Salaried Home Loan", "scheme_code": "KOTAK_SAL", "lender": "KOTAK", "loan_product": "KOTAK_HOME_LOAN",
	           "effective_from": "Start date", "scheme_status": "Active", "maximum_ltv": "80 (optional, % of property value)",
	           "minimum_credit_score": "700 (optional)", "maximum_tenure_months": "300"},
	          rules=["The product must belong to the same lender.", "Maximum LTV here is applied on top of RBI's 90 / 80 / 75 % limits."])
	s += step("A7. Commission Slab Structure", "Your agreed payout with the bank. The Commission % here is copied into every "
	          "commission automatically.", "Commission Slab Structure",
	          {"slab_name": "Kotak Mahindra Bank - standard", "lender": "KOTAK", "calculation_basis": "Disbursed Amount",
	           "commission_percentage": "0.50 (your agreed %)", "gst_rate": "18", "tds_rate": "2",
	           "clawback_window_months": "6 (if the bank claws back on early closure)", "clawback_percentage": "100",
	           "effective_from": "Agreement start", "slab_status": "Active"},
	          notes={"loan_product": "Leave empty for all products, or pick one for a product-specific rate",
	                 "loan_scheme": "Leave empty, or pick one for a scheme-specific rate"},
	          rules=["Only one Active slab may cover the same lender / product / scheme and dates.",
	                 "The most specific Active slab wins: scheme, then product, then lender-wide."])
	s += step("A8. Lender Document Rule", "Extra documents this bank asks for, beyond the 13 standard rows every checklist has.",
	          "Lender Document Rule",
	          {"rule_name": "Kotak - Approved building plan", "lender": "KOTAK", "loan_product": "KOTAK_HOME_LOAN",
	           "applicant_type": "Property Owner (property papers) / Primary Applicant / All", "employment_type": "Leave empty for everyone",
	           "property_type": "Flat (optional)", "document_category": "Property", "document_name": "Approved building plan",
	           "is_mandatory": "Tick if required", "is_active": "Ticked"},
	          rules=["Do not add PAN, Aadhaar, address proof, bank statement, salary slips, ITR or Form 16: they are already standard rows.",
	                 "Use Property Owner for property papers so co-applicants are not asked for them."])
	s += step("A9. Franchise", "A partner office that brings loans and earns a share of the commission.", "Franchise",
	          {"franchise_name": "Baner Loan Desk", "franchise_code": "BLD", "franchise_owner": "Owner's name", "company": "DSA Loan Services",
	           "contact_number": "9822012345", "settlement_percentage": "40", "franchise_status": "Active",
	           "agreement_start_date": "Start", "agreement_end_date": "End"},
	          rules=["Mobile: 10 digits starting 6-9 (+91 and spaces are removed)."])
	s += step("A10. DSA Branch", "Your own office or a franchise's office. Every lead and application belongs to one.",
	          "DSA Branch",
	          {"branch_name": "Baner Franchise Branch", "branch_code": "BLD-PUN-01", "branch_type": "Franchise Owned",
	           "franchise": "BLD (required for franchise branches)", "company": "DSA Loan Services", "branch_manager": "An Employee",
	           "address_line_1": "Street", "city": "Pune", "state": "Maharashtra", "pincode": "411045", "branch_status": "Active"},
	          autos=["Users already given the franchise automatically get access to its new branch."])
	s += step("A11. Employees, users and branch access", "Staff are ERPNext Employees; logins are Users.",
	          extra=[Spacer(1, 3), table([["Step", "Where", "What to enter"],
	                                      ["1", "Employee &gt; + Add", "First Name, Gender, Date of Birth, Date of Joining, Company. Used as agent / branch manager."],
	                                      ["2", "User &gt; + Add", "Email, First Name. Save, then add roles: DSA Agent, Branch Manager, Document Verifier, "
	                                                             "DSA Accounts, Franchise Partner or DSA Admin. Set the password from the user's menu."],
	                                      ["3", "Employee", "Set <b>User ID</b> to the new user so the person and the login are linked."],
	                                      ["4", "User Permission &gt; + Add", "User = the person, Allow = <b>DSA Branch</b>, For Value = their branch, tick "
	                                                                         "<b>Apply To All Document Types</b>. Franchise partners also get Allow = <b>Franchise</b>."],
	                                      ["5", "-", "No User Permission = sees every branch (head office, accounts)."]],
	                                     [12 * mm, 38 * mm, W - 50 * mm])])
	s += step("A12. Lender Login", "Which employee uses which bank portal. Never type passwords here.", "Lender Login",
	          {"login_title": "Kotak portal - Rahul", "lender": "KOTAK", "portal_name": "Kotak DSA Connect", "login_username": "lfs.rahul",
	           "assigned_employee": "Rahul Kulkarni", "access_type": "Individual", "access_status": "Active"},
	          autos=["Status becomes Expired when the Access End Date has passed."],
	          rules=["The same username cannot be Active twice for one bank."])
	return s


def part2():
	s = [PageBreak(), P("Part B - One loan, from enquiry to settlement", "h1"),
	     P("The example follows a Rs 40 lakh SBI home loan for a salaried customer at the Pune branch, with the sample "
	       "SBI commission of 0.40 %.")]
	s += step("B1. Loan Lead (the enquiry)", "Record every enquiry, even if it never becomes a loan.", "Loan Lead",
	          {"lead_title": "Home loan - Test Customer", "customer_name": "Test Customer", "mobile_number": "9876543210",
	           "lead_status": "New, then Contacted / Interested / Qualified as it progresses", "customer_consent": "Tick (agreed to be contacted)",
	           "lead_source": "Walk-in", "loan_type": "Home Loan", "estimated_loan_amount": "4000000", "employment_type": "Salaried",
	           "assigned_company": "DSA Loan Services", "dsa_branch": "LFS-PUN-01", "assigned_agent": "Rahul Kulkarni",
	           "next_follow_up_date": "When to call back"},
	          rules=["You cannot set Converted by hand: use the Convert to Customer button.",
	                 "A warning appears if another open lead has the same mobile number."])
	s += step("B2. Convert to Customer", "On the lead click <b>Convert to Customer</b>. The Loan Customer opens; complete it and save.",
	          "Loan Customer",
	          {"customer_name": "Filled from the lead", "mobile_number": "Filled from the lead",
	           "dsa_branch": "Filled from the lead", "date_of_birth": "12-03-1990", "gender": "Male", "pan": "ABCPT1234K", "kyc_consent": "Tick", "consent_mode": "Signed Form",
	           "consent_proof": "Attach the signed form", "aadhaar_number": "Type all 12 digits", "cibil_score": "760",
	           "cibil_report_date": "Date of the report", "employment_type": "Salaried", "employer_business_name": "Employer",
	           "monthly_income": "145000", "existing_emi": "8000", "kyc_status": "Verified once KYC is checked"},
	          autos=["The customer gets the lead's DSA branch.", "Aadhaar is stored only as XXXX-XXXX-1234.",
	                 "Consent Date is filled when consent is ticked."],
	          rules=["Aadhaar or CIBIL score cannot be saved before KYC & Credit Check Consent is ticked.",
	                 "CIBIL score 300-900 (or -1 for no history) and it needs a report date, not in the future.",
	                 "Consent is on the <b>customer</b>, not the application. The lead's tick box does not count."])
	s += step("B3. Loan Application", "On the customer or from <b>Loan Application &gt; + Add</b>.", "Loan Application",
	          {"loan_lead": "The lead from B1", "primary_customer": "The customer from B2", "lender": "SBI", "lender_branch": "SBI RACPC Pune",
	           "loan_product": "SBI_HOME_LOAN", "loan_scheme": "SBI_HOME_LOAN_SCHEME", "loan_type": "Home Loan", "company": "DSA Loan Services",
	           "dsa_branch": "LFS-PUN-01", "assigned_agent": "Rahul Kulkarni", "requested_loan_amount": "4000000",
	           "requested_tenure_months": "240", "expected_interest_rate": "7.75", "loan_purpose": "Purchase", "property_type": "Flat",
	           "property_value": "6000000", "property_pincode": "411045", "co_applicants": "Add a row per co-applicant / guarantor",
	           "final_status": "Draft (move it forward in B5)"},
	          notes={"application_status": "<font color='#0f7c74'><b>AUTO</b></font> follows the Final Status"},
	          skip=("lender_application_number", "lender_submission_date", "sanction_date", "sanctioned_amount", "sanctioned_interest_rate",
	                "sanctioned_tenure_months", "sanction_valid_until", "rejection_reason", "manager_approval", "workflow_state"),
	          autos=["Estimated EMI is calculated.", "One Document Checklist is created per applicant (primary, co-applicants, guarantors).",
	                 "The lead becomes Converted."],
	          rules=["Product, scheme and lender branch must belong to the chosen lender.",
	                 "Amount and tenure must be inside the product and scheme limits.",
	                 "RBI limit: the loan may be at most 90 % of the property value up to Rs 30 lakh, 80 % up to Rs 75 lakh, 75 % above "
	                 "(Home Loan, Home Purchase, Balance Transfer). Example: 60 lakh on a 60 lakh flat is rejected."])
	s += step("B4. Documents", "Click <b>Document Checklist</b> on the application. Each applicant's checklist has 13 standard rows "
	          "plus the bank's own rows. For every document, create its data record and then mark the row.",
	          extra=[Spacer(1, 3), table([["Document", "Create", "Key fields"],
	                                      ["Aadhaar", "Aadhaar Card Data", "Document Checklist, Aadhaar Last 4 (only 4 digits), name, DOB"],
	                                      ["PAN", "PAN Card Data", "Document Checklist, PAN Number, name on card"],
	                                      ["Address proof", "Address Proof Data", "Proof type, name, address, document date"],
	                                      ["Bank statement", "Bank Statement Data", "Bank, account last 4, Period From / To (6 full months)"],
	                                      ["Salary slips", "Salary Slip Data x 3", "Salary month (3 different months), gross, net"],
	                                      ["Form 16", "Form 16 Data x 3", "Assessment year (3 different), employee PAN = PAN card"],
	                                      ["ITR", "ITR Data x 3", "Assessment year, total income (self-employed applicants)"]],
	                                     [30 * mm, 38 * mm, W - 68 * mm]),
	                 Spacer(1, 3), P("Set <b>Extraction Status</b> to Verified on each record. Then on the checklist set rows to "
	                                 "<b>Verified</b>, and for a salaried applicant set the ITR rows to <b>Not Applicable</b> "
	                                 "(Form 16 is accepted). Rows for paper documents (bank's rules) are marked directly.")],
	          autos=["Each record links itself to the first free matching row and marks it Received.",
	                 "Bank statement months are counted from the period."],
	          rules=["A row with a document type can only be Verified once its record is linked.",
	                 "The bank statement must cover at least 6 months to be Verified.",
	                 "Salary months / assessment years must be different; Form 16 PAN must match the PAN card.",
	                 "Deleting a record that backs a Verified row is refused: set the row back to Pending first."])
	s += step("B5. Move the application forward", "Change <b>Final Status</b> on the application and save after each step.",
	          extra=[Spacer(1, 3), table([["Status", "Also fill", "Notes"],
	                                      ["Documents Pending", "-", "Collecting documents"],
	                                      ["Ready for Submission", "-", "Refused until every applicant has consent on their customer record"],
	                                      ["Submitted", "Lender Application Number, Lender Submission Date", "Warning if CIBIL report is missing or older than 30 days"],
	                                      ["Under Review", "-", "Bank is assessing"],
	                                      ["Query Raised / On Hold", "Application Remarks", "Bank asked for more / paused"],
	                                      ["Sanctioned", "Sanction Date, Sanctioned Amount (+ rate, tenure, valid until)", "Sanctioned amount also checked against the RBI limit"],
	                                      ["Rejected", "Rejection Reason", "End of the road"],
	                                      ["Withdrawn", "Application Remarks", "Customer pulled out"]],
	                                     [38 * mm, 62 * mm, W - 100 * mm])],
	          autos=["Application Status (Open / In Progress / On Hold / Completed / Cancelled) follows the Final Status."])
	s += step("B6. Disbursement - this is where the automation starts",
	          "When the application is Sanctioned, click <b>New Disbursement</b>. Record each tranche the bank releases.",
	          "Loan Disbursement",
	          {"loan_application": "Filled by the button", "disbursement_number": "1 (2, 3... for later tranches)",
	           "disbursement_date": "Date the bank paid", "disbursement_type": "Full (all at once) / Part / Final (last tranche)",
	           "disbursement_status": "Confirmed (only Confirmed counts; Draft, Pending, Failed do not)",
	           "current_disbursement_amount": "4000000", "beneficiary_name": "Seller / builder", "payment_mode": "RTGS",
	           "payment_reference": "UTR number"},
	          autos=["Application becomes Disbursed (Full / Final or balance 0) or Partially Disbursed.",
	                 "Commission Calculation is created: 0.40 % x 40,00,000 = Rs 16,000; GST 18 % Rs 2,880; TDS 2 % Rs 320; net Rs 18,560.",
	                 "When fully disbursed: ERPNext Sales Invoice to SBI, Rs 16,000 + CGST 1,440 + SGST 1,440 = Rs 17,280, due in 30 days.",
	                 "Commission Invoice is created and linked; the commission becomes Invoiced.",
	                 "Email 'Loan Disbursed: ...' with the invoice PDF goes to the SBI invoice email group. See the application's "
	                 "Lender Invoice section and its timeline."],
	          rules=["The application must be Sanctioned or Partially Disbursed.",
	                 "The disbursement number must be unique for the application; the total may not exceed the sanctioned amount.",
	                 "A Confirmed amount cannot be changed: mark it Reversed and add a new one.",
	                 "Part tranches: the invoice waits for the Final tranche and then covers all of them."])
	s += step("B7. Lender payout (what the bank paid)",
	          "On the 1st of each month a statement per bank is created with the expected commission. Open it from "
	          "<b>Lender Payout Statement</b> when the bank's statement or payment arrives.",
	          "Lender Payout Statement",
	          {"statement_number": "Filled by the monthly job, e.g. AUTO-SBI-2026-11", "lender": "Filled by the job",
	           "statement_date": "Filled by the job", "period_from": "Filled: first day of the month",
	           "period_to": "Filled: last day of the month", "reconciliation_status": "Set for you (Disputed / Closed by hand)",
	           "total_lender_commission": "As per the bank's statement (pre-filled with the expected amount)",
	           "total_tds": "As per the bank's statement (pre-filled)", "actual_received_amount": "15680 (what reached your bank)",
	           "payment_date": "Credit date", "bank_reference": "NEFT / UTR reference", "statement_attachment": "Bank's statement PDF"},
	          autos=["Matched when the bank's commission equals the expected amount and the money received equals Net Payable "
	                 "(within Rs 1): commissions become Paid.",
	                 "Otherwise Partially Matched: commissions become Partially Paid; if the bank stated less commission than "
	                 "expected a Debit Note (Draft) is created.",
	                 "Franchise Settlement (Draft) is created for franchise loans in that month.",
	                 "A commission that arrives after a month is reconciled goes to a new top-up statement next time the job runs."])
	s += step("B8. Franchise settlement (franchise loans only)",
	          "Open the draft created in B7 from <b>Franchise Settlement</b>.", "Franchise Settlement",
	          {"settlement_number": "Filled, e.g. AUTO-KLP-2026-11", "franchise": "Filled",
	           "settlement_period_from": "Filled", "settlement_period_to": "Filled",
	           "deductions": "Agreed deductions (e.g. marketing)", "gst_amount": "If the franchise is GST registered",
	           "tds_amount": "TDS you deduct", "settlement_status": "Draft > Pending Approval > Approved > Paid",
	           "settlement_date": "Required for Paid", "payment_reference": "Your payment reference"},
	          autos=["Total Gross Commission = the franchise's commissions received in the period; Share = that x the "
	                 "franchise's % (e.g. 40 %); Net Payable = share - deductions + GST - TDS."],
	          rules=["A franchise can be settled only once for any period (overlaps are refused)."])
	s += step("B9. Clawback (bank takes commission back)",
	          "Automatic when a loan is closed early; or add one by hand from <b>Commission Clawback &gt; + Add</b> for any other reason.",
	          "Commission Clawback",
	          {"commission_calculation": "The commission concerned", "clawback_reason": "Loan Closure / Early Default / Lender Reversal ...",
	           "clawback_percentage": "Enter the % or the amount - the other is calculated",
	           "clawback_amount": "Enter the amount or the % - the other is calculated", "recovery_amount": "What has been returned",
	           "recovery_date": "When", "recovery_status": "Waived / Disputed by hand; others are set for you"},
	          autos=["Setting the application to Closed within the slab's clawback window (sample 6 months) creates a 100 % "
	                 "Clawback for each commission on the loan.",
	                 "Every clawback creates a Credit Note (Draft) under Commission Invoice.",
	                 "Recovery status: Pending, Partially Recovered or Recovered from the amounts; a full 100 % recovery marks the "
	                 "commission Reversed."],
	          rules=["The clawback cannot be more than the original commission; recovery cannot be more than the clawback."])
	return s


def part3():
	s = [PageBreak(), P("Part C - Quick reference", "h1"), P("What staff do and what the system does", "h2")]
	s.append(table([["You do", "The system then does"],
	                ["Save a Loan Application", "Creates a Document Checklist per applicant"],
	                ["Save a document-data record", "Links it to its checklist row (Received)"],
	                ["Mark a tranche Confirmed", "Commission Calculation; when fully disbursed: Sales Invoice with GST, Commission Invoice, email to the bank"],
	                ["(1st of every month)", "Lender Payout Statement per bank with the expected commission"],
	                ["Enter the amount received on a statement", "Matches it, marks commissions Paid, drafts Franchise Settlement / Debit Note"],
	                ["Set an application to Closed early", "Commission Clawback and Credit Note"],
	                ["Create a clawback by hand", "Credit Note"]], [70 * mm, W - 70 * mm]))
	s += [P("Statuses", "h2"), table([
		["Form", "Statuses"],
		["Loan Lead", "New, Contacted, Interested, Qualified, Converted, Not Interested, Lost"],
		["Loan Application", "Draft, Documents Pending, Ready for Submission, Submitted, Under Review, Query Raised, Sanctioned, Rejected, "
		                     "On Hold, Partially Disbursed, Disbursed, Withdrawn, Closed"],
		["Checklist row", "Pending, Received, Under Verification, Verified, Rejected, Resubmission Required, Not Applicable"],
		["Loan Disbursement", "Draft, Pending, Confirmed, Failed, Reversed"],
		["Commission Calculation", "Draft, Calculated, Approved, Invoiced, Partially Paid, Paid, Reversed"],
		["Commission Invoice", "Draft, Pending Approval, Submitted, Partially Paid, Paid, Cancelled"],
		["Lender Payout Statement", "Draft, Pending Reconciliation, Matched, Partially Matched, Disputed, Closed"],
		["Commission Clawback", "Pending, Partially Recovered, Recovered, Waived, Disputed"],
		["Franchise Settlement", "Draft, Pending Approval, Approved, Partially Paid, Paid, Cancelled"]], [42 * mm, W - 42 * mm])]
	s += [P("Messages you may see", "h2"), table([
		["Message", "What to do"],
		["Record KYC & credit check consent on CUST-... before marking the application ...", "Open each listed customer, tick consent, choose the mode, save."],
		["The requested amount is ...% of the property value; the limit is ...%", "Lower the amount or correct the property value."],
		["Loan Product ... lends at most ...", "Choose another product / scheme or change the amount."],
		["Loan Application ... must be Sanctioned before disbursement", "Finish B5 first."],
		["Row n: link the extracted ... before marking ... Verified", "Create the document-data record for that row first."],
		["No active Commission Slab Structure for ...", "Add or activate the bank's slab (A7), then create the commission by hand."],
		["Invoice status Email Pending", "Add members to the bank's invoice email group, then Lender Invoice > Send Invoice Email."],
		["... must be a valid 6-digit PIN code", "Correct the PIN code."]], [95 * mm, W - 95 * mm])]
	s += [P("Useful places", "h2")]
	s += bullets(["Application: <b>Lender Invoice</b> section (invoice, status, recipients) and the <b>Lender Invoice</b> button menu "
	              "(Open Sales Invoice, Send Invoice Email).",
	              "Emails: the timeline at the bottom of the application, Sales Invoice and Lender.",
	              "Accounts: <b>Sales Invoice</b> (ERPNext) for the GST invoices; <b>Commission Invoice</b> for notes.",
	              "Run the monthly payout job early (Windows PowerShell): see the 'How it was built' PDF, section Commands."])
	return s


def main():
	part = os.environ.get("PREVIEW")
	story = (part1() if part in (None, "1") else []) + (part2() + part3() if part in (None, "2") else [])
	doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=16 * mm, bottomMargin=15 * mm,
	                        title="DSA Loan Portal - Data Entry Guide", author="DSA Loan Portal")
	doc.build(story, onFirstPage=footer("Data Entry Guide"), onLaterPages=footer("Data Entry Guide"))
	print("Wrote", OUT)


if __name__ == "__main__":
	main()
