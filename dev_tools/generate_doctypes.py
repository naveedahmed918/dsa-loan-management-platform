"""Generate Frappe v15 DocType files for the DSA Loan module.

Usage:  python generate_doctypes.py [output_dir] [module_name]
Default output: ../dsa_loan  (a module folder you copy into your app)
Each DocType gets <scrubbed_name>/{__init__.py, <name>.json, <name>.py}.
"""
import json
import os
import sys
from datetime import datetime

MODULE = sys.argv[2] if len(sys.argv) > 2 else "DSA Loan Portal"
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "dsa_loan")
# "modified" must be newer than the database copy, or `bench migrate` skips existing DocTypes.
TS = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

UPPER = {"pan", "gstin", "ifsc", "emi", "cibil", "dsa", "utr", "tds", "gst", "cgst", "sgst",
         "igst", "ltv", "foir", "rm", "tat", "pdf", "id", "kyc", "erpnext"}


def label(fn):
    return " ".join(w.upper() if w in UPPER else w.capitalize() for w in fn.split("_"))


def F(name, ftype, options=None, reqd=0, ro=0, fetch=None, depends=None, mand=None,
      unique=0, default=None, lst=0, lbl=None, **extra):
    d = {"fieldname": name, "fieldtype": ftype, "label": lbl or label(name)}
    if options:
        d["options"] = "\n".join(options) if isinstance(options, list) else options
    if reqd: d["reqd"] = 1
    if ro: d["read_only"] = 1
    if fetch: d["fetch_from"] = fetch
    if depends: d["depends_on"] = depends
    if mand: d["mandatory_depends_on"] = mand
    if unique: d["unique"] = 1
    if default is not None: d["default"] = default
    if lst: d["in_list_view"] = 1
    d.update(extra)
    return d


def S(lbl=None, collapsible=0, description=None):
    d = {"fieldtype": "Section Break", "label": lbl, "collapsible": collapsible}
    if description:
        d["description"] = description
    return d


def C():
    return {"fieldtype": "Column Break"}


def st(field, value):
    return f"eval:doc.{field}=='{value}'"


def series(prefix):
    return F("naming_series", "Select", [prefix], reqd=1, default=prefix, lbl="Series")


EMAIL = "Email"
PAY_MODE = ["NEFT", "RTGS", "IMPS", "Cheque", "Other"]
LOAN_CATEGORY = ["Home Purchase", "Home Loan", "Home Improvement", "Loan Against Property", "Balance Transfer",
                 "Plot Purchase", "Plot + Construction"]
# Employment Type / Property Type masters do not exist on the site, so these are Select fields.
EMPLOYMENT = ["", "Salaried", "Self Employed", "Business Owner", "Professional"]
PROPERTY = ["", "Flat", "Independent House", "Villa", "Plot", "Commercial", "Other"]
KYC = ["Pending", "In Progress", "Verified", "Rejected"]

# Fields follow DSA_Home_Loan_Blueprint.pdf. The Blueprint's Table fields to Commission Slab Detail,
# Commission Invoice Item, Lender Payout Item and Franchise Settlement Item are left out on purpose:
# Co-Applicant is the only child table.
# name -> dict(fields, autoname, title, istable, submittable, search, track)
D = {}

# ---------------- PART A: MASTERS ----------------
D["Lender Type"] = dict(autoname="field:lender_type_name", fields=[
    F("lender_type_name", "Data", reqd=1, unique=1, lst=1),
    F("type_code", "Data", reqd=1, unique=1, lst=1),
    F("description", "Small Text"),
    F("is_active", "Check", default="1", lst=1),
])

D["Lender"] = dict(autoname="field:lender_code", title="lender_name", search="lender_name", fields=[
    F("lender_name", "Data", reqd=1, unique=1, lst=1),
    F("lender_code", "Data", reqd=1, unique=1),
    F("lender_type", "Link", "Lender Type", reqd=1, lst=1),
    F("registered_company_name", "Data"),
    F("rbi_registration_number", "Data", lbl="RBI Registration Number"),
    C(),
    F("pan", "Data", permlevel=1),
    F("gstin", "Data"),
    F("website", "Data"),
    F("lender_status", "Select", ["Active", "Inactive", "Suspended"], reqd=1, default="Active", lst=1),
    S("Contact"),
    F("head_office_address", "Link", "Address"),
    F("contact_person", "Data"),
    C(),
    F("contact_number", "Data"),
    F("official_email", "Data", EMAIL),
    S("Invoicing & Email", description="Used when a loan is fully disbursed: a Sales Invoice is raised on the "
      "lender and emailed to the email group"),
    F("erpnext_customer", "Link", "Customer", lbl="ERPNext Customer",
      description="Billing customer for Sales Invoices; created automatically if empty"),
    F("auto_invoice_on_disbursement", "Check", default="1", lbl="Auto Invoice on Disbursement"),
    C(),
    F("invoice_email_group", "Link", "Email Group", lbl="Invoice Email Group",
      description="Everyone in this group (not unsubscribed) receives the invoice. Official Email is used only when no group is set"),
    F("invoice_email_template", "Link", "Email Template",
      description="Leave empty to use 'DSA Disbursement Invoice'"),
    F("invoice_cc", "Small Text", lbl="Invoice CC", description="Extra addresses, comma separated"),
    S(),
    F("remarks", "Small Text"),
])

D["Lender Branch"] = dict(autoname="format:LBR-{#####}", title="lender_branch_name", search="lender_branch_name,lender", fields=[
    F("lender_branch_name", "Data", reqd=1, lst=1),
    F("branch_code", "Data", reqd=1),
    F("lender", "Link", "Lender", reqd=1, lst=1),
    F("branch_type", "Select", ["Head Office", "Regional Office", "Zonal Office", "Branch", "Processing Centre"], reqd=1),
    F("is_active", "Check", default="1"),
    S("Address"),
    F("address_line_1", "Data", reqd=1),
    F("address_line_2", "Data"),
    F("city", "Data", reqd=1, lst=1),
    C(),
    F("district", "Data"),
    F("state", "Data", reqd=1),
    F("pincode", "Data", reqd=1),
    S("Contact"),
    F("branch_manager_name", "Data"),
    C(),
    F("contact_number", "Data"),
    F("email", "Data", EMAIL),
])

