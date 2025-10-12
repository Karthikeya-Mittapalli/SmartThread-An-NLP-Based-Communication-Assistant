# src/thread_summarization.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY_1")

if not API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY_1 in your .env file.")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
# choose a free OpenRouter-hosted model you tested
DEFAULT_MODEL = "deepseek/deepseek-r1-0528-qwen3-8b:free"  # change if needed


def build_prompt(thread_messages):
    formatted = []
    for m in thread_messages:
        sender = m.get("sender") or m.get("from", "")
        ts = m.get("timestamp") or m.get("date", "")
        text = m.get("text") or m.get("clean_message", "")
        formatted.append(f"[{sender} | {ts}]\n{text}\n")
    formatted_thread = "\n".join(formatted)

    prompt = f"""
You are an assistant that summarizes email conversation threads.
Read the following thread and generate a clear concise summary suitable for a busy professional.

Include:
1) Decisions / conclusions
2) Action items with assignee if mentioned
3) Deadlines & timeframes
4) Overall urgency (High/Medium/Low)
5) Open questions

Thread:
<<<
{formatted_thread}
>>>

Output in this exact natural-language format:

Summary:
- Decisions: ...
- Action Items: ...
- Deadlines: ...
- Urgency: ...
- Open Questions: ...
"""
    return prompt


def summarize_thread(thread_messages, model=DEFAULT_MODEL):
    headers = {"Authorization": f"Bearer {API_KEY}",
               "Content-Type": "application/json"}

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant specialized in summarization."},
            {"role": "user", "content": build_prompt(thread_messages)}
        ],
        "max_tokens": 512,
        "temperature": 0.0
    }

    r = requests.post(API_URL, headers=headers, json=data)
    if r.status_code != 200:
        raise Exception(f"OpenRouter error: {r.status_code} {r.text}")
    resp = r.json()
    return resp["choices"][0]["message"]["content"].strip()
