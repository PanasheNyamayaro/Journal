#updated code , just so that you know whats happening:

import streamlit as st
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import io
from utils.google_sheet import append_row_to_sheet
from utils.ai_feedback import generate_ai_feedback



with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; margin-bottom:20px;'>
            <img src='assets/logo.png' style='width:90px; border-radius:6px;' />
        </div>
        """,
        unsafe_allow_html=True
    )
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
direction = st.selectbox("Direction", ["Buy", "Sell"])
entry = st.number_input("Entry Price", min_value=0.0, format="%.5f")
sl = st.number_input("Stop Loss", min_value=0.0, format="%.5f")
tp = st.number_input("Take Profit", min_value=0.0, format="%.5f")
risk_pct = st.number_input("Risk %", min_value=0.0, max_value=100.0, format="%.2f")
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
        "",  # screenshot empty for now
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
        ai_feedback
    ]

trade_data = {
    "Instrument": instrument,
    "Direction": direction,
    "Entry": entry,
    "Stop Loss": sl,
    "Take Profit": tp,
    "Risk %": risk_pct,
    "RR": rr,
    "Account Size": account_size,
    "Risk Amount": risk_amount,
    "Position Size": position_size,
    "Result": result,
    "PnL USD": pnl_usd,
    "PnL %": pnl_pct,
    "Final Balance": final_balance,
    "Session": session,
    "Market Condition": market_condition,
    "Setup Type": setup_type,
    "Execution Score": execution_score,
    "Emotion Before": emotion_before,
    "Emotion After": emotion_after,
    "Followed Plan": followed_plan,
    "What Went Wrong": what_went_wrong
}

append_row_to_sheet(row)
st.success("Trade saved!")

ai_feedback = generate_ai_feedback(trade_data)
st.subheader("AI Feedback")
st.write(ai_feedback)

row.append(ai_feedback)
append_row_to_sheet(row)