D["Loan Product"] = dict(autoname="field:product_code", title="product_name", search="product_name,lender", fields=[
    F("product_name", "Data", reqd=1, lst=1),
    F("product_code", "Data", reqd=1, unique=1),
    F("lender", "Link", "Lender", reqd=1, lst=1),
    F("loan_category", "Select", LOAN_CATEGORY, reqd=1, lst=1),
    F("is_active", "Check", default="1"),
    S("Limits"),
    F("minimum_loan_amount", "Currency"), F("maximum_loan_amount", "Currency"),
    F("minimum_tenure_months", "Int"), F("maximum_tenure_months", "Int"),
    C(),
    F("minimum_interest_rate", "Percent"), F("maximum_interest_rate", "Percent"),
    F("interest_type", "Select", ["", "Fixed", "Floating", "Hybrid"]),
    F("repayment_type", "Select", ["", "EMI", "Other"]),
    S("Fees & Validity"),
    F("processing_fee_type", "Select", ["", "Fixed", "Percentage"]),
    F("processing_fee", "Currency", description="Rupees for Fixed; percent of the loan amount for Percentage"),
    F("minimum_processing_fee", "Currency", depends="eval:doc.processing_fee_type=='Percentage'"),
    F("maximum_processing_fee", "Currency", depends="eval:doc.processing_fee_type=='Percentage'"),
    C(),
    F("effective_from", "Date"), F("effective_to", "Date"),
    F("rates_as_on", "Date", description="Date of the bank's published rate card these figures come from"),
    F("rate_source", "Data", description="Link to the bank's published rates / charges"),
    S(),
    F("product_description", "Small Text"),
])

D["Loan Scheme"] = dict(autoname="field:scheme_code", title="scheme_name", search="scheme_name,lender", fields=[
    F("scheme_name", "Data", reqd=1, lst=1),
    F("scheme_code", "Data", reqd=1, unique=1),
    F("lender", "Link", "Lender", reqd=1, lst=1),
    F("loan_product", "Link", "Loan Product", reqd=1, lst=1),
    C(),
    F("effective_from", "Date", reqd=1),
    F("effective_to", "Date"),
    F("scheme_status", "Select", ["Draft", "Active", "Inactive", "Expired"], reqd=1, default="Draft", lst=1),
    F("scheme_description", "Small Text"),
    S("Eligibility"),
    F("applicant_category", "Select", ["", "Salaried", "Self Employed", "Business Owner", "Professional", "All"]),
    F("minimum_age", "Int"), F("maximum_age", "Int"),
    F("minimum_monthly_income", "Currency"),
    F("minimum_credit_score", "Int"),
    F("maximum_ltv", "Percent", lbl="Maximum LTV"),
    F("maximum_foir", "Percent", lbl="Maximum FOIR"),
    C(),
    F("minimum_loan_amount", "Currency"), F("maximum_loan_amount", "Currency"),
    F("minimum_interest_rate", "Percent"), F("maximum_interest_rate", "Percent"),
    F("minimum_tenure_months", "Int"), F("maximum_tenure_months", "Int"),
    S(),
    F("remarks", "Small Text"),
])

D["Commission Slab Structure"] = dict(autoname="format:CSS-{#####}", title="slab_name", search="slab_name,lender", fields=[
    F("slab_name", "Data", reqd=1, lst=1),
    F("lender", "Link", "Lender", reqd=1, lst=1),
    F("loan_product", "Link", "Loan Product", lst=1),
    F("loan_scheme", "Link", "Loan Scheme"),
    C(),
    F("calculation_basis", "Select", ["Disbursed Amount", "Sanctioned Amount", "Fixed Amount"], reqd=1, default="Disbursed Amount"),
    F("commission_percentage", "Percent", lbl="Commission %",
      description="Agreed payout; copied into each new Commission Calculation (still editable there)"),
    F("gst_rate", "Percent", default="18", lbl="GST Rate",
      description="GST charged on the commission; copied into each new Commission Calculation"),
    F("tds_rate", "Percent", default="2", lbl="TDS Rate",
      description="TDS the lender deducts (section 194H); copied into each new Commission Calculation"),
    S("Clawback", description="If the loan is closed within this many months of disbursement, a Commission Clawback is created automatically"),
    F("clawback_window_months", "Int", lbl="Clawback Window (Months)"),
    C(),
    F("clawback_percentage", "Percent", lbl="Clawback %", depends="eval:doc.clawback_window_months"),
    S(),
    F("effective_from", "Date", reqd=1), F("effective_to", "Date"),
    F("slab_status", "Select", ["Draft", "Active", "Inactive", "Expired"], reqd=1, default="Draft", lst=1),
    S(),
    F("remarks", "Small Text"),
])

D["Lender Document Rule"] = dict(autoname="format:LDR-{#####}", title="rule_name", search="rule_name,lender,document_name", fields=[
    F("rule_name", "Data", reqd=1, lst=1),
    F("lender", "Link", "Lender", reqd=1, lst=1),
    F("loan_product", "Link", "Loan Product"),
    F("loan_scheme", "Link", "Loan Scheme"),
    F("is_active", "Check", default="1"),
    C(),
    F("applicant_type", "Select", ["Primary Applicant", "Co-Applicant", "Guarantor", "Property Owner", "All"], reqd=1, lst=1),
    F("employment_type", "Select", EMPLOYMENT),
    F("property_type", "Select", PROPERTY),
    S("Document"),
    F("document_category", "Select", ["Identity", "Address", "Income", "Employment", "Banking", "Property", "Legal", "Other"], reqd=1),
    F("document_name", "Data", reqd=1, lst=1),
    F("is_mandatory", "Check", default="1"),
    F("verification_required", "Check", default="1"),
    C(),
    F("accepted_format", "Data"),
    F("validity_period_days", "Int"),
    F("remarks", "Small Text"),
])

