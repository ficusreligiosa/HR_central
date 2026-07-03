import gspread
from google.oauth2.service_account import Credentials
import os

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

CREDS_FILE = os.path.join(
    BASE_DIR,
    "credentials",
    "google_credentials.json"
)

SHEET_ID = "1SfY8YmXUKfOP3t4nwjBbOb9SRFdOW7y94jhJNjOOX6E"


def get_google_sheet():
    creds = Credentials.from_service_account_file(
        CREDS_FILE,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(SHEET_ID)

    worksheet = spreadsheet.sheet1

    return worksheet