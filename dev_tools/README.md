# DSA Loan Portal – developer tools

These are the tools used to build and document the **DSA Loan Portal** module. The ready-made documents are in `../docs/`.

On the developer's machine these files live in `<bench>/tools/`. The paths below assume that layout: copy `dev_tools/` to `<bench>/tools/` (or adjust the paths) before running anything.

## The DocTypes are generated

| File | What it does |
|---|---|
| `generate_doctypes.py` | **The source of truth for all 29 DocTypes.** For each DocType it lists the fields (`F()` field, `S()` section, `C()` column), the naming rule, the title and search fields, and the role-permission matrix (`ACCESS`). It writes the JSON files Frappe reads. |
| `controllers/` | The Python and JS controller for each DocType (business rules), copied next to each DocType's JSON. |

To apply a change:

```bash
cd ~/frappe/frappe-bench-v15
python3 tools/generate_doctypes.py apps/dsa_loan/dsa_loan/dsa_loan_portal "DSA Loan Portal"
D=apps/dsa_loan/dsa_loan/dsa_loan_portal/doctype
for f in tools/controllers/*; do n=$(basename $f); b=${n%.*}; cp $f $D/$b/$n; done
bench --site dsaloan.localhost migrate
```

The generator never overwrites an existing controller file; the copy step above is what updates them.

Change the DocTypes through the generator, not the form builder. Edits made in the UI would be lost the next time the generator runs.

## Checks

| File | What it does |
|---|---|
| `audit_site.py` | Compares the site with the DocType JSON and reports DocTypes or fields that are missing or extra. |
| `export_sample_data.py` | Writes this site's DSA records to `../sample_data/`, leaving out the two real-name applications and anything private or specific to this site. The files are loaded with `../scripts/load_sample_data.py`. |
| `dump_doctypes.py` | Prints the DocTypes as they are stored on the site. |
| `seed_demo_data.py` | An older single-loan demo. The full scenario data is in `../scripts/seed_scenarios.py`. |

The end-to-end test and the data scripts are in `../scripts/`; see the README there.

## PDFs (in `../docs/`)

| PDF | Built by |
|---|---|
| `DSA_Loan_Final_DocType_Fields.pdf`: every field of every DocType | `build_field_pdf.py` |
| `DSA_Document_Data_Fields.pdf`: the checklist and the 7 document-data DocTypes | `build_document_data_pdf.py` |
| `DSA_Loan_1_Database_Diagram.pdf`: diagrams, relationships, lifecycle | `build_db_diagram_pdf.py` |
| `DSA_Loan_2_Data_Entry_Guide.pdf`: entering data, form by form | `build_data_entry_guide_pdf.py` |
| `DSA_Loan_3_How_It_Was_Built.pdf`: design, rules, security, automation | `build_how_built_pdf.py` |

All of them read the DocType JSON, so rebuilding them after a change keeps them accurate.

- They need `reportlab`.
- `pdfkit_common.py` loads the Segoe UI font from `C:/Windows/Fonts`, so on Windows run them with the `py` launcher. On another system, change that font path in `pdfkit_common.py`.

```bash
py tools/build_db_diagram_pdf.py apps/dsa_loan/dsa_loan/dsa_loan_portal DSA_Loan_1_Database_Diagram.pdf
py tools/build_data_entry_guide_pdf.py apps/dsa_loan/dsa_loan/dsa_loan_portal DSA_Loan_2_Data_Entry_Guide.pdf
py tools/build_how_built_pdf.py . DSA_Loan_3_How_It_Was_Built.pdf
```
