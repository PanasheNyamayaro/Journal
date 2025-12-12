import streamlit as st
import datetime
from utils.google_sheet import append_row_to_sheet

st.title("New Trade (Entry)")

# Generate Trade ID
trade_id = f"T-{int(datetime.datetime.now().timestamp())}"

instrument = st.selectbox("Instrument", ["EURUSD","GBPUSD","USDJPY","XAUUSD","US30","NAS100","BTCUSD"])
direction = st.selectbox("Direction", ["Buy", "Sell"])
entry = st.number_input("Entry Price", min_value=0.0, format="%.5f")
sl = st.number_input("Stop Loss", min_value=0.0, format="%.5f")
tp = st.number_input("Take Profit", min_value=0.0, format="%.5f")
risk_pct = st.number_input("Risk %", min_value=0.0, max_value=100.0, format="%.2f")
account_size = st.number_input("Account Size (USD)", min_value=0.0, format="%.2f")

# Auto-calcs
risk_amount = account_size * (risk_pct / 100) if account_size and risk_pct else 0

# Create row with empty exit fields
row = [
    trade_id,                        # NEW
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    instrument,
    direction,
    entry,
    sl,
    tp,
    risk_pct,
    risk_amount,
    "",   # Exit Method
    "",   # Exit Notes
    "",   # Result
    "",   # Exit Price
    "",   # PnL USD
    "",   # PnL %
    "",   # Final Balance
    "OPEN"  # NEW status column
]

if st.button("Save Entry"):
    append_row_to_sheet(row)
    st.success(f"Trade Created: {trade_id}")
