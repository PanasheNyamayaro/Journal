# app.py  — Velor Trading Journal v2 (Beginner-first)
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import pandas as pd
import math

st.set_page_config(page_title="Velor Journal", page_icon="📒", layout="centered")

# ---------- CONFIG ----------
SHEET_NAME = "Velor_Tading_Journal"   # exact sheet title
DRIVE_FOLDER_NAME = "Screenshot"       # exact drive folder name
SECRETS_KEY = "gcp_service_account"    # your Streamlit secret key name

# ---------- AUTH ----------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_info(st.secrets[SECRETS_KEY], scopes=scope)
gc = gspread.authorize(creds)
drive_service = build("drive", "v3", credentials=creds)

# ---------- Helpers ----------
def open_sheet():
    sh = gc.open(SHEET_NAME)
    return sh.sheet1

def find_drive_folder_id(folder_name):
    q = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    res = drive_service.files().list(q=q, spaces='drive', fields='files(id, name)').execute()
    files = res.get('files', [])
    if files:
        return files[0]['id']
    return None

def upload_file_to_drive(folder_id, file_buffer, filename, mime_type):
    media = MediaIoBaseUpload(file_buffer, mimetype=mime_type, resumable=True)
    file_metadata = {"name": filename, "parents": [folder_id]}
    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
    return file.get("webViewLink")

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
    try:
        if "JPY" in pair.upper():
            multiplier = 100
        else:
            multiplier = 10000
        return round((value2 - value1) * multiplier, 1)
    except Exception:
        return 0

def calc_pnl_usd(pips, lot_size):
    # simple approximation: 1 pip = $0.10 per 0.01 lot for many FX pairs
    # We use: pip_value_per_lot = 1 for convenience -> user sees approximate results
    # Adjust later to currency specifics if needed
    try:
        return round(pips * lot_size * 0.1, 2)
    except Exception:
        return 0.0

# ---------- UI ----------
st.title("📒 Velor Trading Journal — Log Trade (Beginner Mode)")
st.caption("Fast logging. Toggle Advanced for more fields. Screenshot optional.")

sheet = open_sheet()
folder_id = find_drive_folder_id(DRIVE_FOLDER_NAME)
if folder_id is None:
    st.warning(f"Drive folder '{DRIVE_FOLDER_NAME}' not found. Uploads will be disabled until folder exists and is shared with service account.")

# layout grouped cards (single page grouped)
with st.form("trade_form", clear_on_submit=False):
    st.subheader("Trade Basics")
    cols = st.columns(2)
    pair = cols[0].text_input("Pair (e.g. EURUSD)", value="EURUSD").upper()
    direction = cols[1].selectbox("Direction", ["Buy", "Sell"])
    entry_price = st.number_input("Entry Price", format="%.5f", value=0.0)
    stop_loss = st.number_input("Stop Loss Price", format="%.5f", value=0.0)
    take_profit = st.number_input("Take Profit Price", format="%.5f", value=0.0)

    st.subheader("Risk & Session")
    cols = st.columns(3)
    account_balance = cols[0].number_input("Account Balance ($)", value=1000.0, format="%.2f")
    risk_percent = cols[1].number_input("Risk %", min_value=0.1, max_value=100.0, value=1.0, step=0.1, format="%.2f")
    session = cols[2].selectbox("Trading Session", ["Asia", "London", "New York", "Sydney"])

    if risk_percent > 5.0:
        st.warning("Warning: Risk > 5% — consider lowering position size.")

    st.subheader("Psychology (Quick)")
    cols = st.columns(2)
    emotion_before = cols[0].selectbox("Emotion Before", ["Calm", "Confident", "Nervous", "Rushed", "Bored", "Greedy", "Revenge"])
    quick_note = cols[1].text_input("Quick Note (optional)")

    st.subheader("Exit Method")
    exit_mode = st.radio("Exit Method", ["Auto (Win/Loss/BE)", "Manual Exit Price", "Custom: Partial/Trailing"], index=0)

    if exit_mode == "Auto (Win/Loss/BE)":
        result = st.selectbox("Result", ["Win", "Loss", "Break Even"])
        exit_price_manual = None
    elif exit_mode == "Manual Exit Price":
        exit_price_manual = st.number_input("Manual Exit Price", format="%.5f", value=0.0)
        result = st.selectbox("Result (optional)", ["Win", "Loss", "Break Even"])
    else:
        exit_price_manual = st.number_input("Custom Exit Price (use for partials/trailing)", format="%.5f", value=0.0)
        result = st.selectbox("Result (optional)", ["Win", "Loss", "Break Even"])

    st.subheader("Optional")
    screenshot_file = st.file_uploader("Screenshot (optional)", type=["png", "jpg", "jpeg"])
    show_advanced = st.checkbox("Show Advanced Fields (optional)")

    if show_advanced:
        st.subheader("Advanced (optional)")
        setup_type = st.selectbox("Setup Type", ["Breakout", "Trend Continuation", "Reversal", "News Trade", "Other"])
        market_condition = st.selectbox("Market Condition", ["Trending", "Ranging", "High Volatility", "News-driven", "Other"])
        indicators_used = st.text_input("Indicators Used (comma separated)")
        execution_score = st.slider("Execution Score (1-5)", 1, 5, 3)
    else:
        setup_type = "Other"
        market_condition = ""
        indicators_used = ""
        execution_score = ""

    submitted = st.form_submit_button("✅ Save Trade")

