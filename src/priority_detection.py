# src/priority_detection.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY_1")
if not API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY_1 in your .env file.")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.3-8b-instruct:free"
PRIORITY_LABELS = ["High", "Medium", "Low"]


def classify_priority(text: str) -> str:
    prompt = f"""
You are an assistant that classifies the importance/urgency of a short email or a thread summary.
Return ONLY one of: High, Medium, Low.

Text:
\"\"\"{text}\"\"\"

Consider deadlines, explicit urgent words (ASAP, urgent), manager instructions, and actionable items.
"""
    headers = {"Authorization": f"Bearer {API_KEY}",
               "Content-Type": "application/json"}
    data = {"model": MODEL, "messages": [
        {"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]}
    r = requests.post(API_URL, headers=headers, json=data)
    if r.status_code != 200:
        raise Exception(f"OpenRouter error: {r.status_code} {r.text}")
    label = r.json()["choices"][0]["message"]["content"].strip()
    if label not in PRIORITY_LABELS:
        return "Medium"
    return label


def classify_thread_priority(thread_summary: str) -> str:
    return classify_priority(thread_summary)


def detect_priority(text: str) -> str:
    return classify_priority(text)
