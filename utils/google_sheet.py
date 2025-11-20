import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

def get_sheet():
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    return client.open("Velor_Trading_Journal").sheet1

def append_row_to_sheet(row):
    sheet = get_sheet()
    sheet.append_row(row)
