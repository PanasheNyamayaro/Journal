# ai_feedback.py
from huggingface_hub import InferenceClient
import streamlit as st

# 1. Access secret
HF_API_TOKEn = st.secrets["huggingface"]["HF_API_TOKEN"]

# 2. Setup Client (No URL needed!)
client = InferenceClient(api_key=HF_API_TOKEn)

def generate_ai_feedback(trade_data: dict) -> str:
    prompt = f"You are a professional forex trader analyse this trade and give feedback in less than 60 words: {trade_data}"
    
    try:
        # 3. Simple call that works exactly like Colab
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Connection Error: {e}"
