import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ✅ Correct Scopes
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ✅ Load service account credentials from secrets
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

try:
    sheet = client.open("Velor_Tading_Journal").sheet1
    st.success("✅ Connected to Google Sheets Successfully!")
except Exception as e:
    st.error(f"❌ Failed to connect: {e}")

