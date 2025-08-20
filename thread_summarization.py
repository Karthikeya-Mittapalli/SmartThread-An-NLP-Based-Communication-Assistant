import os
import requests
from dotenv import load_dotenv

# ========== Setup ==========
# Put your OpenRouter API key in env variable for safety
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY as environment variable.")

API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ========== Summarization Prompt Template ==========


def build_prompt(thread_messages):
    """
    thread_messages: list of dicts, each with sender, role, timestamp, text
    """
    formatted_thread = "\n".join(
        [f"[{m['sender']} | {m['role']} | {m['timestamp']}]\n{m['text']}\n"
         for m in thread_messages]
    )

    prompt = f"""
        You are an assistant that summarizes conversation threads.
        Read the following thread and generate a clear, concise summary.

        Your summary should include:
        1. Decisions Made
        2. Action Items
        3. Deadlines / Timeframes
        4. Urgency Level (High/Medium/Low)
        5. Open Questions / Pending Issues

        Thread:
        <<<
        {formatted_thread}
        >>>

        Output Format (Natural Language):
        Summary:
        - Decisions: ...
        - Action Items: ...
        - Deadlines: ...
        - Urgency: ...
        - Open Issues: ...
"""
    return prompt


# ========== Function to Call OpenRouter ==========
def summarize_thread(thread_messages, model="deepseek/deepseek-r1-0528-qwen3-8b:free"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": build_prompt(thread_messages)}
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"OpenRouter API Error: {response.text}")

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


# ========== Example Run ==========
if __name__ == "__main__":
    sample_thread = [
        {"sender": "Bob", "role": "Engineer", "timestamp": "2025-08-19 09:12",
         "text": "I’ve updated the Q3 report draft. Charlie, can you add sales numbers?"},
        {"sender": "Charlie", "role": "Analyst", "timestamp": "2025-08-19 09:30",
         "text": "Sure, I’ll add sales data by 2 PM."},
        {"sender": "Alice", "role": "Manager", "timestamp": "2025-08-19 09:45",
         "text": "Great. Let’s finalize the full report today. Please send me the completed version by 5 PM."}
    ]

    summary = summarize_thread(sample_thread)
    print("\nThread Summary:\n", summary)