# ---------- On submit ----------
if submitted:
    timestamp = datetime.utcnow().isoformat()
    # determine exit price
    if exit_mode == "Auto (Win/Loss/BE)":
        if result == "Win":
            exit_price = take_profit if take_profit and take_profit > 0 else entry_price
        elif result == "Loss":
            exit_price = stop_loss if stop_loss and stop_loss > 0 else entry_price
        else:
            exit_price = entry_price
    else:
        exit_price = exit_price_manual if exit_price_manual and exit_price_manual > 0 else entry_price

    # pips & rr & pnl calculations
    pips_made = calc_pips(entry_price, exit_price, pair)
    rr = calc_rr(entry_price, stop_loss, take_profit, direction)
    pnl_usd = calc_pnl_usd(pips_made, 1.0)  # default lot multiplier; adjust later
    pnl_percent = round((pnl_usd / account_balance) * 100, 2) if account_balance else 0.0
    final_balance = round(account_balance + pnl_usd, 2)

    # position size approx (simple)
    try:
        pos_size = round((account_balance * (risk_percent / 100.0)) / abs(entry_price - stop_loss), 4) if stop_loss and entry_price != stop_loss else 0
    except Exception:
        pos_size = 0

    # upload screenshot if provided
    screenshot_link = ""
    if screenshot_file is not None and folder_id is not None:
        buf = io.BytesIO(screenshot_file.read())
        fname = f"{pair}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{screenshot_file.name}"
        try:
            link = upload_file_to_drive(folder_id, buf, fname, screenshot_file.type)
            screenshot_link = link
        except Exception as e:
            st.warning("Screenshot upload failed: " + str(e))

    # build row in the agreed column order — match your sheet exactly
    row = [
        timestamp,            # Date & Time (Timestamp)
        pair,                 # Instrument (Pair)
        direction,            # Direction
        entry_price,          # Entry Price
        "Scalp/Day/Swing",    # Trade Type (placeholder)
        account_balance,      # Account Size
        risk_percent,         # Risk %
        round(account_balance * (risk_percent / 100.0), 2),  # Risk Amount ($)
        stop_loss,            # Stop Loss Price
        take_profit,          # Take Profit Price
        pos_size,             # Position Size (Lots)
        rr if rr is not None else "",    # R:R Ratio
        setup_type,           # Main Setup
        indicators_used,      # Indicators Used
        market_condition,     # Market Structure / Condition
        "",                   # Confirmation signals (free text)
        "",                   # News Driver
        "",                   # Expected Impact
        "",                   # Market Sentiment
        "",                   # Relevant Data Source
        "",                   # Time of next news
        emotion_before,       # Emotional State Before
        "",                   # Emotional State During (left blank)
        "",                   # Was trade impulsive? (Y/N)
        "",                   # Did you follow plan? (Y/N)
        execution_score,      # Discipline / Execution Score
        result,               # Result
        pnl_usd,              # PnL_USD
        pnl_percent,          # PnL_Percent
        final_balance,        # Final Balance
        pips_made,            # PnL_Pips
        quick_note,           # Notes
        screenshot_link,      # Screenshot (URL)
        "Feedback coming soon"  # AI_Feedback placeholder
    ]

    try:
        sheet.append_row(row)
        st.success("✅ Trade saved to Google Sheets")
    except Exception as e:
        st.error("Failed to write to sheet: " + str(e))

    # reset some fields (keep account balance for convenience)
    if 'pair' in locals():
        st.rerun()
