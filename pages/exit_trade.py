import streamlit as st
from utils.google_sheet import get_sheet, update_row_in_sheet

st.title("Close Trade (Exit)")

df = get_sheet()

open_trades = df[df["Status"] == "OPEN"]

trade_choice = st.selectbox(
    "Select Open Trade",
    open_trades["Trade ID"].tolist()
)

trade = open_trades[open_trades["Trade ID"] == trade_choice].iloc[0]

exit_method = st.selectbox(
    "Exit Method",
    ["Take Profit (TP)", "Stop Loss (SL)", "Manual Exit (Other)"]
)

exit_notes = ""
if exit_method == "Manual Exit (Other)":
    exit_notes = st.text_input("Exit Notes")

exit_price = st.number_input("Exit Price", min_value=0.0, format="%.5f")

# Auto PnL
direction = trade["Direction"]
entry = trade["Entry"]
risk_amt = trade["Risk Amount"]

if direction == "Buy":
    pnl_usd = (exit_price - entry) * 10000   # rough pip calc
else:
    pnl_usd = (entry - exit_price) * 10000

pnl_pct = (pnl_usd / trade["Account Size"]) * 100
final_balance = trade["Account Size"] + pnl_usd

if pnl_usd > 0:
    result = "Win"
elif pnl_usd < 0:
    result = "Loss"
else:
    result = "Break Even"

st.write(f"PnL USD: {pnl_usd:.2f}")
st.write(f"PnL %: {pnl_pct:.2f}")
st.write(f"Final Balance: {final_balance:.2f}")

if st.button("Close Trade"):
    row_index = trade.name  # row in dataframe

    update_row_in_sheet(row_index, {
        "Exit Method": exit_method,
        "Exit Notes": exit_notes,
        "Exit Price": exit_price,
        "PnL USD": pnl_usd,
        "PnL %": pnl_pct,
        "Final Balance": final_balance,
        "Result": result,
        "Status": "CLOSED"
    })

    st.success("Trade Closed Successfully")
