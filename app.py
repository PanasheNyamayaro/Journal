#updated code , just so that you know whats happening:

import streamlit as st
import datetime
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
from utils.google_sheet import append_row_to_sheet
from utils.ai_feedback import generate_ai_feedback
import datetime
import pytz

st.logo("logo.png")

PIP_VALUES = {
    "EURUSD": 1,
    "GBPUSD": 1,
    "USDJPY": 0.917,   # depends on price, approx
    "XAUUSD": 1,      # gold = $1 per pip (0.01 move)
    "US30": 1,        # indices depend on broker, adjust
    "NAS100": 1,
    "BTCUSD": 1       # crypto varies by tick size
}

def get_pip_distance(instrument, entry, sl, tp, direction):
    pip_value = PIP_VALUES.get(instrument.upper(), 1)  # default 10

    if direction == "Buy":
        sl_distance = entry - sl
        tp_distance = tp - entry
    else:  # Sell
        sl_distance = sl - entry
        tp_distance = entry - tp

    return sl_distance, tp_distance, pip_value

st.title("Trade Log")

# --- Quick Log (Critical) ---
st.subheader("Quick Log")

instrument = st.selectbox("Instrument",["EURUSD","GBPUSD","USDJPY","XAUUSD","US30","NAS100","BTCUSD"])


def get_active_sessions():
    # 1. Get current time in UTC
    now_utc = datetime.datetime.now(pytz.utc)
    
    # 2. Define Session Hours in UTC (Standard Times)
    # Note: These may vary slightly based on seasonal DST shifts.
    sessions = {
        "Sydney": {"open": 21, "close": 6},  # 9 PM - 6 AM UTC
        "Tokyo":  {"open": 0,  "close": 9},  # 12 AM - 9 AM UTC
        "London": {"open": 7,  "close": 16}, # 7 AM - 4 PM UTC
        "New York": {"open": 13, "close": 22} # 1 PM - 10 PM UTC
    }
    
    active = []
    
    # 3. Check for Weekends (Trading is generally closed Sat/Sun)
    if now_utc.weekday() >= 5:
        return ["Market Closed (Weekend)"]

    current_hour = now_utc.hour
    
    for name, hours in sessions.items():
        start = hours["open"]
        end = hours["close"]
        
        # Handle sessions that cross midnight (e.g., Sydney)
        if start > end:
            if current_hour >= start or current_hour < end:
                active.append(name)
        else:
            if start <= current_hour < end:
                active.append(name)
                
    return active if active else ["No major sessions active"]


# Output results
current_active = get_active_sessions()
print(f"Current UTC Time: {datetime.datetime.now(pytz.utc).strftime('%H:%M')}")
st.write(f"Active Sessions: {', '.join(current_active)}")

direction = st.selectbox("Direction", ["Buy", "Sell"])
entry = st.number_input("Entry Price", min_value=0.0, format="%.5f")
sl = st.number_input("Stop Loss", min_value=0.0, format="%.5f")
tp = st.number_input("Take Profit", min_value=0.0, format="%.5f")
risk_pct = st.number_input("Risk %", min_value=0.0, max_value=100.0, format="%.2f")
if risk_pct > 5:
    st.warning(f"{risk_pct}% risk is too high.",icon = "⚠️")
else:
    pass
account_size = st.number_input("Account Size (USD)", min_value=0.0, format="%.2f")
swap = st.number_input("Swap", format="%.2f")
commision = st.number_input("Commision", format="%.2f")

sl_dist, tp_dist, pip_value = get_pip_distance(
    instrument, entry, sl, tp, direction
)

st.write(sl_dist * 1000)

# --- Auto Calculations ---
risk_amount = account_size * (risk_pct / 100) if account_size and risk_pct else 0
rr = tp_dist / sl_dist if sl_dist != 0 else 0

#rr = ((tp - entry) / (entry - sl)) if entry and sl and tp and (entry - sl) != 0 else 0

if sl_dist > 0:
    position_size = risk_amount / (sl_dist * pip_value)
