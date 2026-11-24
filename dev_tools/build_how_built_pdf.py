"""PDF 3 - how the DSA Loan Portal was built: DocTypes, controllers, permissions, automation, data, tests.

Usage: py tools/build_how_built_pdf.py <bench_dir> <output.pdf>   (PREVIEW=1|2|3 builds one third, for checking)
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.platypus import CondPageBreak, Flowable, PageBreak, Preformatted, SimpleDocTemplate, Spacer  # noqa: E402

from pdfkit_common import (AMBER, AUTO_BG, GRID, MUTED, NAVY, S, TEAL, WARN_BG, E, P, box, bullets, cover, data_fields,  # noqa: E402
                           footer, load_doctypes, table)

BENCH, OUT = sys.argv[1], sys.argv[2]
APP = os.path.join(BENCH, "apps", "dsa_loan")
MOD = os.path.join(APP, "dsa_loan", "dsa_loan_portal")
DOCS = load_doctypes(MOD)
W = A4[0] - 28 * mm
ROLES = ["DSA Admin", "Branch Manager", "DSA Agent", "Document Verifier", "DSA Accounts", "Franchise Partner"]

COMMITS = [
	("52c9765", "20-11", "Rebuild DocTypes to the consolidated field specification (from the analysis of 7 spec PDFs)"),
	("91d8551", "20-11", "Remove leftovers not in the final DocType spec"),
	("24724fe", "20-11", "Keep Co-Applicant as the only child table"),
	("603ca24", "22-11", "Align every DocType field with the DSA Home Loan Blueprint"),
	("249aa89", "23-11", "Document Checklist table and the 7 extracted-data DocTypes"),
	("3e229d2", "23-11", "Roles, branch data separation, Aadhaar masking, consent and CIBIL"),
	("ebbb605", "23-11", "Raise and email the lender's Sales Invoice when a loan is disbursed"),
	("5d1c20a", "23-11", "Loan Disbursed status in the lender invoice email"),
	("ecf098b", "24-11", "Per-DocType numbering, RBI LTV and limit checks, PIN code validation"),
	("e5f8764", "24-11", "Commission % on slabs; fee range, rate date and source on products"),
	("41b245d", "24-11", "Invoice email never falls back to the bank's public address"),
	("eff8958", "24-11", "Invoice closed loans too; field text for the email group"),
	("78a7b6e", "24-11", "Data and test scripts with run order (scripts/)"),
	("2ae53a2", "24-11", "Automate commission, invoices, payouts, settlements and clawbacks"),
	("af88f92", "24-11", "Payout statements: top-up for commissions arriving after reconciliation"),
]


# ------------------------------------------------------------------ helpers reading the code
def rights(dt):
	"""role -> (level-0 rights, level-1 rights) from the DocType JSON permissions."""
	out = {}
	for p in DOCS[dt].get("permissions", []):
		letters = "".join(k[0].upper() for k in ("read", "write", "create", "delete", "submit") if p.get(k))
		lvl = p.get("permlevel", 0)
		r0, r1 = out.get(p["role"], ("", ""))
		out[p["role"]] = (letters, r1) if not lvl else (r0, letters)
	return out


def throws():
	"""DocType -> list of error messages, read from frappe.throw(_("...")) in the controllers."""
	found = {}
	files = glob.glob(os.path.join(MOD, "doctype", "*", "*.py")) + glob.glob(os.path.join(MOD, "*.py"))
	for path in sorted(files):
		src = open(path, encoding="utf-8").read()
		msgs = re.findall(r'frappe\.throw\(\s*_\(\s*\(?\s*"((?:[^"\\]|\\.)+)"', src)
		if not msgs:
			continue
		stem = os.path.splitext(os.path.basename(path))[0]
		name = next((d for d in DOCS if d.lower().replace(" ", "_").replace("-", "_") == stem), None) or f"{stem}.py (shared)"
		found.setdefault(name, []).extend(m.replace("{0}", "X").replace("{1}", "Y").replace("{2}", "Z").replace("{3}", "")
		                                  for m in msgs)
	return found


def hooks():
	"""The app's hook block, read from hooks.py (from before_install to the end of doc_events)."""
	src = open(os.path.join(APP, "dsa_loan", "hooks.py"), encoding="utf-8").read().expandtabs(4)
	start = src.index("before_install")
	end = src.index("}", src.index("}", src.index("doc_events")) + 1) + 1
	return [l for l in src[start:end].splitlines() if l.strip() and not l.lstrip().startswith("#")]