D["DSA Branch"] = dict(autoname="field:branch_code", title="branch_name", search="branch_name", fields=[
    F("branch_name", "Data", reqd=1, lst=1),
    F("branch_code", "Data", reqd=1, unique=1),
    F("branch_type", "Select", ["Company Owned", "Franchise Owned", "Franchise Operated"], reqd=1, default="Company Owned"),
    F("franchise", "Link", "Franchise"),
    F("company", "Link", "Company", reqd=1),
    C(),
    F("branch_manager", "Link", "Employee"),
    F("contact_number", "Data"),
    F("email", "Data", EMAIL),
    F("opening_date", "Date"),
    F("branch_status", "Select", ["Active", "Inactive", "Closed"], reqd=1, default="Active", lst=1),
    S("Address"),
    F("address_line_1", "Data", reqd=1),
    F("address_line_2", "Data"),
    C(),
    F("city", "Data", reqd=1, lst=1), F("state", "Data", reqd=1), F("pincode", "Data", reqd=1),
])

D["Franchise"] = dict(autoname="field:franchise_code", title="franchise_name", search="franchise_name,franchise_owner", fields=[
    F("franchise_name", "Data", reqd=1, lst=1),
    F("franchise_code", "Data", reqd=1, unique=1),
    F("franchise_owner", "Data", reqd=1),
    F("company", "Link", "Company", reqd=1),
    F("owner_employee", "Link", "Employee"),
    C(),
    F("contact_number", "Data", reqd=1, lst=1),
    F("email", "Data", EMAIL),
    F("registered_address", "Link", "Address"),
    F("franchise_status", "Select", ["Active", "Inactive", "Suspended", "Terminated"], reqd=1, default="Active", lst=1),
    S("Tax & Agreement"),
    F("pan", "Data", permlevel=1),
    F("gstin", "Data"),
    C(),
    F("agreement_start_date", "Date"), F("agreement_end_date", "Date"),
    F("settlement_percentage", "Percent"),
    S(),
    F("remarks", "Small Text"),
])

# ---------------- PART B: TRANSACTIONS ----------------
D["Loan Lead"] = dict(autoname="format:LEAD-{YYYY}-{#####}", title="lead_title", search="customer_name,mobile_number", track=1, fields=[
    F("lead_title", "Data", reqd=1, lst=1),
    F("lead_date", "Date", reqd=1, default="Today"),
    F("customer_name", "Data", reqd=1, lst=1),
    F("mobile_number", "Data", reqd=1, lst=1),
    F("alternate_mobile", "Data"),
    F("email", "Data", EMAIL),
    F("city", "Data"),
    C(),
    F("lead_status", "Select", ["New", "Contacted", "Interested", "Qualified", "Converted", "Not Interested", "Lost"],
      reqd=1, default="New", lst=1),
    F("next_follow_up_date", "Date"),
    F("customer_consent", "Check", description="Customer consented to be contacted and to data processing"),
    S("Requirement"),
    F("lead_source", "Select", ["Website", "Referral", "Agent", "Walk-in", "Advertisement", "Partner", "Other"], reqd=1),
    F("loan_type", "Select", LOAN_CATEGORY, reqd=1, lst=1),
    C(),
    F("estimated_loan_amount", "Currency"),
    F("employment_type", "Select", EMPLOYMENT),
    S("Assignment"),
    F("assigned_company", "Link", "Company", reqd=1),
    F("dsa_branch", "Link", "DSA Branch", reqd=1),
    C(),
    F("assigned_agent", "Link", "Employee"),
    F("branch_manager", "Link", "Employee"),
    S(),
    F("remarks", "Small Text"),
])

D["Loan Customer"] = dict(autoname="format:CUST-{YYYY}-{#####}", title="customer_name", search="customer_name,mobile_number", track=1, fields=[
    F("customer_name", "Data", reqd=1, lst=1),
    F("mobile_number", "Data", reqd=1, lst=1),
    F("alternate_mobile", "Data"),
    F("email", "Data", EMAIL),
    C(),
    F("date_of_birth", "Date"),
    F("gender", "Select", ["", "Male", "Female", "Other", "Prefer not to say"]),
    F("marital_status", "Select", ["", "Single", "Married", "Divorced", "Widowed"]),
    F("customer_category", "Select", ["", "Resident Individual", "NRI", "Company"]),
    F("kyc_status", "Select", KYC, reqd=1, default="Pending", lst=1),
    F("customer_status", "Select", ["Active", "Inactive", "Blacklisted"], reqd=1, default="Active"),
    F("dsa_branch", "Link", "DSA Branch", lbl="DSA Branch",
      description="Branch that sourced this customer; limits who can see the record"),
    S("Consent"),
    F("kyc_consent", "Check", lbl="KYC & Credit Check Consent",
      description="Customer agreed to KYC verification, a credit bureau check and sharing data with lenders"),
    F("consent_mode", "Select", ["", "Signed Form", "OTP", "Email", "Recorded Call"],
      depends="eval:doc.kyc_consent", mand="eval:doc.kyc_consent"),
    C(),
    F("consent_date", "Datetime", ro=1, depends="eval:doc.kyc_consent"),
    F("consent_proof", "Attach", depends="eval:doc.kyc_consent"),
    S("Identity (restricted)"),
    F("pan", "Data", unique=1, permlevel=1),
    C(),
    F("aadhaar_number", "Data", permlevel=1, lbl="Aadhaar Number (masked)",
      description="Type the 12 digits; only the last 4 are kept (XXXX-XXXX-1234)"),
    S("Credit Bureau (restricted)"),
    F("cibil_score", "Int", permlevel=1, lbl="CIBIL Score",
      description="300 to 900, or -1 for no credit history"),
    F("cibil_report_date", "Date", permlevel=1, lbl="CIBIL Report Date"),
    C(),
    F("cibil_report", "Attach", permlevel=1, lbl="CIBIL Report"),
    S("Employment & Income"),
    F("employment_type", "Select", EMPLOYMENT),
    F("employer_business_name", "Data", lbl="Employer / Business Name"),
    F("designation", "Data"),
    C(),
    F("monthly_income", "Currency", permlevel=1),
    F("other_monthly_income", "Currency", permlevel=1),
    F("existing_emi", "Currency", permlevel=1, lbl="Existing EMI"),
    S("Address"),
    F("residential_address", "Link", "Address"),
    C(),
    F("permanent_address", "Link", "Address"),
    S(),
    F("remarks", "Small Text"),
])

