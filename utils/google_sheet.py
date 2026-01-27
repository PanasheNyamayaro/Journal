import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = "Velor_Tading_Journal"
WORKSHEET_NAME = "Sheet1"

def get_sheet():
    creds_info = st.secrets["gcp_service_account"]

    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)


def append_row_to_sheet(row):
    sheet = get_sheet()
    sheet.append_row(row)
