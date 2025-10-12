# src/thread_manager.py
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["enron_email"]
emails_col = db["mails"]
threads_col = db["threads"]


def _participants_from_processed(proc):
    parts = set()
    if proc.get("from", {}).get("email"):
        parts.add(proc["from"]["email"])
    for p in proc.get("to", []) + proc.get("cc", []) + proc.get("bcc", []):
        if p.get("email"):
            parts.add(p["email"])
    return parts


def find_thread_by_in_reply(in_reply_to):
    if not in_reply_to:
        return None
    # try exact match in thread messages
    return threads_col.find_one({"messages.message_id": in_reply_to})


def find_thread_by_references(references):
    if not references:
        return None
    return threads_col.find_one({"messages.message_id": {"$in": references}})


def find_thread_by_subject_and_participants(subject_norm, participants):
    if not subject_norm:
        return None
    candidates = threads_col.find({"subject_norm": subject_norm})
    for t in candidates:
        # gather participants in thread
        thread_parts = set()
        for m in t.get("messages", []):
            # m['from'] might be dict
            f = m.get("from", {})
            if f and f.get("email"):
                thread_parts.add(f["email"])
            for r in m.get("to", []):
                if r.get("email"):
                    thread_parts.add(r["email"])
        if participants & thread_parts:
            return t
    return None


def add_to_thread(processed_email: dict, email_id):
    """
    processed_email: result of preprocess_email()
    email_id: the original _id or a generated id (string/ObjectId)
    """
    message_id = processed_email.get("message_id")
    in_reply_to = processed_email.get("in_reply_to")
    references = processed_email.get("references", [])
    subj_norm = processed_email.get("normalized_subject", "")
    participants = _participants_from_processed(processed_email)

    # 1. Try in_reply_to
    thread = find_thread_by_in_reply(in_reply_to) if in_reply_to else None

    # 2. Try references
    if not thread and references:
        thread = find_thread_by_references(references)

    # 3. Fallback to subject + participants overlap
    if not thread and subj_norm:
        thread = find_thread_by_subject_and_participants(
            subj_norm, participants)

    # 4. Insert or update
    message_obj = {
        "email_id": str(email_id),
        "message_id": message_id,
        "from": processed_email.get("from"),
        "to": processed_email.get("to"),
        "cc": processed_email.get("cc"),
        "date": processed_email.get("date"),
        "clean_message": processed_email.get("clean_message")
    }

    if thread:
        threads_col.update_one(
            {"_id": thread["_id"]},
            {"$push": {"messages": message_obj}, "$set": {
                "last_updated": datetime.now()}}
        )
        return thread["_id"]
    else:
        new_thread = {
            "subject": processed_email.get("subject", ""),
            "subject_norm": subj_norm,
            "created_at": datetime.now(),
            "last_updated": datetime.now(),
            "messages": [message_obj],
            "summary": None,
            "priority": None
        }
        res = threads_col.insert_one(new_thread)
        return res.inserted_id


def get_thread_by_message_id(message_id):
    return threads_col.find_one({"messages.message_id": message_id})


def list_threads(limit=10):
    return list(threads_col.find().sort("last_updated", -1).limit(limit))


def update_thread_summary(thread_id, summary_text):
    threads_col.update_one({"_id": ObjectId(thread_id)}, {
                           "$set": {"summary": summary_text, "last_updated": datetime.now()}})


def update_thread_priority(thread_id, priority_level):
    threads_col.update_one({"_id": ObjectId(thread_id)}, {
                           "$set": {"priority": priority_level, "last_updated": datetime.now()}})