D["Co-Applicant"] = dict(istable=1, fields=[
    F("applicant", "Link", "Loan Customer", reqd=1, lst=1),
    F("applicant_type", "Select", ["Co-Applicant", "Guarantor"], reqd=1, default="Co-Applicant", lst=1),
    F("relationship_with_primary", "Select", ["Spouse", "Parent", "Son", "Daughter", "Sibling", "Other"], reqd=1, lst=1),
    F("is_income_considered", "Check", lst=1),
    F("monthly_income", "Currency"),
    F("existing_emi", "Currency", lbl="Existing EMI"),
    F("ownership_percentage", "Percent"),
    F("kyc_status", "Select", KYC, reqd=1, default="Pending", lst=1),
    F("remarks", "Small Text"),
])

FINAL_STATUS = ["Draft", "Documents Pending", "Ready for Submission", "Submitted", "Under Review", "Query Raised",
                "Sanctioned", "Rejected", "On Hold", "Partially Disbursed", "Disbursed", "Withdrawn", "Closed"]

D["Loan Application"] = dict(autoname="format:LAPP-{YYYY}-{#####}", title="primary_customer", search="primary_customer,lender", track=1, fields=[
    F("application_date", "Date", reqd=1, default="Today"),
    F("loan_lead", "Link", "Loan Lead", reqd=1),
    F("primary_customer", "Link", "Loan Customer", reqd=1, lst=1),
    F("lender", "Link", "Lender", reqd=1, lst=1),
    F("lender_branch", "Link", "Lender Branch"),
    C(),
    F("loan_product", "Link", "Loan Product", reqd=1),
    F("loan_scheme", "Link", "Loan Scheme"),
    F("loan_type", "Select", LOAN_CATEGORY, reqd=1),
    F("application_status", "Select", ["Open", "In Progress", "On Hold", "Completed", "Cancelled"], reqd=1, default="Open"),
    S("DSA Assignment"),
    F("company", "Link", "Company", reqd=1),
    F("franchise", "Link", "Franchise"),
    F("dsa_branch", "Link", "DSA Branch", reqd=1),
    C(),
    F("branch_manager", "Link", "Employee"),
    F("assigned_agent", "Link", "Employee", reqd=1),
    S("Loan Requirements"),
    F("requested_loan_amount", "Currency", reqd=1, lst=1),
    F("requested_tenure_months", "Int", reqd=1),
    F("expected_interest_rate", "Percent"),
    F("estimated_emi", "Currency", ro=1, lbl="Estimated EMI"),
    F("loan_purpose", "Select", ["Purchase", "Construction", "Plot + Construction", "Renovation", "Balance Transfer", "Top-up", "Other"], reqd=1),
    C(),
    F("property_type", "Select", PROPERTY),
    F("property_value", "Currency"),
    F("property_address", "Small Text"),
    F("property_city", "Data"), F("property_state", "Data"), F("property_pincode", "Data"),
    S("Applicant Details"),
    F("co_applicants", "Table", "Co-Applicant"),
    S("Lender Processing", collapsible=1),
    F("lender_application_number", "Data"),
    F("lender_submission_date", "Date"),
    F("sanction_date", "Date", mand="eval:doc.final_status=='Sanctioned'"),
    F("sanctioned_amount", "Currency", mand="eval:doc.final_status=='Sanctioned'"),
    C(),
    F("sanctioned_interest_rate", "Percent"),
    F("sanctioned_tenure_months", "Int"),
    F("sanction_valid_until", "Date"),
    F("rejection_reason", "Small Text", mand="eval:doc.final_status=='Rejected'"),
    F("application_remarks", "Small Text"),
    S("Workflow"),
    F("workflow_state", "Link", "Workflow State", ro=1),
    F("manager_approval", "Select", ["", "Pending", "Approved", "Rejected"]),
    C(),
    F("manager_approval_date", "Datetime", ro=1),
    F("final_status", "Select", FINAL_STATUS, reqd=1, default="Draft", lst=1),
    S("Lender Invoice", collapsible=1, description="Filled automatically once the loan is Disbursed"),
    F("sales_invoice", "Link", "Sales Invoice", ro=1),
    F("invoice_status", "Select", ["", "Awaiting Commission", "Invoice Created", "Emailed", "Email Pending", "Failed"], ro=1),
    F("invoice_amount", "Currency", ro=1),
    C(),
    F("invoice_emailed_on", "Datetime", ro=1),
    F("invoice_email_recipients", "Small Text", ro=1),
    F("invoice_communication", "Link", "Communication", ro=1, lbl="Invoice Email"),
    F("invoice_error", "Small Text", ro=1, depends="eval:doc.invoice_error"),
])

D["Document Checklist"] = dict(autoname="format:DOC-{YYYY}-{#####}", title="applicant", search="loan_application,applicant", track=1, fields=[
    F("loan_application", "Link", "Loan Application", reqd=1, lst=1),
    F("applicant", "Link", "Loan Customer", reqd=1, lst=1),
    F("lender_document_rule", "Link", "Lender Document Rule"),
    F("dsa_branch", "Link", "DSA Branch", ro=1, fetch="loan_application.dsa_branch", lbl="DSA Branch"),
    S("Documents"),
    F("documents", "Table", "Document Checklist Item"),
])

DOC_STATUS = ["Pending", "Received", "Under Verification", "Verified", "Rejected", "Resubmission Required", "Not Applicable"]
D["Document Checklist Item"] = dict(istable=1, fields=[
    F("document_name", "Data", reqd=1, lst=1),
    F("document_status", "Select", DOC_STATUS, reqd=1, default="Pending", lst=1),
    F("document_file", "Attach", lst=1),
    F("extracted_data_type", "Link", "DocType"),
    F("extracted_data", "Dynamic Link", "extracted_data_type", lst=1),
    F("remarks", "Small Text"),
])


