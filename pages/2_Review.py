# pages/2_Review.py
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Velor Review", page_icon="📝", layout="centered")

SECRETS_KEY = "gcp_service_account"
SHEET_NAME = "Velor_Tading_Journal"

# Auth
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets[SECRETS_KEY], scopes=scope)
gc = gspread.authorize(creds)
sheet = gc.open(SHEET_NAME).sheet1

data = sheet.get_all_values()
if len(data) < 2:
    st.info("No trades to review yet.")
    st.stop()

df = pd.DataFrame(data[1:], columns=data[0])
df.columns = [c.strip() for c in df.columns]

# basic filters
st.title("📝 Trade Review — Velor Journal")
st.caption("Filter and inspect trades. Tap a row to see details.")

cols = st.columns(3)
date_from = st.date_input("From", value=pd.to_datetime(df.iloc[0,0]).date())
date_to = st.date_input("To", value=pd.to_datetime(df.iloc[-1,0]).date())
pair_filter = st.text_input("Pair (leave blank = all)")
setup_filter = st.text_input("Setup (leave blank = all)")
result_filter = st.selectbox("Result", ["All", "Win", "Loss", "Break Even"])

# apply filters safely
df["_Timestamp"] = df.iloc[:,0]  # assume first column is timestamp/date
try:
    df["_DateOnly"] = pd.to_datetime(df["_Timestamp"], errors="coerce").dt.date
except Exception:
    df["_DateOnly"] = df["_Timestamp"]

mask = (df["_DateOnly"] >= date_from) & (df["_DateOnly"] <= date_to)
if pair_filter:
    mask &= df.apply(lambda r: pair_filter.lower() in str(r.values).lower(), axis=1)
if setup_filter:
    mask &= df.apply(lambda r: setup_filter.lower() in str(r.values).lower(), axis=1)
if result_filter != "All":
    # find a column with 'Result' in name
    result_col = None
    for c in df.columns:
        if c.lower() == "result":
            result_col = c
            break
    if result_col:
        mask &= (df[result_col] == result_filter)

dff = df[mask].reset_index(drop=True)

st.write(f"Showing {len(dff)} trades")

# show compact list view
for idx, row in dff.iterrows():
    # main line
    pair = row.get("Instrument (Pair)", row.get("Pair", row.get("Pair ", "")))
    result = row.get("Result", "")
    rr = row.get("R:R Ratio", row.get("RR", ""))
    session = row.get("Trading Session", row.get("Trading_Session", ""))
    emotion = row.get("Emotional State Before", row.get("Emotion Before", ""))

    left = f"**{pair}**  |  {session}  |  {result}  |  RR: {rr}"
    st.markdown(left)

    # expand detail
    if st.button(f"View details {idx}", key=f"view_{idx}"):
        st.write(row.to_frame().T)
        st.markdown("---")
