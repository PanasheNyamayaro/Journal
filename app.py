
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(credentials)

# Open sheet (CHANGE name to yours)
sheet = client.open("Velor Journal DB").sheet1

st.title("📒 Velor Trading Journal")

st.write("✅ Connected to Google Sheets successfully!")
with st.form("trade_form"):
    pair = st.selectbox("Forex Pair", ["EURUSD", "GBPUSD", "XAUUSD"])
    direction = st.radio("Buy or Sell?", ["Buy", "Sell"])
    risk = st.number_input("Risk %", min_value=0.1, max_value=5.0, step=0.1)
    notes = st.text_area("Notes")

    submitted = st.form_submit_button("Log Trade")

if submitted:
    sheet.append_row([pair, direction, risk, notes])
    st.success("Trade logged ✅")
    
