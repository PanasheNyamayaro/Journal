# ai_feedback.py
import os
import requests
import streamlit as st

MODEL = "Qwen/Qwen2.5-7B-Instruct"
HF_API_TOKEN = st.secrets["huggingface"]

API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

def generate_ai_feedback(trade_data: dict) -> str:
    # ... (Keep your prompt logic here)

    # NEW: Chat-style payload
    payload = {
        "model": MODEL, # Move model name inside the payload
        "messages": [
            {"role": "system", "content": "You are a professional trading coach."},
            {"role": "user", "content": f"Analyze this trade data: {trade_data}"}
        ],
        "max_tokens": 200,
        "temperature": 0.4
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
    
    if response.status_code != 200:
        return f"Error {response.status_code}: {response.text}"

    # NEW: Nested response structure
    result = response.json()
    return result["choices"][0]["message"]["content"].strip()
