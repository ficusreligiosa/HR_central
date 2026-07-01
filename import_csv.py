"""
CSV Import Script — Google Form Submissions → Form Inbox (Pending)
Usage:
    python import_csv.py employees.csv

Employees will appear in Form Inbox for HR to review and approve.
"""
import sys
import csv
import re
from app.database import SessionLocal, engine
from app.models.form_submission import FormSubmission
from app.database import Base

def parse_bool_str(val):
    if not val: return 'No'
    return 'Yes' if str(val).strip().lower() in ('yes', 'true', '1', 'y') else 'No'

def clean_number(val):
    if not val: return None
    val = str(val).strip().replace(' ', '')
    try:
        f = float(val)
        if f > 1e10:
            return str(int(f))
        return val
    except:
        return val

def clean_date(val):
    if not val: return None
    val = str(val).strip()
    if re.match(r'^\d{2}-\d{2}-\d{4}$', val): return val
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', val):
        parts = val.split('/')
        return f"{int(parts[0]):02d}-{int(parts[1]):02d}-{parts[2]}"
    return val

def map_row(row):
    name = str(row.get('Name', '')).strip()
    if not name: return None

    return {
        'name':             name,
        'father_name':      str(row.get("Father's Name", '') or row.get("Father/Husband Name", '')).strip(),
        'date_of_birth':    clean_date(row.get('Date of Birth') or row.get('DOB(As per Adhar)')),
        'date_of_joining':  clean_date(row.get('Date of Joining') or row.get('Date Of Joining')),
        'marital_status':   str(row.get('Marital Status', '')).strip(),
        'gender':           str(row.get('Gender', '')).strip(),
        'contact':          clean_number(row.get('Contact Number')),
        'email':            str(row.get('Email', '') or row.get('E-mail ID (Personal)', '')).strip(),
        'aadhar_number':    clean_number(row.get('Adhar card Number') or row.get('Aadhar')),
        'pan_number':       str(row.get('Pan Number') or row.get('PAN') or '').strip(),
        'bank_name':        str(row.get('Bank Name', '')).strip(),
        'account_number':   clean_number(row.get('Bank Account Number') or row.get('Bank Account No.')),
        'ifsc_code':        str(row.get('IFSC Code') or row.get('IFSC CODE') or '').strip(),
        'blood_group':      str(row.get('Blood Group', '')).strip(),
        'qualification':    str(row.get('Last qualification Certificate') or row.get('Qualification') or '').strip(),
        'is_pf_deducted':   parse_bool_str(row.get('Is PF Deducted\n') or row.get('Is PF Deducted')),
        'is_esic_deducted': parse_bool_str(row.get('Is ESIC Deducted\n') or row.get('Is ESIC Deducted')),
        'aadhar_link':      str(row.get('Upload adhar Card', '')).strip(),
        'pan_link':         str(row.get('Upload Pan', '')).strip(),
        'cheque_link':      str(row.get('Cheque', '')).strip(),
        'offer_letter_link':str(row.get('Upload Offer Letter', '')).strip(),
        'submitted_at':     str(row.get('Timestamp', '')).strip(),
        'status':           'pending',
    }

def import_csv(filepath):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    with open(filepath, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} rows in CSV\n")

    created = 0
    skipped = 0
    errors  = 0

    for i, row in enumerate(rows, 1):
        try:
            data = map_row(row)
            if not data:
                print(f"Row {i}: Skipped (no name)")
                skipped += 1
                continue

            # Skip duplicates based on name + contact
            existing = db.query(FormSubmission).filter(
                FormSubmission.name == data['name'],
                FormSubmission.contact == data['contact']
            ).first()

            if existing:
                print(f"Row {i}: SKIP — {data['name']} already in inbox")
                skipped += 1
                continue

            sub = FormSubmission(**data)
            db.add(sub)
            db.commit()
            print(f"Row {i}: ✅ Added to inbox — {data['name']}")
            created += 1

        except Exception as e:
            db.rollback()
            print(f"Row {i}: ❌ Error — {e}")
            errors += 1

    db.close()
    print(f"\n{'='*50}")
    print(f"Done! Added to inbox: {created} | Skipped: {skipped} | Errors: {errors}")
    print(f"\nGo to Form Inbox in the app to review and approve each submission.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python import_csv.py your_file.csv")
        sys.exit(1)
    import_csv(sys.argv[1])