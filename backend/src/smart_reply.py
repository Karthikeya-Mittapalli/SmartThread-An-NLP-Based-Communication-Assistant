import os
import requests
import json
import time
from dotenv import load_dotenv

from src.key_manager import key_manager

# --- Load environment variables ---
load_dotenv()

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemma-2-9b-it:free"  # same as analyze_email()

def suggest_reply(summary_data_or_text, model=MODEL):
    """
    Generates a smart email reply based on either:
    - a dict containing summary info (Decisions, Action Items, etc.)
    - OR a plain message body string (if summary not available).
    """

    # --- Determine if we got structured summary data or raw text ---
    if isinstance(summary_data_or_text, dict):
        summary_data = summary_data_or_text
        prompt = f"""
        You are a helpful email assistant tasked with writing concise, professional replies
        based on summarized conversation data.

        Summary Information:
        - Decisions: {summary_data.get("Decisions", "None")}
        - Action Items: {summary_data.get("Action Items", "None")}
        - Deadlines: {summary_data.get("Deadlines", "None")}
        - Urgency: {summary_data.get("Urgency", "None")}
        - Open Issues: {summary_data.get("Open Issues", "None")}

        Write a short, professional reply (2–4 sentences) that:
        1. Acknowledges any decisions made,
        2. Confirms understanding of action items,
        3. Optionally states the next step or expresses readiness to proceed.

        Return ONLY the reply text (no JSON, no extra formatting).
        """
    else:
        message_body = summary_data_or_text
        prompt = f"""
        You are a helpful email assistant that writes short, context-aware replies.

        Below is the email text. Generate a concise, professional reply (2–4 sentences)
        that acknowledges the message, addresses any key points, and maintains a polite tone.

        Email:
        ---
        {message_body}
        ---
        Return ONLY the reply text (no JSON or markdown).
        """

    # --- Build headers and request payload ---
    current_api_key = key_manager.get_key()
    headers = {
        "Authorization": f"Bearer {current_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "SmartMail Backend"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,  # slightly creative for natural tone
    }

    # --- Exponential Backoff Logic ---
    max_retries = 4
    for attempt in range(max_retries):
        try:
            r = requests.post(API_URL, headers=headers, json=data, timeout=20)
            r.raise_for_status()

            response_text = r.json()["choices"][0]["message"]["content"].strip()
            if response_text:
                return response_text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                delay = 2 ** attempt
                print(f"[SuggestReply] Rate limit exceeded. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"[SuggestReply] HTTP Error: {e}")
                break
        except Exception as e:
            print(f"[SuggestReply] Unexpected error: {e}")
            break

    # --- Fallback reply if model fails ---
    return "Thanks for the update! I’ve noted your points and will follow up shortly."

