import sqlite3
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from services.db_init import initialize_database
from services.db_service import append_row

# ---------- Google Auth ----------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scope
)

client = gspread.authorize(creds)

SPREADSHEET_ID = "1fX4AkwJbaZnRwRREzWyJJHVLJWqEoAAlsgqtaYNS-Kg"

spreadsheet = client.open_by_key(SPREADSHEET_ID)

# ---------- Initialize SQLite ----------
initialize_database()

tables = [
    "Clients",
    "Editors",
    "Work_Assignments",
    "Billing",
    "Expenses",
    "Social_Insights"
]

# build worksheet dictionary once
worksheets = {ws.title: ws for ws in spreadsheet.worksheets()}

for table in tables:

    print(f"Migrating {table}...")

    sheet = worksheets[table]

    data = sheet.get_all_values()

    headers = data[0]
    rows = data[1:]

    df = pd.DataFrame(rows, columns=headers)

    for _, row in df.iterrows():
        append_row(table, row.to_dict())

print("Migration completed successfully.")