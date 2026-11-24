"""Each DSA DocType now numbers its records from its own counter (LEAD-2026-, LDR-, ...).

Start every counter after the highest number already used with that prefix, so no new name collides
with an existing record (e.g. imported LDR-00070). Safe to run any time; counters only move forward.
"""

import re

import frappe

NAME = re.compile(r"^(.*?)(\d+)$")


def execute():
	for doctype, autoname in frappe.get_all(
		"DocType", {"module": "DSA Loan Portal", "istable": 0}, ["name", "autoname"], as_list=True
	):
		if not autoname or ".#####" not in autoname:
			continue
		top = {}
		for name in frappe.get_all(doctype, pluck="name"):
			m = NAME.match(name)
			if m:
				top[m.group(1)] = max(top.get(m.group(1), 0), int(m.group(2)))
		for prefix, current in top.items():
			frappe.db.sql(
				"insert into tabSeries (name, current) values (%s, %s) on duplicate key update current = greatest(current, %s)",
				(prefix, current, current),
			)
