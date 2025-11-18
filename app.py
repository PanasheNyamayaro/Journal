import streamlit as st
import datetime
from utils.google_sheet import append_row_to_sheet

st.title("Trade Log")

# --- Critical Fields ---
st.subheader("Quick Log")

instrument = st.text_input("Instrument")
direction = st.selectbox("Direction", ["Buy", "Sell"])
entry = st.number_input("Entry Price", min_value=0.0, format="%.5f")
sl = st.number_input("Stop Loss", min_value=0.0, format="%.5f")
tp = st.number_input("Take Profit", min_value=0.0, format="%.5f")
risk_pct = st.number_input("Risk %", min_value=0.0, max_value=100.0, format="%.2f")
account_size = st.number_input("Account Size (USD)", min_value=0.0, format="%.2f")

# --- Auto Calculations ---
risk_amount = account_size * (risk_pct / 100) if account_size and risk_pct else 0
rr = ((tp - entry) / (entry - sl)) if entry and sl and tp and (entry - sl) != 0 else 0
position_size = (risk_amount / abs(entry - sl)) if entry and sl and risk_amount else 0

st.write(f"**Risk Amount:** {risk_amount:.2f} USD")
st.write(f"**RR:** {rr:.2f}")
st.write(f"**Position Size:** {position_size:.2f} units")

# --- Toggle Advanced Fields ---
with st.expander("Advanced Fields"):
    trade_type = st.selectbox("Trade Type", ["Market", "Limit", "Stop", "Other"])
    session = st.selectbox("Session", ["Asian", "London", "New York", "Other"])
    market_condition = st.text_input("Market Condition")
    setup_type = st.text_input("Setup Type")
    indicators_used = st.text_input("Indicators Used")
    execution_score = st.slider("Execution Score", 1, 10)
    notes = st.text_area("Notes")
    result = st.selectbox("Result", ["Win", "Loss", "Break Even"])
    pnl_usd = st.number_input("PnL USD", format="%.2f")
    pnl_pct = st.number_input("PnL %", format="%.2f")
    final_balance = st.number_input("Final Balance", format="%.2f")
    emotion_before = st.text_input("Emotion Before")
    emotion_after = st.text_input("Emotion After")
    followed_plan = st.selectbox("Followed Plan", ["Yes", "No", "Partial"])
    news_impact = st.text_input("News Impact")
    sentiment = st.text_input("Sentiment")
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
        setup_type,
        indicators_used,
        execution_score,
        "",  # screenshot empty
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
    ]

    append_row_to_sheet(row)
    st.success("Trade saved!")
