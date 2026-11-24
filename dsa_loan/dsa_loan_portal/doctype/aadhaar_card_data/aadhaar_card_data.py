# Copyright (c) 2026
# For license information, please see license.txt

from dsa_loan.dsa_loan_portal.document_data import ExtractedDocument, clean_last_4


class AadhaarCardData(ExtractedDocument):
	def validate_document(self):
		clean_last_4(self, "aadhaar_last_4", "Aadhaar number")