# ---------------- PART D: EXTRACTED DOCUMENT DATA ----------------
def extracted_common():
    return [
        F("document_checklist", "Link", "Document Checklist", reqd=1, lst=1),
        F("loan_application", "Link", "Loan Application", ro=1, fetch="document_checklist.loan_application"),
        F("applicant", "Link", "Loan Customer", ro=1, fetch="document_checklist.applicant", lst=1),
        F("dsa_branch", "Link", "DSA Branch", ro=1, fetch="document_checklist.dsa_branch", lbl="DSA Branch"),
        F("source_file", "Attach"),
        C(),
        F("extraction_status", "Select", ["Pending", "Extracted", "Verified", "Failed"], reqd=1, default="Pending", lst=1),
        F("extracted_on", "Datetime"),
        S("Extracted Data"),
    ]


AY = ["2024-25", "2025-26", "2026-27"]

D["Aadhaar Card Data"] = dict(autoname="format:AADH-{#####}", search="applicant", fields=extracted_common() + [
    F("aadhaar_last_4", "Data", permlevel=1, length=4, lbl="Aadhaar Last 4",
      description="Last 4 digits only. Never store the full Aadhaar number here."),
    F("name_on_card", "Data"),
    F("date_of_birth", "Date"),
    F("gender", "Select", ["", "Male", "Female", "Other"]),
    F("address", "Small Text"),
])

D["PAN Card Data"] = dict(autoname="format:PAN-{#####}", search="applicant", fields=extracted_common() + [
    F("pan_number", "Data", permlevel=1, lbl="PAN Number"),
    F("name_on_card", "Data"),
    F("father_name", "Data"),
    F("date_of_birth", "Date"),
])

D["Address Proof Data"] = dict(autoname="format:ADDR-{#####}", search="applicant", fields=extracted_common() + [
    F("proof_type", "Select", ["Passport", "Voter ID", "Driving Licence", "Utility Bill", "Rent Agreement", "Other"]),
    F("name_on_document", "Data"),
    F("address", "Small Text"),
    F("document_date", "Date"),
    F("valid_till", "Date"),
])

D["Bank Statement Data"] = dict(autoname="format:BANK-{#####}", search="applicant", fields=extracted_common() + [
    F("bank_name", "Data"),
    F("account_last_4", "Data", permlevel=1, length=4, lbl="Account Last 4"),
    F("period_from", "Date"),
    F("period_to", "Date"),
    F("months_covered", "Int", ro=1, description="Calculated from the period; lenders need at least 6"),
    C(),
    F("average_balance", "Currency"),
    F("total_credits", "Currency"),
    F("total_debits", "Currency"),
    F("salary_credits", "Currency"),
    F("bounced_cheques", "Int"),
])

D["Salary Slip Data"] = dict(autoname="format:SAL-{#####}", search="applicant", fields=extracted_common() + [
    F("employer_name", "Data"),
    F("salary_month", "Date", description="Any date in the salary month"),
    F("gross_salary", "Currency"),
    F("deductions", "Currency"),
    F("net_salary", "Currency"),
])

D["ITR Data"] = dict(autoname="format:ITR-{#####}", search="applicant", fields=extracted_common() + [
    F("assessment_year", "Select", AY, lbl="Assessment Year"),
    F("total_income", "Currency"),
    F("tax_paid", "Currency"),
    F("filing_date", "Date"),
    F("acknowledgement_number", "Data"),
])

D["Form 16 Data"] = dict(autoname="format:F16-{#####}", search="applicant", fields=extracted_common() + [
    F("assessment_year", "Select", AY, lbl="Assessment Year"),
    F("employer_name", "Data"),
    F("employer_tan", "Data", lbl="Employer TAN"),
    F("employee_pan", "Data", permlevel=1, lbl="Employee PAN"),
    C(),
    F("gross_salary", "Currency"),
    F("total_deductions", "Currency"),
    F("taxable_income", "Currency"),
    F("tds_deducted", "Currency", lbl="TDS Deducted"),
    F("certificate_number", "Data"),
    F("issue_date", "Date"),
])

D["Lender Login"] = dict(autoname="format:LLOG-{#####}", title="login_title", search="login_title,lender", track=1, fields=[
    F("login_title", "Data", reqd=1, lst=1),
    F("lender", "Link", "Lender", reqd=1, lst=1),
    F("lender_branch", "Link", "Lender Branch"),
    F("portal_name", "Data", reqd=1),
    F("portal_url", "Data"),
    F("login_username", "Data", description="Username only. Never store passwords here."),
    C(),
    F("assigned_employee", "Link", "Employee", reqd=1),
    F("access_type", "Select", ["Individual", "Shared", "API Integration"], reqd=1, default="Individual"),
    F("access_status", "Select", ["Active", "Inactive", "Locked", "Expired"], reqd=1, default="Active", lst=1),
    F("access_start_date", "Date"), F("access_end_date", "Date"),
    F("last_access_date", "Datetime"),
    S(),
    F("remarks", "Small Text"),
])

