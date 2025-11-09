import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="Velor Journal", page_icon="📈", layout="centered")

# Google Auth Setup
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

# Open your Sheet
sheet = client.open("Velor_Tading_Journal").sheet1  # update if name changed

st.title("📓 Velor Trade Journal")
st.write("Log your trade details below ⬇")

# ───────────────────────────────────────────
# ✅ Trade Form
# ───────────────────────────────────────────
with st.form("trade_form"):
    date = st.date_input("Date", datetime.now())
    pair = st.text_input("Pair (ex: EURUSD)")
    direction = st.selectbox("Direction", ["Buy", "Sell"])
    entry_price = st.number_input("Entry Price", value=0.0, format="%.5f")
    stop_loss = st.number_input("Stop Loss (pips)", value=0.0)
    take_profit = st.number_input("Take Profit (pips)", value=0.0)
    risk_percent = st.number_input("Risk %", value=1.0)
    
    # Auto calculate Result R (temporary default)
    result_r = 0  # will be calculated later

    notes = st.text_area("Notes (optional)")
    ai_feedback = ""  # reserved for AI

    submitted = st.form_submit_button("✅ Log Trade")

if submitted:
    row = [
        str(date), pair, direction, entry_price,
        stop_loss, take_profit,
        risk_percent, result_r,
        notes, ai_feedback
    ]
    sheet.append_row(row)
    st.success("✅ Trade logged successfully!")
