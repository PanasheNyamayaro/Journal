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
    return client.open("Velor_Tading_Journal").worksheet("Sheet1")


def append_row_to_sheet(row):
    sheet = get_sheet()
    sheet.append_row(row, table_range="A1")

def get_sheet():
    creds_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(creds)
    return client.open("Velor_Trading_Journal").sheet1


def append_row_to_sheet(row):
    sheet = get_sheet()
    sheet.append_row(row)


def update_row_in_sheet(row_index, updates: dict):
    sheet = get_sheet()

    headers = sheet.row_values(1)

    for col_name, value in updates.items():
        if col_name in headers:
            col_index = headers.index(col_name) + 1
            sheet.update_cell(row_index + 2, col_index, value)