D["Loan Disbursement"] = dict(autoname="format:DISB-{YYYY}-{#####}", search="loan_application,lender", track=1, fields=[
    F("loan_application", "Link", "Loan Application", reqd=1, lst=1),
    F("disbursement_number", "Data", reqd=1, lst=1),
    F("lender", "Link", "Lender", reqd=1, ro=1, fetch="loan_application.lender"),
    F("dsa_branch", "Link", "DSA Branch", ro=1, fetch="loan_application.dsa_branch", lbl="DSA Branch"),
    F("lender_reference_number", "Data"),
    C(),
    F("disbursement_date", "Date", reqd=1),
    F("disbursement_type", "Select", ["Full", "Part", "Final"], reqd=1),
    F("disbursement_status", "Select", ["Draft", "Pending", "Confirmed", "Failed", "Reversed"], reqd=1, default="Confirmed", lst=1,
      description="Confirmed = the bank has released the money; only Confirmed tranches move the loan forward and earn commission"),
    S("Amounts"),
    F("sanctioned_amount", "Currency", ro=1, fetch="loan_application.sanctioned_amount"),
    F("previous_disbursed_amount", "Currency", ro=1),
    F("current_disbursement_amount", "Currency", reqd=1, lst=1),
    C(),
    F("total_disbursed_amount", "Currency", ro=1),
    F("balance_amount", "Currency", ro=1),
    S("Payment"),
    F("beneficiary_name", "Data"),
    F("beneficiary_account_reference", "Data", permlevel=1),
    F("payment_reference", "Data"),
    C(),
    F("payment_mode", "Select", [""] + PAY_MODE),
    F("proof_document", "Attach"),
    S(),
    F("remarks", "Small Text"),
])

# ---------------- PART C: COMMISSION & SETTLEMENT ----------------
D["Commission Calculation"] = dict(autoname="format:COMM-{YYYY}-{#####}", search="loan_disbursement,lender", track=1, fields=[
    F("loan_application", "Link", "Loan Application", reqd=1, lst=1),
    F("loan_disbursement", "Link", "Loan Disbursement", reqd=1, lst=1),
    F("lender", "Link", "Lender", reqd=1, ro=1, fetch="loan_application.lender"),
    F("commission_slab", "Link", "Commission Slab Structure", reqd=1),
    F("company", "Link", "Company", reqd=1, ro=1, fetch="loan_application.company"),
    C(),
    F("franchise", "Link", "Franchise", ro=1, fetch="loan_application.franchise"),
    F("dsa_branch", "Link", "DSA Branch", reqd=1, ro=1, fetch="loan_application.dsa_branch"),
    F("assigned_agent", "Link", "Employee", ro=1, fetch="loan_application.assigned_agent"),
    F("calculation_date", "Date", reqd=1, default="Today"),
    F("calculation_status", "Select", ["Draft", "Calculated", "Approved", "Invoiced", "Partially Paid", "Paid", "Reversed"],
      reqd=1, default="Draft", lst=1),
    S("Commission"),
    F("commission_basis_amount", "Currency", reqd=1, ro=1),
    F("commission_percentage", "Percent"),
    F("fixed_commission", "Currency"),
    F("gross_commission", "Currency", reqd=1, ro=1, lst=1),
    C(),
    F("gst_rate", "Percent", lbl="GST Rate"), F("gst_amount", "Currency", ro=1, lbl="GST Amount"),
    F("tds_rate", "Percent", lbl="TDS Rate"), F("tds_amount", "Currency", ro=1, lbl="TDS Amount"),
    F("other_deductions", "Currency"),
    F("net_commission", "Currency", reqd=1, ro=1),
    F("payout_statement", "Link", "Lender Payout Statement", ro=1,
      description="The lender payout statement that covers this commission"),
    S(),
    F("remarks", "Small Text"),
])

D["Commission Invoice"] = dict(autoname="format:CIN-{YYYY}-{#####}", search="lender,invoice_number", track=1, fields=[
    F("invoice_date", "Date", reqd=1, default="Today"),
    F("company", "Link", "Company", reqd=1),
    F("lender", "Link", "Lender", reqd=1, lst=1),
    F("invoice_type", "Select", ["Commission", "Adjustment", "Debit Note", "Credit Note"], reqd=1, default="Commission"),
    C(),
    F("invoice_number", "Data"),
    F("due_date", "Date"),
    F("invoice_status", "Select", ["Draft", "Pending Approval", "Submitted", "Partially Paid", "Paid", "Cancelled"],
      reqd=1, default="Draft", lst=1),
    F("erpnext_sales_invoice", "Link", "Sales Invoice", lbl="ERPNext Sales Invoice"),
    S("Amounts"),
    F("taxable_amount", "Currency", reqd=1),
    F("cgst_amount", "Currency", lbl="CGST Amount"),
    F("sgst_amount", "Currency", lbl="SGST Amount"),
    F("igst_amount", "Currency", lbl="IGST Amount"),
    C(),
    F("total_gst_amount", "Currency", ro=1, lbl="Total GST Amount"),
    F("tds_expected", "Currency", lbl="TDS Expected"),
    F("invoice_total", "Currency", reqd=1, ro=1, lst=1),
    S(),
    F("remarks", "Small Text"),
])

D["Commission Clawback"] = dict(autoname="format:CLB-{YYYY}-{#####}", search="commission_calculation,lender", track=1, fields=[
    F("clawback_date", "Date", reqd=1, default="Today"),
    F("commission_calculation", "Link", "Commission Calculation", reqd=1, lst=1),
    F("commission_invoice", "Link", "Commission Invoice"),
    F("loan_application", "Link", "Loan Application", reqd=1, ro=1, fetch="commission_calculation.loan_application"),
    F("lender", "Link", "Lender", reqd=1, ro=1, fetch="commission_calculation.lender", lst=1),
    C(),
    F("clawback_reason", "Select", ["Loan Cancellation", "Loan Closure", "Early Default", "Duplicate Payment",
                                    "Lender Reversal", "Other"], reqd=1),
    F("recovery_status", "Select", ["Pending", "Partially Recovered", "Recovered", "Waived", "Disputed"],
      reqd=1, default="Pending", lst=1),
    F("erpnext_purchase_invoice", "Link", "Purchase Invoice", lbl="ERPNext Purchase Invoice"),
    S("Amounts"),
    F("original_commission", "Currency", reqd=1, ro=1, fetch="commission_calculation.gross_commission"),
    F("clawback_percentage", "Percent"),
    F("clawback_amount", "Currency", reqd=1, lst=1),
    C(),
    F("gst_adjustment_amount", "Currency", lbl="GST Adjustment Amount"),
    F("recovery_amount", "Currency"),
    F("recovery_date", "Date"),
    S(),
    F("remarks", "Small Text"),
])

