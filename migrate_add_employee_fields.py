"""
One-time migration: adds the new Extended HR Fields columns to the existing
'employees' table in PostgreSQL.

Why this script exists:
  main.py calls Base.metadata.create_all(bind=engine) on startup, but that
  only CREATES tables that don't exist yet — it does NOT add new columns to
  a table that already exists. Since 'employees' already exists in your
  database, the ~39 new columns in the updated app/models/employee.py won't
  appear until you run this script once.

Usage:
    (venv) PS C:\\Users\\manav\\HR_Central> python migrate_add_employee_fields.py

Safe to run multiple times — every ADD COLUMN uses IF NOT EXISTS, so nothing
breaks or duplicates if you run it again by mistake. Existing employee rows
are left untouched; new columns are simply added with NULL/default values.
"""

from sqlalchemy import text
from app.database import engine

# (column_name, SQL type + default) — must match app/models/employee.py
NEW_COLUMNS = [
    ("doc_medical_certificate",       "VARCHAR(20) DEFAULT 'Pending'"),

    ("emergency_contact_number",      "VARCHAR(15)"),
    ("emergency_contact_person",      "VARCHAR(100)"),
    ("emergency_relation",            "VARCHAR(50)"),

    ("med_allowance",                 "FLOAT DEFAULT 0"),
    ("misc_allowance",                "FLOAT DEFAULT 0"),
    ("fixed_other_allowance",         "FLOAT DEFAULT 0"),
    ("variable_pay_annual",           "FLOAT DEFAULT 0"),
    ("esi_employer_contribution",     "FLOAT DEFAULT 0"),
    ("pf_employer_contribution",      "FLOAT DEFAULT 0"),
    ("esic_employee_deduction",       "FLOAT DEFAULT 0"),
    ("pf_employee_deduction",         "FLOAT DEFAULT 0"),

    ("insurance_amount",              "FLOAT DEFAULT 0"),
    ("bonus_amount",                  "FLOAT DEFAULT 0"),
    ("gratuity_amount",               "FLOAT DEFAULT 0"),
    ("pl_amount",                     "FLOAT DEFAULT 0"),
    ("cl_amount",                     "FLOAT DEFAULT 0"),

    ("doc_personal_details",          "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_form_26",                   "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_esi_form1",                 "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_form2_pf",                  "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_nomination_form_f",         "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_epf_form11",                "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_joining_report",            "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_rules_regulation_ack",      "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_appointment_letter",        "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_confirmation_letter",       "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_service_record",            "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_increment_letter",          "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_promotion_letter",          "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_employment_history_sheet",  "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_jd",                        "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_master_task_sheet",         "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_kra",                       "VARCHAR(20) DEFAULT 'Pending'"),
    ("doc_kpi",                       "VARCHAR(20) DEFAULT 'Pending'"),

    ("asset_sim",                     "VARCHAR(20) DEFAULT 'Pending'"),
    ("asset_laptop",                  "VARCHAR(20) DEFAULT 'Pending'"),

    ("file_number",                   "VARCHAR(50)"),
    ("date_of_leaving",                "VARCHAR(20)"),
    ("full_final_completed",          "VARCHAR(20) DEFAULT 'Pending'"),
    ("relieving_letter_issued",       "VARCHAR(20) DEFAULT 'Pending'"),
    ("remarks",                       "TEXT"),
    ("address_verification_link",     "VARCHAR(500)"),

    ("source",                       "VARCHAR(30)"),
    ("approved_by",                  "VARCHAR(100)"),
]

def run():
    with engine.begin() as conn:
        for col_name, col_def in NEW_COLUMNS:
            sql = f'ALTER TABLE employees ADD COLUMN IF NOT EXISTS {col_name} {col_def};'
            conn.execute(text(sql))
            print(f"✅ ensured column: {col_name}")
    print("\n🎉 Migration complete — employees table now has all extended HR fields.")

if __name__ == "__main__":
    run()