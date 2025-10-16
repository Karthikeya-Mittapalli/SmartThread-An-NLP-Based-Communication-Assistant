import os
import requests
import json
import time
from dotenv import load_dotenv

from src.key_manager import key_manager

API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Using a model that is good at following JSON format instructions
MODEL = "google/gemma-2-9b-it:free" 
PRIORITY_LABELS = ["High", "Medium", "Low"]

def analyze_email(text: str) -> dict:
    """
    Summarizes, classifies, and structures an email in one API call.
    Returns a JSON dict like:
    {
    "summary": "...",
    "priority": "High",
    "Decisions": "...",
    "Action Items": "...",
    "Deadlines": "...",
    "Urgency": "...",
    "Open Issues": "..."
    }
    """
    prompt = f"""
    You are an expert business email analyst. Analyze the email text below
    and output a structured JSON object summarizing its key aspects.

    Tasks:
    1. Summarize the email in one concise sentence for a busy professional.
    2. Determine the overall priority (High, Medium, or Low).
    3. Identify and extract the following (write "None" if not applicable):
       - Decisions made
       - Action Items
       - Deadlines
       - Urgency
       - Open Issues or pending clarifications

    Format your reply as **only** a JSON object, no explanations.

    Example Format:
    {{
      "summary": "The client requests final approval on the Q3 marketing proposal by Friday.",
      "priority": "High",
      "Decisions": "Proceed with final review of proposal.",
      "Action Items": "John to prepare final draft; Sarah to schedule review meeting.",
      "Deadlines": "Friday, 5 PM",
      "Urgency": "High",
      "Open Issues": "Need feedback from finance team."
    }}

    Email Text:
    ---
    {text}
    ---
    """
    current_api_key = key_manager.get_key()

    headers = {
        "Authorization": f"Bearer {current_api_key}",
        "Content-Type": "application/json",
        # This header encourages the model to return JSON
        "HTTP-Referer": "http://localhost:3000", 
        "X-Title": "SmartMail Backend"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        # Some models support a dedicated JSON response format
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
    }

    # --- Exponential Backoff Logic ---
    max_retries = 4
    for attempt in range(max_retries):
        try:
            r = requests.post(API_URL, headers=headers, json=data, timeout=20)
            r.raise_for_status()

            response_text = r.json()["choices"][0]["message"]["content"].strip()
            
            # Parse the JSON response
            result = json.loads(response_text)

            # Validate the response
            summary = result.get("summary")
            priority = result.get("priority")

            if isinstance(summary, str) and priority in PRIORITY_LABELS:
                return result # Success!
            else:
                print(f"[EmailAnalyzer] Invalid JSON content: {result}")
                # Fall through to return default

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                delay = (2 ** attempt)
                print(f"[EmailAnalyzer] Rate limit exceeded. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"[EmailAnalyzer] HTTP Error: {e}")
                break # Break on other HTTP errors or last retry
        except json.JSONDecodeError:
            print(f"[EmailAnalyzer] Failed to decode JSON from response: {response_text}")
            # The model didn't return valid JSON, break and return default
            break
        except Exception as e:
            print(f"[EmailAnalyzer] An unexpected error occurred: {e}")
            break

    # --- Fallback if all retries or parsing fail ---
    return {
        "summary": text[:150] + "..." if len(text) > 150 else text, # Simple truncate for summary
        "priority": "Medium"
    }