D["Lender Payout Statement"] = dict(autoname="format:LPS-{YYYY}-{#####}", title="statement_number", search="statement_number,lender", track=1, fields=[
    F("statement_number", "Data", reqd=1, lst=1),
    F("lender", "Link", "Lender", reqd=1, lst=1),
    F("statement_date", "Date", reqd=1),
    C(),
    F("period_from", "Date", reqd=1), F("period_to", "Date", reqd=1),
    F("reconciliation_status", "Select", ["Draft", "Pending Reconciliation", "Matched", "Partially Matched", "Disputed", "Closed"],
      reqd=1, default="Draft", lst=1),
    S("Amounts"),
    F("total_expected_commission", "Currency", ro=1,
      description="Gross commission of this lender's calculations dated in the period"),
    F("total_lender_commission", "Currency", reqd=1),
    F("total_tds", "Currency", lbl="Total TDS"),
    F("total_gst_adjustment", "Currency", lbl="Total GST Adjustment"),
    C(),
    F("total_deductions", "Currency"),
    F("net_payable", "Currency", reqd=1, ro=1, lst=1),
    F("actual_received_amount", "Currency"),
    S("Payment"),
    F("payment_date", "Date"),
    F("bank_reference", "Data"),
    C(),
    F("statement_attachment", "Attach"),
    S(),
    F("remarks", "Small Text"),
])

D["Franchise Settlement"] = dict(autoname="format:FST-{YYYY}-{#####}", title="settlement_number", search="settlement_number,franchise", track=1, fields=[
    F("settlement_number", "Data", reqd=1, lst=1),
    F("franchise", "Link", "Franchise", reqd=1, lst=1),
    F("company", "Link", "Company", reqd=1, fetch="franchise.company", fetch_if_empty=1),
    C(),
    F("settlement_period_from", "Date", reqd=1), F("settlement_period_to", "Date", reqd=1),
    F("settlement_status", "Select", ["Draft", "Pending Approval", "Approved", "Partially Paid", "Paid", "Cancelled"],
      reqd=1, default="Draft", lst=1),
    S("Amounts"),
    F("total_gross_commission", "Currency", ro=1,
      description="Gross commission received (Paid / Partially Paid) on this franchise's calculations in the period"),
    F("franchise_share_percentage", "Percent", reqd=1, fetch="franchise.settlement_percentage", fetch_if_empty=1),
    F("franchise_share_amount", "Currency", reqd=1, ro=1),
    C(),
    F("deductions", "Currency"),
    F("gst_amount", "Currency", lbl="GST Amount"),
    F("tds_amount", "Currency", lbl="TDS Amount"),
    F("net_payable", "Currency", reqd=1, ro=1, lst=1),
    S("Payment"),
    F("settlement_date", "Date"),
    F("payment_reference", "Data"),
    C(),
    F("erpnext_purchase_invoice", "Link", "Purchase Invoice", lbl="ERPNext Purchase Invoice"),
    S(),
    F("remarks", "Small Text"),
])


# ---------------- writer ----------------
def scrub(name):
    return name.replace(" ", "_").replace("-", "_").lower()


def classname(name):
    return name.replace(" ", "").replace("-", "")


# ---------------- ROLES & PERMISSIONS ----------------
# Roles are created by dsa_loan.dsa_loan_portal.access.create_roles (before_migrate / after_install).
ADMIN, BM, AGENT, VER, ACC, FP = ("DSA Admin", "Branch Manager", "DSA Agent", "Document Verifier",
                                  "DSA Accounts", "Franchise Partner")
FULL = "rwcd"
MASTERS = ["Lender Type", "Lender", "Lender Branch", "Loan Product", "Loan Scheme", "Lender Document Rule"]
EXTRACTED = ["Aadhaar Card Data", "PAN Card Data", "Address Proof Data", "Bank Statement Data",
             "Salary Slip Data", "ITR Data", "Form 16 Data"]
COMMISSION = ["Commission Calculation", "Commission Invoice", "Commission Clawback", "Lender Payout Statement"]
CUSTOMER_PL1 = {ADMIN: "rw", BM: "rw", AGENT: "rw", FP: "rw", VER: "rw"}

# doctype -> (level-0 rights per role, permlevel-1 rights per role).  r=read w=write c=create d=delete
ACCESS = {}
for _dt in MASTERS:
    ACCESS[_dt] = ({ADMIN: FULL, BM: "r", AGENT: "r", VER: "r", ACC: "r", FP: "r"}, {ADMIN: "rw", ACC: "r"})
ACCESS["Commission Slab Structure"] = ({ADMIN: FULL, ACC: FULL, BM: "r"}, {})
for _dt in ["DSA Branch", "Franchise"]:
    ACCESS[_dt] = ({ADMIN: FULL, BM: "r", AGENT: "r", VER: "r", ACC: "r", FP: "r"}, {ADMIN: "rw", ACC: "r", FP: "r"})
ACCESS["Loan Lead"] = ({ADMIN: FULL, BM: FULL, AGENT: "rwc", FP: "rwc"}, {})
ACCESS["Loan Customer"] = ({ADMIN: FULL, BM: FULL, AGENT: "rwc", FP: "rwc", VER: "r", ACC: "r"}, CUSTOMER_PL1)
ACCESS["Loan Application"] = ({ADMIN: FULL, BM: FULL, AGENT: "rwc", FP: "rwc", VER: "r", ACC: "r"}, {})
ACCESS["Document Checklist"] = ({ADMIN: FULL, BM: FULL, AGENT: "rwc", FP: "rwc", VER: "rw"}, {})
for _dt in EXTRACTED:
    ACCESS[_dt] = ({ADMIN: FULL, BM: FULL, AGENT: "rwc", FP: "rwc", VER: "rwc"}, CUSTOMER_PL1)
ACCESS["Lender Login"] = ({ADMIN: FULL, BM: FULL, AGENT: "r", ACC: "r"}, {})
ACCESS["Loan Disbursement"] = ({ADMIN: FULL, BM: "rwc", ACC: FULL, AGENT: "r", FP: "r"}, {ADMIN: "rw", ACC: "rw", BM: "r"})
for _dt in COMMISSION:
    ACCESS[_dt] = ({ADMIN: "r", ACC: FULL, BM: "r"}, {ADMIN: "r", ACC: "rw"})
