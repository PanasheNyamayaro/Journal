import gspread
import streamlit as st
from google.oauth2.service_account import Credentials

# ---------- AUTH ----------
def get_gspread_client():
    creds_info = st.secrets["gcp_service_account"]

    creds = Credentials.from_service_account_info(
        creds_info,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )

    return gspread.authorize(creds)


# ---------- USER → SHEET LOOKUP ----------
def get_user_sheet_id(user_email: str):
    """
    Looks up which Google Sheet belongs to the logged-in user
    from the Velor_User_Map sheet.
    """
    client = get_gspread_client()

    map_sheet = client.open("Velor_User_Map").sheet1
    records = map_sheet.get_all_records()

    for row in records:
        if row["email"].strip().lower() == user_email.strip().lower():
            return row["sheet_id"]

    return None


# ---------- MAIN JOURNAL SHEET ----------
def get_sheet():
    user = st.experimental_user

    if not user or not user.email:
        st.error("You must be logged in to use the journal.")
        st.stop()

    sheet_id = get_user_sheet_id(user.email)

    if not sheet_id:
        st.error("No journal assigned to this account.")
        st.stop()

    client = get_gspread_client()
    return client.open_by_key(sheet_id).sheet1


# ---------- WRITE ----------
def append_row_to_sheet(row: list):
    sheet = get_sheet()
    sheet.append_row(row, value_input_option="USER_ENTERED")
