# Copyright (c) 2026
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate

from dsa_loan.dsa_loan_portal.doctype.commission_slab_structure.commission_slab_structure import find_structure


class CommissionCalculation(Document):
	def validate(self):
		disb = frappe.db.get_value(
			"Loan Disbursement",
			self.loan_disbursement,
			["loan_application", "disbursement_status", "current_disbursement_amount", "disbursement_date"],
			as_dict=True,
		)
		if disb.loan_application != self.loan_application:
			frappe.throw(_("Disbursement {0} belongs to {1}, not {2}.").format(self.loan_disbursement, disb.loan_application, self.loan_application))
		if disb.disbursement_status != "Confirmed":
			frappe.throw(_("Commission can only be calculated on a Confirmed disbursement."))
		dup = frappe.db.get_value(
			"Commission Calculation",
			{"loan_disbursement": self.loan_disbursement, "calculation_status": ("!=", "Reversed"), "name": ("!=", self.name)},
		)
		if dup:
			frappe.throw(_("Disbursement {0} already has Commission Calculation {1}.").format(self.loan_disbursement, dup))

		app = frappe.db.get_value(
			"Loan Application",
			self.loan_application,
			["lender", "company", "franchise", "dsa_branch", "assigned_agent", "loan_product", "loan_scheme", "sanctioned_amount"],
			as_dict=True,
		)
		self.lender, self.company, self.franchise = app.lender, app.company, app.franchise
		self.dsa_branch, self.assigned_agent = app.dsa_branch, app.assigned_agent

		if not self.commission_slab:
			self.commission_slab = find_structure(app.lender, app.loan_product, app.loan_scheme, disb.disbursement_date)
		if not self.commission_slab:
			frappe.throw(_("No Active Commission Slab Structure for {0} on {1}.").format(app.lender, disb.disbursement_date))
		slab = frappe.db.get_value(
			"Commission Slab Structure", self.commission_slab, ["lender", "calculation_basis", "effective_from", "effective_to"], as_dict=True
		)
		if slab.lender != app.lender:
			frappe.throw(_("Commission Slab {0} belongs to lender {1}.").format(self.commission_slab, slab.lender))

		basis = app.sanctioned_amount if slab.calculation_basis == "Sanctioned Amount" else disb.current_disbursement_amount
		self.commission_basis_amount = flt(basis)
		if slab.calculation_basis == "Fixed Amount" and not flt(self.fixed_commission):
			frappe.throw(_("This slab pays a Fixed Amount; enter the Fixed Commission."))
		slab_rates = frappe.db.get_value("Commission Slab Structure", self.commission_slab,
			["commission_percentage", "gst_rate", "tds_rate"], as_dict=True)
		if not flt(self.fixed_commission) and not flt(self.commission_percentage):
			self.commission_percentage = slab_rates.commission_percentage
		if self.is_new() and not flt(self.gst_rate) and not flt(self.tds_rate):
			self.gst_rate, self.tds_rate = slab_rates.gst_rate, slab_rates.tds_rate
		if not flt(self.fixed_commission) and not flt(self.commission_percentage):
			frappe.throw(_("Enter the Commission Percentage or a Fixed Commission."))
		self.calculate()
		if self.calculation_status == "Draft":
			self.calculation_status = "Calculated"

	def calculate(self):
		gross = flt(self.fixed_commission) or self.commission_basis_amount * flt(self.commission_percentage) / 100
		self.gross_commission = flt(gross, 2)
		# GST/TDS rates are entered by accounts; nothing is hard-coded here.
		self.gst_amount = flt(self.gross_commission * flt(self.gst_rate) / 100, 2)
		self.tds_amount = flt(self.gross_commission * flt(self.tds_rate) / 100, 2)
		self.net_commission = flt(self.gross_commission + self.gst_amount - self.tds_amount - flt(self.other_deductions), 2)
