import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

st.set_page_config(page_title="Velor Dashboard", page_icon="📊", layout="centered")

# Google Sheets auth
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
gc = gspread.authorize(creds)
sheet = gc.open("Velor_Tading_Journal").sheet1

# Load sheet data into a DataFrame
data = sheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])

# Convert types
numeric_cols = ["RR", "PnL_USD", "PnL_Percent", "Final Balance"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Dashboard metrics
total_trades = len(df)
wins = len(df[df["Result"] == "Win"])
losses = len(df[df["Result"] == "Loss"])

win_rate = round((wins / total_trades) * 100, 2) if total_trades > 0 else 0
avg_rr = round(df["RR"].mean(), 2) if total_trades > 0 else 0
avg_pnl_percent = round(df["PnL_Percent"].mean(), 2) if total_trades > 0 else 0

st.title("📊 Velor Journal Dashboard")
st.caption("Live metrics from your trading history")

col1, col2, col3 = st.columns(3)
col1.metric("Total Trades", total_trades)
col2.metric("Win Rate", f"{win_rate}%")
col3.metric("Avg RR", avg_rr)

st.metric("Avg PnL %", f"{avg_pnl_percent}%")

# Equity curve
st.subheader("📈 Equity Curve")

if "Final Balance" in df.columns:
    plt.figure()
    plt.plot(df["Final Balance"])
    plt.xlabel("Trade Number")
    plt.ylabel("Balance ($)")
    plt.title("Account Growth Over Time")
    st.pyplot(plt)
else:
    st.info("Not enough data for equity curve yet.")

# Trades count by setup
st.subheader("🧩 Trades by Setup Type")
if "Setup Type" in df.columns:
    setup_counts = df["Setup Type"].value_counts()
    st.bar_chart(setup_counts)
else:
    st.info("No setup data yet")

st.caption("Metrics improve as more trades are logged ✅")