ACCESS["Franchise Settlement"] = ({ADMIN: "r", ACC: FULL, BM: "r", FP: "r"}, {ADMIN: "r", ACC: "rw", FP: "r"})


def perm_row(role, rights, submittable, level=0):
    p = {"role": role}
    if level:
        p["permlevel"] = level
    if "r" in rights:
        p.update(read=1)
        if not level:
            p.update(report=1, print=1, email=1, share=1)
            if role in ("System Manager", ADMIN, BM, ACC):
                p["export"] = 1
    if "w" in rights: p["write"] = 1
    if "c" in rights: p["create"] = 1
    if "d" in rights: p["delete"] = 1
    if submittable and "w" in rights and not level:
        p.update(submit=1, cancel=1, amend=1)
    return p


def perms(name, submittable, has_pl1):
    level0, level1 = ACCESS.get(name, ({}, {}))
    p = [perm_row("System Manager", FULL, submittable)]
    p += [perm_row(role, rights, submittable) for role, rights in level0.items()]
    if has_pl1:
        # permlevel 1 = sensitive fields (PAN, masked Aadhaar, income, credit score, bank details)
        p.append(perm_row("System Manager", "rw", submittable, 1))
        p += [perm_row(role, rights, submittable, 1) for role, rights in level1.items()]
    return p


# Areas used to group the Connections panel on each form
AREA = {**{d: "Lender" for d in ["Lender Type", "Lender", "Lender Branch", "Loan Product", "Loan Scheme",
                                 "Commission Slab Structure", "Lender Document Rule", "Lender Login"]},
        **{d: "DSA" for d in ["Franchise", "DSA Branch"]},
        **{d: "Loan" for d in ["Loan Lead", "Loan Customer", "Loan Application", "Document Checklist"]},
        **{d: "Documents" for d in EXTRACTED},
        **{d: "Money" for d in ["Loan Disbursement", "Commission Calculation", "Commission Invoice", "Commission Clawback",
                                "Lender Payout Statement", "Franchise Settlement"]}}


def connections(target):
    """DocType Links for the form's Connections panel: every module DocType that links to `target`
    (first link field per DocType)."""
    out = []
    for src, spec in D.items():
        if spec.get("istable") or src == target:
            continue
        field = next((f["fieldname"] for f in spec["fields"] if f["fieldtype"] == "Link" and f.get("options") == target), None)
        if field:
            out.append({"link_doctype": src, "link_fieldname": field, "group": AREA.get(src, "Other")})
    order = ["Loan", "Documents", "Money", "DSA", "Lender", "Other"]
    out.sort(key=lambda l: (order.index(l["group"]), l["link_doctype"]))
    return out


def build(name, spec):
    fields, sb, cb = [], 0, 0
    for f in spec["fields"]:
        f = dict(f)
        if f["fieldtype"] == "Section Break":
            sb += 1; f["fieldname"] = f"section_break_{sb}"
            if not f.get("label"): f.pop("label", None)
            if not f.get("collapsible"): f.pop("collapsible", None)
        elif f["fieldtype"] == "Column Break":
            cb += 1; f["fieldname"] = f"column_break_{cb}"
        fields.append(f)
    names = [f["fieldname"] for f in fields]
    assert len(names) == len(set(names)), f"duplicate fieldname in {name}"

    doc = {
        "actions": [], "allow_rename": 0, "creation": TS, "doctype": "DocType",
        "engine": "InnoDB", "field_order": names, "fields": fields, "index_web_pages_for_search": 0,
        "links": connections(name), "modified": TS, "modified_by": "Administrator", "module": MODULE,
        "name": name, "owner": "Administrator", "sort_field": "modified", "sort_order": "DESC",
        "states": [],
    }
    if spec.get("istable"):
        doc.update(istable=1, editable_grid=1, permissions=[])
    else:
        an = spec["autoname"]
        if an.startswith("format:") and "{#####}" in an:
            # "format:X-{#####}" draws from ONE counter shared by every DocType; the old-style series
            # "X-.#####" keeps a counter per prefix (LEAD-2026-, LDR-, ...), so each DocType counts on its own.
            an = an[len("format:"):].replace("{YYYY}", ".YYYY.").replace("{#####}", ".#####")
        doc["autoname"] = an
        doc["naming_rule"] = ('By "Naming Series" field' if an.startswith("naming_series")
                              else "By fieldname" if an.startswith("field:")
                              else "Expression" if an.startswith("format:") else "Expression (old style)")
        assert name in ACCESS, f"no role access defined for {name}"
        doc["permissions"] = perms(name, spec.get("submittable"), any(f.get("permlevel") for f in fields))
        if spec.get("submittable"): doc["is_submittable"] = 1
        if spec.get("track"): doc["track_changes"] = 1
        if spec.get("title"):
            doc["title_field"] = spec["title"]
            doc["show_title_field_in_link"] = 1
        if spec.get("search"): doc["search_fields"] = spec["search"]
    return doc


def main():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "__init__.py"), "a").close()
    dt_root = os.path.join(OUT, "doctype")
    os.makedirs(dt_root, exist_ok=True)
    open(os.path.join(dt_root, "__init__.py"), "a").close()
    for name, spec in D.items():
        folder = os.path.join(dt_root, scrub(name))
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, "__init__.py"), "a").close()
        with open(os.path.join(folder, scrub(name) + ".json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(build(name, spec), fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        py = os.path.join(folder, scrub(name) + ".py")
        if not os.path.exists(py):  # never overwrite hand-written controllers
            with open(py, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("# Copyright (c) 2026\n# For license information, please see license.txt\n\n"
                         "from frappe.model.document import Document\n\n\n"
                         f"class {classname(name)}(Document):\n\tpass\n")
    print(f"Wrote {len(D)} DocTypes to {os.path.abspath(dt_root)}")


if __name__ == "__main__":
    main()
