import os
import requests # type: ignore
import json
import time
from dotenv import load_dotenv # type: ignore

from src.key_manager import key_manager
from src.priority_detection_flask import detect_priority

# Load environment variables
load_dotenv()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemma-2-9b-it:free"


def analyze_email(text: str) -> dict:
    """
    Perform email analysis combining:
    1. LLM-based summarization
    2. NLP-based manual priority detection
    """
    # ---- Step 1: Summarize using LLM ----
    summary = summarize_email(text)

    # ---- Step 2: Manual Priority Detection (NER + Rules) ----
    priority = detect_priority(text)

    # ---- Step 3: Return unified output ----
    return {
        "summary": summary,
        "priority": priority["priority"],
        "entities": priority["entities"]
    }


def summarize_email(text: str) -> str:
    """
    Generate a short summary using LLM (Gemma or other model).
    Fallback gracefully if API fails.
    """
    headers = {
        "Authorization": f"Bearer {key_manager.get_key()}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an assistant that summarizes emails clearly and concisely."},
            {"role": "user", "content": f"Summarize this email in 2 sentences:\n\n{text}"}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Summarization failed: {e}")
        return "Summary unavailable due to API error."
