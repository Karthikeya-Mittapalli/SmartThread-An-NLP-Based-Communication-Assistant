# main.py (at project root)
from src.pre_processing import preprocess_email
from src.thread_manager import add_to_thread, list_threads, update_thread_summary, update_thread_priority
from src.priority_detection import detect_priority
from src.thread_summarization import summarize_thread

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

client = MongoClient(MONGO_URI)
db = client["enron_email"]
emails_col = db["test_mails"]
threads_col = db["threads"]

# imports from src


def process_unread(limit=10):
    # Fetch unread emails (simulate by setting is_unread flag in Mongo)
    cursor = emails_col.find({"is_unread": True}).limit(limit)
    any_found = False
    for email in cursor:
        any_found = True
        eid = email["_id"]
        print(
            f"\nProcessing email _id={eid} subject={email.get('subject') or '...'}")
        processed = preprocess_email(email)
        # store processed fields back to email doc
        emails_col.update_one({"_id": eid}, {"$set": processed})
        # add to thread (returns thread_id)
        tid = add_to_thread(processed, eid)
        print(" -> assigned to thread:", tid)
    if not any_found:
        print("No emails with is_unread=True found. Mark 1-2 test emails as unread or insert sample emails.")


def summarize_and_prioritize(limit=10):
    threads = list_threads(limit=limit)
    for t in threads:
        messages = []
        for m in sorted(t.get("messages", []), key=lambda x: x.get("date") or ""):
            messages.append({
                "sender": (m.get("from") or {}).get("name") or (m.get("from") or {}).get("email"),
                "timestamp": str(m.get("date")),
                "text": m.get("clean_message")
            })
        if not messages:
            continue
        print(
            f"\n--- Summarizing thread: {t.get('subject')} (id={t.get('_id')}) ---")
        try:
            summary = summarize_thread(messages)
        except Exception as e:
            summary = f"Summarization failed: {e}"
        update_thread_summary(t["_id"], summary)
        try:
            priority = detect_priority(summary)
        except Exception as e:
            priority = "Medium"
        update_thread_priority(t["_id"], priority)
        print("Summary:\n", summary)
        print("Priority:", priority)


if __name__ == "__main__":
    print("Starting test pipeline: process unread -> thread -> summarize -> priority")
    process_unread(limit=5)
    summarize_and_prioritize(limit=10)
    print("\nDone.")
