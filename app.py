# app.py -- Velor Trading Journal (multi-step, mobile-friendly)
import streamlit as st
from datetime import datetime, date, time as dtime
import gspread
from google.oauth2.service_account import Credentials
import math

st.set_page_config(page_title="Velor Journal", page_icon="📒", layout="centered")

# ---------- Google Sheets auth (uses st.secrets["google_service_account"]) ----------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
gc = gspread.authorize(creds)

SHEET_NAME = "Velor_Tading_Journal"   # <--- ensure this matches your sheet title EXACTLY
sheet = gc.open(SHEET_NAME).sheet1

# ---------- Helper functions ----------
def calc_rr(entry, stop, tp, direction):
    try:
        if direction == "Buy":
            risk = abs(entry - stop)
            reward = abs(tp - entry)
        else:
            risk = abs(stop - entry)
            reward = abs(entry - tp)
        if risk == 0:
            return None
        return round(reward / risk, 2)
    except Exception:
        return None

def calc_pips(value1, value2, pair):
    # rough pip calc: if pair contains 'JPY' use 2 decimal pips, else 4
    try:
        if "JPY" in pair.upper():
            multiplier = 100
        else:
            multiplier = 10000
        return round((value2 - value1) * multiplier, 1)
    except Exception:
        return 0

def approx_position_size(account_balance, risk_percent, entry, stop, pair):
    # approximate: money risked / price-distance
    try:
        risk_amount = account_balance * (risk_percent / 100.0)
        pip_diff = abs(entry - stop)
        if pip_diff == 0:
            return 0
        # this yields units of quote-currency per pip-unit — keep it simple and labelled 'approx'
        pos = risk_amount / pip_diff
        return round(pos, 2)
    except Exception:
        return 0

# initialize session state for wizard
if "step" not in st.session_state:
    st.session_state.step = 1

st.title("📒 Velor Trading Journal — Log a Trade")
st.caption("Fast multi-step form. Use Next / Back to navigate. Fields optimized for mobile.")

# ---------- STEP 1: Account & Market Context ----------
if st.session_state.step == 1:
    st.subheader("Step 1 — Account & Market")
    account_balance = st.number_input("Account Balance (before trade, $)", min_value=0.0, value=1000.0, step=10.0, format="%.2f")
    risk_percent = st.number_input("Risk % on this trade", min_value=0.1, max_value=100.0, value=1.0, step=0.1, format="%.2f")
    if risk_percent > 5.0:
        st.warning("Warning: You are risking more than 5% on this trade.")
    session = st.selectbox("Trading Session", ["London", "New York", "Asian", "London/New York Overlap", "Custom"])
    market_condition = st.selectbox("Market Condition", ["Trending", "Ranging", "High Volatility", "News-driven", "Other"])
    day_of_week = datetime.now().strftime("%A")
    st.markdown(f"**Day:** {day_of_week}")
    news_filter = st.selectbox("News Filter", ["None", "Minor", "Major (avoid trading)"])
    exact_time = st.time_input("Exact Time (optional)", value=datetime.now().time())
    if st.button("Next"):
        st.session_state.step = 2
        # store values
        st.session_state.account_balance = account_balance
        st.session_state.risk_percent = risk_percent
        st.session_state.session = session
        st.session_state.market_condition = market_condition
        st.session_state.day_of_week = day_of_week
        st.session_state.news_filter = news_filter
        st.session_state.exact_time = exact_time

# ---------- STEP 2: Setup & Execution ----------
elif st.session_state.step == 2:
    st.subheader("Step 2 — Setup & Execution")
    pair = st.text_input("Pair / Symbol (ex: EURUSD)", value="EURUSD").upper()
    direction = st.selectbox("Direction", ["Buy", "Sell"])
    setup_type = st.selectbox("Setup Type", ["Breakout", "Pullback", "Reversal", "Support/Resistance", "Trendline", "Orderflow", "Other"])
    entry_price = st.number_input("Entry Price", value=1.00000, format="%.5f")
    stop_loss = st.number_input("Stop Loss Price", value=0.0, format="%.5f")
    take_profit = st.number_input("Take Profit Price", value=0.0, format="%.5f")
    exec_quality = st.selectbox("Execution Quality (Plan followed?)", ["Yes", "No", "Partly"])
    # auto calculations preview
    rr = calc_rr(entry_price, stop_loss, take_profit, direction)
    pips_risk = calc_pips(entry_price, stop_loss, pair)
    pips_target = calc_pips(entry_price, take_profit, pair)
    pos_size_approx = approx_position_size(st.session_state.get("account_balance", 1000.0), st.session_state.get("risk_percent", 1.0), entry_price, stop_loss, pair)
    st.markdown(f"**Approx Position Size:** {pos_size_approx} (approx units)")
    st.markdown(f"**Risk/Reward (R):** {rr if rr is not None else 'N/A'} — **Pips risk**: {pips_risk} — **Pips target**: {pips_target}")
    cols = st.columns([1,1])
    if cols[0].button("Back"):
        st.session_state.step = 1
    if cols[1].button("Next"):
        st.session_state.pair = pair
        st.session_state.direction = direction
        st.session_state.setup_type = setup_type
        st.session_state.entry_price = entry_price
        st.session_state.stop_loss = stop_loss
        st.session_state.take_profit = take_profit
        st.session_state.exec_quality = exec_quality
        st.session_state.rr = rr
        st.session_state.pips_risk = pips_risk
        st.session_state.pips_target = pips_target
        st.session_state.pos_size_approx = pos_size_approx
        st.session_state.step = 3