# ------------------------------------------------------------------ architecture drawing
class Architecture(Flowable):
	def __init__(self, width, height=250):
		super().__init__()
		self.width, self.height = width, height

	def node(self, x, y, w, h, title, lines, fill, stroke):
		c = self.canv
		c.setFillColor(fill)
		c.setStrokeColor(stroke)
		c.setLineWidth(0.9)
		c.roundRect(x, y, w, h, 4, stroke=1, fill=1)
		c.setFillColor(NAVY)
		c.setFont("UI-B", 8.2)
		c.drawString(x + 6, y + h - 12, title)
		c.setFont("UI", 7.2)
		c.setFillColor(colors.black)
		for i, l in enumerate(lines):
			c.drawString(x + 6, y + h - 24 - i * 9.5, l)

	def arrow(self, x1, y1, x2, y2, label=""):
		c = self.canv
		c.setStrokeColor(MUTED)
		c.setFillColor(MUTED)
		c.setLineWidth(0.8)
		c.line(x1, y1, x2, y2)
		import math
		a = math.atan2(y2 - y1, x2 - x1)
		p = c.beginPath()
		p.moveTo(x2, y2)
		p.lineTo(x2 - 5 * math.cos(a) + 2.5 * math.sin(a), y2 - 5 * math.sin(a) - 2.5 * math.cos(a))
		p.lineTo(x2 - 5 * math.cos(a) - 2.5 * math.sin(a), y2 - 5 * math.sin(a) + 2.5 * math.cos(a))
		p.close()
		c.drawPath(p, stroke=0, fill=1)
		if label:
			c.setFont("UI", 6.8)
			c.drawCentredString((x1 + x2) / 2, (y1 + y2) / 2 + 3, label)

	def draw(self):
		w = self.width
		light = colors.HexColor("#eef2f7")
		self.node(0, 200, 120, 46, "Users (browser)", ["Agents, managers, verifiers,", "accounts, franchise partners"], light, NAVY)
		self.node(160, 112, 200, 134, "dsa_loan app (Frappe v16)", [
			"29 DocTypes (JSON) in module DSA Loan Portal",
			"Controllers: one .py per DocType (rules)",
			"utils.py: PAN, GSTIN, PIN, mobile, ranges",
			"document_data.py: checklists, documents",
			"access.py: roles, branch access",
			"invoicing.py: Sales Invoice + email",
			"automation.py: commission ... clawback",
			"patches/: data fixes run on migrate",
			"scripts/: data loading and the e2e test",
		], AUTO_BG, TEAL)
		self.node(400, 168, w - 400, 78, "ERPNext v16", ["Company, Employee, Customer", "Sales Invoice, GST tax templates",
		                                                 "General Ledger entries"], light, NAVY)
		self.node(400, 72, w - 400, 78, "Background (bench start)", ["Scheduler: monthly payout job", "Worker: email queue",
		                                                              "Chromium: invoice PDFs"], WARN_BG, AMBER)
		self.node(160, 8, 200, 70, "MariaDB database", ["One table per DocType (tabLoan Application ...)",
		                                                "User Permissions, Email Queue, Series"], light, NAVY)
		self.node(0, 72, 120, 64, "Gmail SMTP", ["dsaloanservices918@gmail.com", "-> lender email groups"], light, NAVY)
		self.arrow(120, 222, 160, 222, "forms")
		self.arrow(360, 210, 400, 210, "invoices")
		self.arrow(360, 125, 400, 110, "jobs")
		self.arrow(260, 112, 260, 78, "")
		self.arrow(400, 100, 120, 100, "")
		self.canv.setFont("UI", 6.8)
		self.canv.setFillColor(MUTED)
		self.canv.drawString(150, 102, "emails with invoice PDF")


