import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------
# GOOGLE SHEETS AUTH
# -----------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

SHEET_NAME = "TradingJournal"
sheet = client.open(SHEET_NAME).sheet1

# -----------------------------
# LOAD SHEET DATA
# -----------------------------
def load_data():
    df = pd.DataFrame(sheet.get_all_records())
    return df

# -----------------------------
# SAVE ENTRY
# -----------------------------
def save_trade(data):
    sheet.append_row(data)
    st.success("Trade Logged Successfully!")
    st.rerun()  # FIXED

# -----------------------------
# MAIN APP UI
# -----------------------------
st.title("Velor Pro — Trading Journal")

df = load_data()

st.subheader("Quick Trade Entry")

# CRITICAL FIRST
instrument = st.text_input("Instrument")
direction = st.selectbox("Direction", ["Buy", "Sell"])
entry = st.number_input("Entry", format="%.5f")
sl = st.number_input("Stop Loss", format="%.5f")
tp = st.number_input("Take Profit", format="%.5f")

risk_percent = st.number_input("Risk %", 0.1, 10.0, 1.0)
account_size = st.number_input("Account Size", 0.0)
rr = st.number_input("RR", 0.0)

# AUTO CALCULATIONS
if account_size > 0 and risk_percent > 0:
    risk_amount = round(account_size * (risk_percent / 100), 2)
else:
    risk_amount = 0

position_size = 0  # Add formula later

st.write(f"**Risk Amount:** ${risk_amount}")

# ADVANCED TOGGLE
with st.expander("Advanced Details"):
    trade_type = st.selectbox("Trade Type", ["Scalp", "Day", "Swing"])
    session = st.selectbox("Session", ["Asia", "London", "New York"])
    market_condition = st.selectbox("Market Condition", ["Trending", "Ranging", "Choppy"])
    setup_type = st.text_input("Setup Type")
    indicators = st.text_input("Indicators Used")
    exec_score = st.slider("Execution Score", 1, 10)

    emotion_before = st.selectbox("Emotion Before", ["Calm", "Fear", "Greed", "Revenge", "Overconfidence"])
    emotion_during = st.selectbox("Emotion During", ["Calm", "Stressed", "Hesitant", "Impulsive"])
    emotion_after = st.selectbox("Emotion After", ["Satisfied", "Regret", "Frustrated", "Proud"])

    followed_plan = st.selectbox("Followed Plan?", ["Yes", "No"])
    news_impact = st.text_input("News Impact")
    sentiment = st.selectbox("Sentiment", ["Bullish", "Bearish", "Neutral"])
    right = st.text_area("What Went Right")
    wrong = st.text_area("What Went Wrong")

    screenshot = st.file_uploader("Screenshot (Optional)")

notes = st.text_area("Notes")
result = st.selectbox("Result", ["Win", "Loss", "Break-even"])
pnl_usd = st.number_input("PnL USD")
pnl_pct = st.number_input("PnL %")
final_balance = st.number_input("Final Balance")

# SAVE BUTTON
if st.button("Save Trade"):
    row = [
        str(datetime.now()),
        instrument,
        direction,
        entry,
        sl,
        tp,
        risk_percent,
        rr,
        account_size,
        risk_amount,
        position_size,
        trade_type,
        session,
        market_condition,
        setup_type,
        indicators,
        exec_score,
        "uploaded" if screenshot else "",
        notes,
        result,
        pnl_usd,
        pnl_pct,
        final_balance,
        emotion_before,
        emotion_during,
        emotion_after,
        followed_plan,
        news_impact,
        sentiment,
        right,
        wrong
    ]

    save_trade(row)
