import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

# ================== CONFIG ==================
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY_1")
if not API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY in your .env file.")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-3.3-8b-instruct:free"
PRIORITY_LABELS = ["High", "Medium", "Low"]

# ================== MONGODB ==================
client = MongoClient("mongodb://localhost:27017/")
db = client["enron_email"]
emails_col = db["mails"]

# ================== OPENROUTER PRIORITY DETECTION ==================
def classify_priority(email_text: str) -> str:
    """
    Uses OpenRouter LLaMA 3.3-8B model to classify email priority.
    """
    prompt = f"""
You are an assistant that classifies emails into High, Medium, or Low priority.

Email:
\"\"\"
{email_text}
\"\"\"

Consider urgency, deadlines, action items, and importance.
Return ONLY one label: High, Medium, or Low.
"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"OpenRouter API Error: {response.text}")

    label = response.json()["choices"][0]["message"]["content"].strip()
    if label not in PRIORITY_LABELS:
        return "Medium"  # fallback
    return label

# ================== PROCESS SINGLE EMAIL ==================
def process_email_by_id(email_id: str):
    email_doc = emails_col.find_one({"_id": ObjectId(email_id)})
    if not email_doc:
        print(f"Email {email_id} not found.")
        return
    clean_message = email_doc.get("clean_message", "")
    if not clean_message:
        print(f"Email {email_id} has no clean_message field.")
        return
    priority = classify_priority(clean_message)
    emails_col.update_one({"_id": email_doc["_id"]}, {"$set": {"priority": priority}})
    print(f"✅ Email {email_id} processed with priority: {priority}")

# ================== EXAMPLE RUN ==================
if __name__ == "__main__":
    # Replace with an actual email ObjectId from your MongoDB
    sample_email_id = "6892fe052589ce0138d7759f"
    process_email_by_id(sample_email_id)
