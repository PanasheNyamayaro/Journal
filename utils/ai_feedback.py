# ai_feedback.py
import os
import requests
import streamlit as st

MODEL = "meta-llama/Llama-3.2-1B-Instruct"
HF_API_TOKEN = st.secrets["huggingface"]

API_URL = f"https://router.huggingface.co/models/{MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

def generate_ai_feedback(trade_data: dict) -> str:
    """
    trade_data: dictionary of one trade
    returns: AI feedback text
    """

    prompt = f"""
You are a professional trading coach.

Analyze this trade and give short, direct feedback.
Focus on:
- Risk management
- Execution quality
- Emotional discipline
- One improvement action

Trade details:
{trade_data}

Respond in under 120 words.
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.4,
            "max_new_tokens": 200
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
    resc = response.status_code
    st.write(resc)
    if response.status_code != 200:
        return "AI feedback unavailable."

    result = response.json()

    return result[0]["generated_text"].strip()