else:
    position_size = 0
st.write(position_size)

#position_size = (risk_amount / abs(entry - sl)) if entry and sl and risk_amount else 0

# Live PnL auto calc (only if TP/SL isn't hit yet)
# Final Balance auto calc = account_size + pnl_usd
pnl_usd = 0  # Default. User sets Result (win/loss/breakeven), then amount is auto handled in Review page.


result = st.selectbox("Result", ["Win", "Loss", "Break Even"])
if result == "Win":
    pnl_usd = risk_amount * rr
elif result == "Loss":
    pnl_usd = -risk_amount 
else:
    pnl_usd = pnl_usd
final_balance = account_size + pnl_usd 
pnl_pct = (pnl_usd / account_size) * 100 if account_size != 0 else 0

st.write(pnl_usd)
st.write(final_balance)

st.write(f"**Risk Amount:** {risk_amount:.2f} USD")
st.write(f"**RR:** {rr:.2f}")
st.write(f"**Position Size:** {position_size:.2f} units")
st.write(f"**PnL % (auto):** {pnl_pct:.2f}%")
st.write(f"**Final Balance (auto):** {final_balance:.2f} USD")

# --- Advanced Fields ---
with st.expander("Advanced Fields"):
    trade_type = st.selectbox("Trade Type", ["Market", "Limit", "Stop", "Other"])

    session = st.selectbox(
        "Session",
        ["Sydney", "Tokyo", "London", "London–New York Overlap", "New York"]
    )

    market_condition = st.selectbox(
        "Market Condition",
        ["Trending", "Ranging", "Choppy"]
    )

    setup_type = st.multiselect(
        "Setup Type (Choose All That Apply)",
        ["Trend Continuation", "Breakout", "Support and Resistance", 
         "Price Imbalance", "Order Block", "Liquidity Sweep"]
    )

    indicators_used = st.text_input("Indicators Used")
    execution_score = st.slider("Execution Score", 1, 10)

    notes = st.text_area("Notes")

    news_impact = st.selectbox("News Impact", ["High", "Neutral", "Low"])
    sentiment = st.selectbox("Sentiment", ["Risk ON", "Neutral", "Risk OFF"])

    emotion_before = st.text_input("Emotion Before")
    emotion_after = st.text_input("Emotion After")
    followed_plan = st.selectbox("Followed Plan", ["Yes", "No", "Partial"])

    what_went_right = st.text_area("What Went Right")
    what_went_wrong = st.text_area("What Went Wrong")
if st.button("AI feedback"):
    trade_data = { "Instrument": instrument, "Direction": direction, "Entry": entry, "Stop Loss": sl, "Take Profit": tp, "Risk %": risk_pct, "RR": rr, "Account Size": account_size, "Risk Amount": risk_amount, "Position Size": position_size, "Result": result, "PnL USD": pnl_usd, "PnL %": pnl_pct, "Final Balance": final_balance, "Session": session, "Market Condition": market_condition, "Setup Type": setup_type, "Execution Score": execution_score, "Emotion Before": emotion_before, "Emotion After": emotion_after, "Followed Plan": followed_plan, "What Went Wrong": what_went_wrong }
    ai_feedback = generate_ai_feedback(trade_data)
    st.write(ai_feedback)
# --- Save Button ---
if st.button("Save Trade"):
    row = [
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        instrument,
        direction,
        entry,
        sl,
        tp,
        risk_pct,
        rr,
        account_size,
        risk_amount,
        position_size,
        trade_type,
        session,
        market_condition,
        ", ".join(setup_type),
        indicators_used,
        execution_score,
        "",
        notes,
        result,
        pnl_usd,
        pnl_pct,
        final_balance,
        emotion_before,
        emotion_after,
        followed_plan,
        news_impact,
        sentiment,
        what_went_right,
        what_went_wrong,
        ""   # AI feedback placeholder
    ]

    append_row_to_sheet(row)
    st.success("Trade saved (NO AI)")
