# src/thread_summarization.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY_1")
if not API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY_1 in your .env file.")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-r1-0528-qwen3-8b:free"

def build_prompt(thread_messages):
    formatted = []
    for m in thread_messages:
        sender = m.get("from", "")
        ts = m.get("timestamp", "")
        text = m.get("text", "")
        formatted.append(f"[{sender} | {ts}]\n{text}\n")
    formatted_thread = "\n".join(formatted)

    prompt = f"""
You are an assistant that summarizes email conversation threads.
Generate a clear, concise summary for a busy professional.

Include:
- Decisions / conclusions
- Action items
- Deadlines & timeframes
- Overall urgency (High/Medium/Low)
- Open questions

Thread:
<<<
{formatted_thread}
>>>

Output as plain text summary.
"""
    return prompt

def summarize_thread(thread_messages, model=DEFAULT_MODEL) -> str:
    """Generates a summary for a list of thread messages."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant specialized in summarization."},
            {"role": "user", "content": build_prompt(thread_messages)}
        ],
        "temperature": 0.0,
        "max_tokens": 512
    }

    try:
        r = requests.post(API_URL, headers=headers, json=data, timeout=20)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[ThreadSummarization] API error: {e}")
        # fallback: just concatenate messages
        return " ".join([m.get("text", "") for m in thread_messages])
