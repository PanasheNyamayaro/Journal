import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from google.oauth2.service_account import Credentials

st.title("📒 Velor Trading Journal")

# Load credentials from Streamlit Secrets
creds_dict = st.secrets["gcp_service_account"]

# Authenticate with Google
creds = Credentials.from_service_account_info(creds_dict)
client = gspread.authorize(creds)

# Connect to your Google Sheet
sheet = client.open("Velor_Trading_Journal").sheet1

st.success("✅ Connected to Google Sheets successfully!")

with st.form("trade_form"):
    pair = st.selectbox("Forex Pair", ["EURUSD", "GBPUSD", "XAUUSD"])
    direction = st.radio("Buy or Sell?", ["Buy", "Sell"])
    risk = st.number_input("Risk %", min_value=0.1, max_value=5.0, step=0.1)
    notes = st.text_area("Notes")

    submitted = st.form_submit_button("Log Trade")

if submitted:
    sheet.append_row([pair, direction, risk, notes])
    st.success("Trade logged ✅")
    
