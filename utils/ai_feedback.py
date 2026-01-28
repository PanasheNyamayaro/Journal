# ai_feedback.py
import os
import requests
import streamlit as st

MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
HF_API_TOKEN = st.secrets["huggingface"]["HF_API_TOKEN"]

API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

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
