import streamlit as st
import datetime
#from utils.google_sheet import append_row_to_sheet
from utils.google_sheet import get_sheet
st.write(get_sheet().get_all_values())

st.title("Trade Log")

# --- Quick Log (Critical) ---
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

# Live PnL auto calc (only if TP/SL isn't hit yet)
# Final Balance auto calc = account_size + pnl_usd
pnl_usd = 0  # Default. User sets Result (win/loss/breakeven), then amount is auto handled in Review page.
pnl_pct = (pnl_usd / account_size * 100) if account_size != 0 else 0
final_balance = account_size + pnl_usd

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
    result = st.selectbox("Result", ["Win", "Loss", "Break Even"])

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
    ]

    append_row_to_sheet(row)
    st.success("Trade saved!")