# ---------- STEP 3: Psychology ----------
elif st.session_state.step == 3:
    st.subheader("Step 3 — Psychology")
    emotion_before = st.selectbox("Emotion Before Trade", ["Calm", "Confident", "Nervous", "Rushed", "Bored", "Greedy", "Revenge"])
    emotion_after = st.selectbox("Emotion After Trade", ["Relieved", "Annoyed", "Proud", "Neutral", "Upset", "Surprised"])
    patience = st.slider("Patience Score", min_value=1, max_value=5, value=3)
    cols = st.columns([1,1])
    if cols[0].button("Back"):
        st.session_state.step = 2
    if cols[1].button("Next"):
        st.session_state.emotion_before = emotion_before
        st.session_state.emotion_after = emotion_after
        st.session_state.patience = patience
        st.session_state.step = 4

# ---------- STEP 4: Outcome & Reflection ----------
elif st.session_state.step == 4:
    st.subheader("Step 4 — Outcome & Reflection")
    result = st.selectbox("Result", ["Win", "Loss", "Break Even"])
    pnl_usd = st.number_input("Profit / Loss ($)", value=0.0, format="%.2f")
    pnl_percent = round((pnl_usd / st.session_state.get("account_balance", 1.0)) * 100, 2)
    final_balance = round(st.session_state.get("account_balance", 0.0) + pnl_usd, 2)
    repeat = st.radio("Would you take this trade again?", ["Yes", "No"])
    went_right = st.selectbox("What went right?", ["Choice: Setup, Execution, Risk Management, None"])
    went_wrong = st.selectbox("What went wrong?", ["Choice: Setup, Execution, Risk Management, Impulse"])
    notes = st.text_area("Notes (optional)")
    # screenshot upload - we store filename or URL placeholder
    screenshot = st.file_uploader("Upload screenshot (optional)", type=["png","jpg","jpeg"])
    if screenshot is not None:
        # we won't upload image to sheet; we can save filename or use later storage
        screenshot_name = screenshot.name
    else:
        screenshot_name = ""
    cols = st.columns([1,1])
    if cols[0].button("Back"):
        st.session_state.step = 3

    if cols[1].button("Save Trade → Sheets"):
        # build row matching sheet columns exactly
        row = [
            datetime.now().isoformat(),                       # Timestamp
            st.session_state.get("account_balance", ""),      # Account Balance
            st.session_state.get("risk_percent", ""),         # Risk%
            st.session_state.get("pos_size_approx", ""),      # Position Size (approx)
            st.session_state.get("session", ""),              # Trading Session
            st.session_state.get("market_condition", ""),     # Market Condition
            st.session_state.get("day_of_week", ""),          # Day of Week
            st.session_state.get("news_filter", ""),          # News Filter
            str(st.session_state.get("exact_time", "")),      # Exact Time
            st.session_state.get("pair", ""),                 # Pair
            st.session_state.get("direction", ""),            # Direction
            st.session_state.get("setup_type", ""),           # Setup Type
            st.session_state.get("entry_price", ""),          # Entry
            st.session_state.get("stop_loss", ""),            # Stop Loss
            st.session_state.get("take_profit", ""),          # Take Profit
            st.session_state.get("rr", ""),                   # RR
            st.session_state.get("pips_risk", ""),            # Pips Risk
            st.session_state.get("pips_target", ""),          # Pips Target
            st.session_state.get("exec_quality", ""),         # Execution Quality
            st.session_state.get("emotion_before", ""),       # Emotion Before
            st.session_state.get("emotion_after", ""),        # Emotion After
            st.session_state.get("patience", ""),             # Patience Score
            result,                                           # Result
            round(pnl_usd,2),                                 # PnL $
            round(pnl_percent,2),                             # PnL %
            final_balance,                                    # Final Account Balance
            repeat,                                           # Repeat Trade?
            went_right,                                       # What went right
            went_wrong,                                       # What went wrong
            notes,                                            # Notes
            screenshot_name,                                  # Screenshot filename
            ""                                                # AI_Feedback (reserved)
        ]
        sheet.append_row(row)
        st.success("✅ Trade saved to Google Sheets")
        # reset steps to 1 for next entry
        st.session_state.step = 1