def code(text):
	return box([Preformatted(text, S["code"])], bg=colors.HexColor("#f6f8fa"), border=GRID, width=W)


# ------------------------------------------------------------------ sections
def part1():
	s = cover("DSA Loan Portal", "How it was built: design, code, automation and data",
	          ["What the system is, how it is put together, and why it was built this way.",
	           "How the 29 DocTypes were created and kept in sync, and where the business rules live.",
	           "Security: roles, branch separation, Aadhaar masking, consent.",
	           "Automation: invoices, emails, commission, payouts, settlements and clawbacks.",
	           "Master data and bank rates, the scripts, the tests, and what is still open.",
	           "Rule, permission and hook tables are read from the code itself."])
	s += [Spacer(1, 8 * mm), table([["Item", "Value"],
	                                 ["Platform", "Frappe Framework v16 + ERPNext v16, Python, MariaDB, Redis"],
	                                 ["App / module", "dsa_loan / DSA Loan Portal (29 DocTypes)"],
	                                 ["Repository", "naveedahmed918/DSA-Loan-Management-System, branch kalyani/loan-application-form"],
	                                 ["Site", "dsaloan.localhost on port 8001 (WSL Ubuntu, bench at ~/frappe/frappe-bench-v15)"],
	                                 ["State", "15 commits on the branch; the last 10 are local only (not pushed)"]],
	                                [36 * mm, W - 36 * mm]), PageBreak()]

	s += [P("1. What it is", "h1"),
	      P("A loan-management system for a Direct Selling Agent (DSA): a company that brings home-loan customers to banks and "
	        "housing finance companies and earns a commission on every disbursed loan. It tracks the customer from the first "
	        "enquiry to the bank's sanction, collects and verifies documents, records disbursements, invoices the bank for the "
	        "commission, reconciles what the bank pays, shares commission with franchise partners and handles clawbacks."),
	      Spacer(1, 6), P("2. Architecture", "h1"), Architecture(W), Spacer(1, 6)]
	s += bullets(["<b>DocType</b> = Frappe's table + form + API in one definition (a JSON file). Frappe creates the database "
	              "table, the form, list view, search, permissions and REST API from it.",
	              "<b>Controller</b> = a Python class next to each DocType; its validate / on_update methods hold the business rules "
	              "and run on every save, whoever saves (form, API, script).",
	              "<b>Hooks</b> (hooks.py) connect events to code: before/after migrate, a monthly scheduler job and a "
	              "Commission Calculation event.",
	              "<b>ERPNext</b> supplies the accounting: Customer, Sales Invoice, GST templates, General Ledger."])
	s.append(PageBreak())

	s += [P("3. How the DocTypes were created", "h1"), P("3.1 From documents to a field list", "h2")]
	s += bullets(["Seven DSA loan specification PDFs were analysed and their fields merged into one consolidated list.",
	              "The list was then aligned field by field with <b>DSA_Home_Loan_Blueprint.pdf</b>: 20 parent DocTypes, one "
	              "lender per Loan Application, Lender Login as portal-access tracking, Employment / Property Type as choice fields.",
	              "Of the Blueprint's child tables only <b>Co-Applicant</b> was kept; the Document Checklist got its own child "
	              "table and 7 document-data DocTypes were added.",
	              "Legacy DocTypes, dashboards and unused columns from the starting branch were removed (patch remove_legacy_doctypes)."])
	s += [P("3.2 Generated, not hand-clicked", "h2"),
	      P("All 29 DocTypes are produced by one Python script, <b>tools/generate_doctypes.py</b>. Each DocType is a short list of "
	        "field calls; the script writes the JSON files Frappe reads. This keeps 29 forms consistent, lets a change be "
	        "reviewed as text, and rebuilds everything in seconds."),
	      code('D["Lender"] = dict(autoname="field:lender_code", title="lender_name", fields=[\n'
	           '    F("lender_name", "Data", reqd=1, unique=1, lst=1),\n'
	           '    F("lender_code", "Data", reqd=1, unique=1),\n'
	           '    F("lender_type", "Link", "Lender Type", reqd=1, lst=1),\n'
	           '    F("pan", "Data", permlevel=1),          # sensitive: permission level 1\n'
	           '    S("Invoicing & Email"),                 # section break\n'
	           '    F("invoice_email_group", "Link", "Email Group"), ...])'),
	      Spacer(1, 4)]
	s += bullets(["<b>F(...)</b> adds a field (type, link target, required, read-only, fetch-from, depends-on, default...), "
	              "<b>S()</b> a section and <b>C()</b> a column. Labels are made from field names (pan -> PAN, emi -> EMI).",
	              "The script also writes naming rules (per-DocType series such as LAPP-.YYYY.-.#####), title and search fields, "
	              "change tracking and the role permissions (section 5).",
	              "Every run stamps a new 'modified' time so <b>bench migrate</b> re-syncs the JSON into the database.",
	              "Controllers live in <b>tools/controllers/</b> and are copied next to each DocType JSON before migrating."])
	s += [P("3.3 Applying a change", "h2"),
	      code("python3 tools/generate_doctypes.py apps/dsa_loan/dsa_loan/dsa_loan_portal \"DSA Loan Portal\"\n"
	           "for f in tools/controllers/*; do ... cp $f <doctype folder>; done\n"
	           "bench --site dsaloan.localhost migrate     # creates / alters tables, runs patches and hooks"),
	      Spacer(1, 4), P("3.4 Design decisions", "h2"),
	      table([["Decision", "Why"],
	             ["One lender per Loan Application", "Matches the Blueprint and how a file is logged with one bank; another bank = another application."],
	             ["Document Checklist per applicant", "Co-applicants and guarantors have their own KYC and income documents."],
	             ["7 document-data DocTypes + Dynamic Link", "Each document's figures are typed fields (PAN, months, income) that rules can check."],
	             ["Select fields for Employment / Property Type", "Those masters do not exist on the site; a fixed list is simpler."],
	             ["Codes as record names (lender, product, scheme, branch)", "Readable links (SBI, HDFC_HOME_LOAN) instead of numbers."],
	             ["One counter per DocType", "Frappe's 'format:' names shared one counter across DocTypes; old-style series fixed it."],
	             ["Rules in controllers, not only in the form", "They then apply to every save: form, API, scripts and automation."]],
	            [62 * mm, W - 62 * mm])]
	return s


