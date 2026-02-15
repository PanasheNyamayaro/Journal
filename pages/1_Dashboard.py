# pages/1_Dashboard.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

st.html("""
    <style>
        img[alt="Logo"] {
            height:6rem !important;
        }
    </style>
""")


st.logo("logo.png")


st.set_page_config(page_title="Velor Dashboard", page_icon="📊", layout="centered")

SECRETS_KEY = "gcp_service_account"
SHEET_NAME = "Velor_Tading_Journal"

# Auth
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets[SECRETS_KEY], scopes=scope)
gc = gspread.authorize(creds)
sheet = gc.open(SHEET_NAME).sheet1

# Load data
data = sheet.get_all_values()
if len(data) < 2:
    st.info("No trades yet. Log your first trade from the main page.")
    st.stop()

df = pd.DataFrame(data[1:], columns=data[0])

# Normalise column names (strip)
df.columns = [c.strip() for c in df.columns]

# Convert numeric columns safely
def safe_numeric(col):
    if col in df.columns:
        return pd.to_numeric(df[col].replace("", pd.NA), errors="coerce")
    return pd.Series(dtype="float64")

# Common names used by app.py
pnl_col = None
rr_col = None
final_balance_col = None
result_col = None
setup_col = None
session_col = None
pips_col = None
timestamp_col = None

# attempt to find matching columns
candidates = {c.lower(): c for c in df.columns}
for key in ["pnl_usd", "pnl_usd", "pnl_usd", "pnl_usd"]:
    if key in candidates: pnl_col = candidates[key]
for key in ["rr", "r:r", "r_r"]:
    if key in candidates and rr_col is None: rr_col = candidates[key]
for key in ["final balance", "final_balance", "finalbalance"]:
    if key in candidates and final_balance_col is None: final_balance_col = candidates[key]
for key in ["result", "Result"]:
    if key in df.columns and result_col is None: result_col = key
for key in ["setup type", "setup_type", "main setup", "setup"]:
    for k in [key]:
        if k in candidates and setup_col is None: setup_col = candidates[k]
for key in ["trading session", "session"]:
    if key in candidates and session_col is None: session_col = candidates[key]
for key in ["pnl_pips", "pips", "pips_made", "pnl_pips"]:
    if key in candidates and pips_col is None: pips_col = candidates[key]
for key in ["timestamp", "date & time", "date"]:
    if key in candidates and timestamp_col is None: timestamp_col = candidates[key]

# Safe numeric conversions
if pnl_col:
    df["__pnl_usd"] = safe_numeric(pnl_col)
else:
    # try other common names
    for alt in ["PnL_USD", "Pnl_USD", "PnL"]:
        if alt in df.columns:
            df["__pnl_usd"] = safe_numeric(alt)
            pnl_col = alt
            break

if rr_col:
    df["__rr"] = safe_numeric(rr_col)
else:
    df["__rr"] = pd.to_numeric(df.get("RR", pd.Series()), errors="coerce")

if final_balance_col:
    df["__final_balance"] = safe_numeric(final_balance_col)
else:
    df["__final_balance"] = pd.to_numeric(df.get("Final Balance", pd.Series()), errors="coerce")

# Results & counts
total_trades = len(df)
wins = len(df[df[result_col] == "Win"]) if result_col in df.columns else len(df[df.iloc[:,0].notna()])  # fallback
losses = len(df[df[result_col] == "Loss"]) if result_col in df.columns else 0
win_rate = round((wins / total_trades) * 100, 2) if total_trades > 0 else 0
avg_rr = round(df["__rr"].mean(skipna=True), 2) if "__rr" in df.columns else 0
avg_pnl = round(df["__pnl_usd"].mean(skipna=True), 2) if "__pnl_usd" in df.columns else 0

# Header Metrics
st.title("📊 Velor Dashboard")
st.caption("Live metrics from your Velor Journal sheet")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Trades", total_trades)
c2.metric("Win Rate", f"{win_rate}%")
c3.metric("Avg RR", avg_rr)
c4.metric("Avg PnL ($)", avg_pnl)

# Equity Curve
st.subheader("Equity Curve")
if "__final_balance" in df.columns and df["__final_balance"].notna().any():
    fig, ax = plt.subplots()
    ax.plot(df["__final_balance"].fillna(method="ffill").astype(float).reset_index(drop=True))
    ax.set_xlabel("Trade #")
    ax.set_ylabel("Balance ($)")
    st.pyplot(fig)
else:
    st.info("Final balance not available yet. It will appear after trades are logged.")

# Setup Performance
st.subheader("Setup Performance")
if setup_col and setup_col in df.columns:
    group = df.groupby(setup_col).agg(
        Trades=(setup_col, "count"),
        WinCount=(result_col, lambda s: (s == "Win").sum() if result_col in df.columns else 0),
        AvgRR=("__rr", "mean"),
        NetProfit=("__pnl_usd", "sum")
    ).reset_index()
    group["WinRate"] = (group["WinCount"] / group["Trades"] * 100).round(2)
    st.dataframe(group.sort_values("NetProfit", ascending=False).reset_index(drop=True))
    st.bar_chart(group.set_index(setup_col)["NetProfit"])
else:
    st.info("Setup Type column not found. Add Setup Type to your sheet to see breakdowns.")

# Session Performance
st.subheader("Session Performance")
if session_col and session_col in df.columns:
    sess = df.groupby(session_col).agg(Trades=(session_col,"count"), NetProfit=("__pnl_usd","sum"))
    st.dataframe(sess)
    st.bar_chart(sess["NetProfit"])
else:
    st.info("Trading Session column missing.")

# Top insights
st.subheader("Quick Insights")
insights = []
if total_trades >= 5:
    best_setup = group.sort_values("NetProfit", ascending=False).iloc[0][setup_col] if 'group' in locals() and not group.empty else None
    if best_setup:
        insights.append(f"Best setup so far: {best_setup}")
    worst = group.sort_values("NetProfit", ascending=True).iloc[0][setup_col] if 'group' in locals() and not group.empty else None
    if worst:
        insights.append(f"Worst setup: {worst}")
    if avg_rr and avg_rr > 1.5:
        insights.append("Good average R:R — keep position sizing disciplined.")
else:
    insights.append("Log at least 5 trades to get meaningful insights.")
for i in insights:
    st.write("- " + i)
