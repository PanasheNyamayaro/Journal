# ai_feedback.py

import os
import requests

MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}


def build_prompt(trade_data: dict) -> str:
    """
    Converts trade data into a structured prompt
    """

    return f"""
You are a professional trading psychologist and performance coach.

Analyze the following trade and give:
1. Discipline feedback
2. Risk management feedback
3. One clear improvement rule

Trade data:
Instrument: {trade_data.get("instrument")}
Direction: {trade_data.get("direction")}
Risk %: {trade_data.get("risk_percent")}
RR: {trade_data.get("rr")}
Followed Plan: {trade_data.get("followed_plan")}
Emotion Before: {trade_data.get("emotion_before")}
Emotion After: {trade_data.get("emotion_after")}
Result: {trade_data.get("result")}
PnL %: {trade_data.get("pnl_percent")}

Be concise. No fluff.
"""


def get_ai_feedback(trade_data: dict) -> str:
    prompt = build_prompt(trade_data)

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 250,
            "temperature": 0.4,
            "top_p": 0.9,
            "do_sample": True
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    result = response.json()

    # HuggingFace returns a list
    return result[0]["generated_text"].replace(prompt, "").strip()


# -------------------------------
# Test run
# -------------------------------
if __name__ == "__main__":
    sample_trade = {
        "instrument": "EURUSD",
        "direction": "Buy",
        "risk_percent": 2,
        "rr": 3,
        "followed_plan": "Yes",
        "emotion_before": "Calm",
        "emotion_after": "Confident",
        "result": "Win",
        "pnl_percent": 6
    }

    feedback = get_ai_feedback(sample_trade)
    print("\nAI FEEDBACK:\n")
    print(feedback)