def part2():
	s = [PageBreak(), P("4. Business rules (validations)", "h1"),
	     P("Every message below is raised by a controller and stops the save. Read automatically from the code; X / Y stand "
	       "for the values filled in at run time.", "small"), Spacer(1, 3)]
	rows = [["DocType / file", "Rule (error message)"]]
	for dt, msgs in sorted(throws().items()):
		for i, m in enumerate(dict.fromkeys(msgs)):
			rows.append([f"<b>{E(dt)}</b>" if i == 0 else "", E(m)])
	s += [table(rows, [46 * mm, W - 46 * mm]), Spacer(1, 4)]
	s += bullets(["<b>RBI loan-to-value</b> (Loan Application): requested and sanctioned amount at most 90 % of the property value "
	              "up to Rs 30 lakh, 80 % up to Rs 75 lakh, 75 % above; a scheme's Maximum LTV can lower it further.",
	              "<b>Product / scheme limits</b>: amount and tenure inside the minimum / maximum when they are set.",
	              "<b>Formats</b> (utils.py): mobile 10 digits 6-9; PAN AAAAA9999A; GSTIN 15 characters; IFSC; PIN 6 digits not "
	              "starting with 0. Values are cleaned (spaces, +91, upper case) before checking."])

	s += [PageBreak(), P("5. Security", "h1"), P("5.1 Roles and what each can do", "h2"),
	      P("R = read, W = write, C = create, D = delete, S = submit. Level 1 = the sensitive fields (PAN, Aadhaar, income, "
	        "CIBIL, bank details). System Manager has everything. Read from the DocType JSON.", "small"), Spacer(1, 3)]
	rows = [["DocType"] + [r.replace("Document ", "Doc. ").replace("Franchise ", "Fr. ") for r in ROLES] + ["Level 1 (sensitive)"]]
	for dt in sorted(d for d in DOCS if not DOCS[d].get("istable")):
		r = rights(dt)
		lvl1 = ", ".join(f"{k.replace('Branch Manager', 'BM').replace('DSA ', '').replace('Document Verifier', 'Verifier').replace('Franchise Partner', 'FP')} {v[1]}"
		                 for k, v in r.items() if v[1] and k != "System Manager") or "-"
		rows.append([E(dt)] + [r.get(role, ("-", ""))[0] or "-" for role in ROLES] + [E(lvl1)])
	s.append(table(rows, [40 * mm] + [15 * mm] * 6 + [W - 130 * mm]))
	s += [P("5.2 Branch and franchise separation", "h2")]
	s += bullets(["Every customer-facing DocType carries a <b>DSA Branch</b> link (customer, application, checklist, the 7 "
	              "document DocTypes, disbursement, commission).",
	              "A <b>User Permission</b> on DSA Branch limits a user to that branch; Frappe then filters every list, report, "
	              "link and search. Franchise partners also get one on their Franchise.",
	              "<b>access.grant_branch_access()</b> gives a user a branch or a whole franchise; a franchise's new branches are "
	              "added for its users automatically. Users without a User Permission (head office) see all branches.",
	              "Checked in the tests: the Pune agent sees only Pune applications; Accounts sees every branch but not PAN."])
	s += [P("5.3 Personal data", "h2")]
	s += bullets(["<b>Aadhaar</b>: only XXXX-XXXX-1234 is stored (the full number is never kept); document records keep the last 4 digits.",
	              "<b>Consent</b>: KYC & credit-check consent (mode, date, proof) on each Loan Customer; required before Aadhaar or "
	              "CIBIL can be saved and before an application goes to Ready for Submission / Submitted.",
	              "<b>CIBIL</b>: score 300-900 (or -1), report date, report file; warning at submission if older than 30 days.",
	              "<b>Lender Login</b> stores portal usernames only; passwords never.",
	              "Demo users have generated passwords kept in a file outside git."])
	return s


def part3():
	s = [CondPageBreak(120 * mm), P("6. Automation", "h1"),
	     P("All automatic steps are in <b>invoicing.py</b> and <b>automation.py</b>, triggered from controllers and hooks. "
	       "They never block the save that triggers them: a failure is rolled back on its own (database savepoint), "
	       "logged in the Error Log and shown as a message.")]
	s.append(table([["Event", "What is created automatically", "Code"],
	                ["Loan Application saved", "Document Checklist per applicant: 13 standard rows + matching Lender Document Rules", "document_data.make_checklists"],
	                ["Document-data record saved", "Linked to the first free matching checklist row (Received)", "document_data.ExtractedDocument"],
	                ["Disbursement Confirmed", "Commission Calculation with the slab's %, GST and TDS", "automation.create_commission"],
	                ["Loan Disbursed + all commissions present", "ERPNext Sales Invoice (submitted, GST 18 %), email with PDF to the lender's group, Communication kept", "invoicing.process"],
	                ["Sales Invoice raised", "Commission Invoice linked to it; commissions Invoiced", "automation.create_commission_invoice"],
	                ["1st of each month (scheduler)", "Lender Payout Statement per lender and month for uncovered commissions (top-up after reconciliation)", "automation.create_monthly_payout_statements"],
	                ["Payout Matched / Partially Matched", "Commissions Paid / Partially Paid; Franchise Settlement drafted; Debit Note when short", "automation.on_payout_reconciled"],
	                ["Application Closed within clawback window", "Commission Clawback per commission", "automation.clawback_on_closure"],
	                ["Clawback created", "Credit Note (Draft)", "automation.credit_note_for_clawback"]],
	               [42 * mm, 92 * mm, W - 134 * mm]))
	s += [P("6.1 The lender invoice and email", "h2")]
	s += bullets(["The lender becomes an ERPNext <b>Customer</b> (created on first use); a service Item <b>DSA Commission</b>; "
	              "one invoice line per tranche's commission; default GST template <b>Output GST In-state 18 %</b> (CGST 9 + SGST 9).",
	              "Email text comes from the Email Template <b>DSA Disbursement Invoice</b> (Jinja): subject 'Loan Disbursed: customer "
	              "(lender reference) - Invoice ...', body with the disbursement table, total and due date.",
	              "Recipients: the lender's <b>Invoice Email Group</b> members; Official Email only when no group is set (an empty "
	              "group means nobody, so a bank's public address is never emailed by accident).",
	              "Sent through Frappe's email queue with the invoice PDF (Chromium) by the Gmail account set in Email Account.",
	              "Outcome is written on the application: Invoice Status (Awaiting Commission / Invoice Created / Emailed / "
	              "Email Pending / Failed), amount, recipients, link to the email. Buttons allow Create & Email / Send again."])
	s += [P("6.2 Hooks registered", "h2"), code("\n".join(hooks()))]

	s += [CondPageBreak(70 * mm), P("7. Patches (one-time data fixes run by bench migrate)", "h1"),
	      table([["Patch", "What it does"],
	             ["remove_legacy_doctypes", "Deletes DocTypes not in the final spec (only if empty) and unused columns"],
	             ["mask_aadhaar_and_backfill_branch", "Masks Aadhaar numbers already stored; fills the new DSA Branch links"],
	             ["sync_naming_counters", "Starts each DocType's own counter after its highest existing number"],
	             ["link_commissions_to_payouts", "Links existing commissions to the payout statements that reconciled them"]],
	            [60 * mm, W - 60 * mm])]

	s += [P("8. Master data", "h1")]
	s += bullets(["<b>Imported</b> from Atharva's branch atharva/home-loan-master-data: 3 lender types, 6 lenders (SBI, HDFC, ICICI, "
	              "Axis, LIC HFL, Bank of Baroda), 5 DSA branches, 30 products, 38 schemes, 70 document rules. Data only; his "
	              "fixtures hook was not merged.",
	              "<b>Corrected</b>: 26 rules that repeated standard checklist rows turned off; 24 property/legal rules moved to "
	              "Property Owner; self-employed rules copied across Self Employed / Business Owner / Professional; SBI's published "
	              "document list added (22 rules); Plot + Construction products; valid branch PIN codes.",
	              "<b>Bank rates</b> from the banks' own pages (24-11-2026): SBI 7.50-8.80 % (card w.e.f. 15-10-2026), ICICI 8.75-10.05 %, "
	              "Axis 8.00-9.10 %, BOB 7.40-9.15 %, LIC HFL 7.15-10.25 % (Q2 FY27 range), HDFC 8.00-13.45 % (repo + 2.50 to 7.95). "
	              "Each product keeps Rates As On and Rate Source.",
	              "<b>Commission %</b> and <b>clawback rule</b> on the slabs are SAMPLES (SBI 0.40, HDFC 0.55, ICICI 0.50, Axis 0.60, "
	              "LIC HFL 0.65, BOB 0.45; 100 % within 6 months), to be replaced with the agreed terms. GST 18 %, TDS 2 % (194H)."])

	s += [CondPageBreak(60 * mm), P("9. Scripts, demo data and tests", "h1"),
	      table([["Script (apps/dsa_loan/scripts)", "Purpose"],
	             ["import_atharva_master_data.py", "Import the master data fixtures"],
	             ["fix_atharva_rules.py / fix_master_data.py", "Corrections listed in section 8"],
	             ["load_bank_rates.py", "Published rates, fees, limits; sample commission and clawback terms"],
	             ["setup_gst.py", "Output CGST / SGST / IGST accounts and GST templates"],
	             ["seed_scenarios.py", "Demo data: 5-20 records per DocType, every status covered"],
	             ["create_demo_users.py", "One user per role, limited to a branch / franchise"],
	             ["e2e_flow_test.py", "95 checks over the whole flow, rolled back afterwards"]],
	            [70 * mm, W - 70 * mm]), Spacer(1, 4)]
	s += bullets(["The end-to-end test creates a lender, branch, lead, customers, application, documents, disbursements and "
	              "commissions, checks every rule and automatic step, then rolls everything back. Latest run: 95 / 95 passed.",
	              "tools/audit_site.py compares the site with the DocType JSON (no differences apart from two dashboard pages that "
	              "belong to another branch)."])

	s += [P("10. Build history", "h1"),
	      table([["Commit", "Date", "Change"]] + [[c, d, E(t)] for c, d, t in COMMITS], [20 * mm, 16 * mm, W - 36 * mm])]

	s += [CondPageBreak(60 * mm), P("11. Commands", "h1"),
	      P("Inside Ubuntu (WSL):", "small"),
	      code("cd ~/frappe/frappe-bench-v15\n"
	           "bench start                                        # web, scheduler, worker (keep running)\n"
	           "bench --site dsaloan.localhost migrate             # after any DocType / patch change\n"
	           "cd sites && ../env/bin/python ../apps/dsa_loan/scripts/e2e_flow_test.py dsaloan.localhost\n"
	           "bench --site dsaloan.localhost execute dsa_loan.dsa_loan_portal.automation.create_monthly_payout_statements"),
	      P("From Windows PowerShell (run the payout job for November):", "small"),
	      code("wsl --% -d Ubuntu --cd ~/frappe/frappe-bench-v15 -- bash -ic \"bench --site dsaloan.localhost execute\n"
	           "  dsa_loan.dsa_loan_portal.automation.create_monthly_payout_statements\n"
	           "  --kwargs '{\\\"month_start\\\": \\\"2026-11-01\\\"}'\"          (shown on 3 lines: type it as ONE line)")]

	s += [P("12. Open items", "h1"),
	      box([P('<font color="#b45309"><b>Before production</b></font>')] + bullets([
	          "Replace the SAMPLE commission % and clawback rule with each bank's agreed terms.",
	          "Add the banks' GSTIN and PAN (only Axis has a PAN) and real branch addresses (placeholders today).",
	          "16 products and most schemes have no tenure / LTV / CIBIL limits because the banks do not publish them.",
	          "Commission DocTypes were changed (slab %, GST/TDS, clawback, payout link): review with the colleague who owns commission.",
	          "10 commits are local only; push and update the pull request when approved.",
	          "Invoice PDFs need Chromium's system libraries (libnss3, libasound2t64) on every server.",
	          "seed_scenarios.py was updated for the automation but not re-run on an empty site."]), bg=WARN_BG, border=AMBER, width=W)]
	return s


def main():
	part = os.environ.get("PREVIEW")
	story = (part1() if part in (None, "1") else []) + (part2() if part in (None, "2") else []) + \
		(part3() if part in (None, "3") else [])
	doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=16 * mm, bottomMargin=15 * mm,
	                        title="DSA Loan Portal - How It Was Built", author="DSA Loan Portal")
	doc.build(story, onFirstPage=footer("How It Was Built"), onLaterPages=footer("How It Was Built"))
	print("Wrote", OUT)


if __name__ == "__main__":
	main()
