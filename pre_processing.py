import re
from pymongo import MongoClient
from bson import ObjectId

# --- MongoDB Connection ---
client = MongoClient("mongodb://localhost:27017/")
db = client["enron_email"]        # replace with your DB name
emails_col = db["mails"]      # replace with your collection name

def clean_email(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # --- Remove everything before first blank line (headers) ---
    text = re.split(r"\n\s*\n", text, maxsplit=1)
    text = text[1] if len(text) > 1 else text[0]

    # Remove quoted replies and forwards
    text = re.sub(r"(?m)^>.*\n?", "", text)
    text = re.sub(r"-{2,}\s*Original Message\s*-{2,}", "", text, flags=re.I)

    # Remove signatures
    text = re.sub(r"(?m)(--\s*\n.*$)", "", text)
    text = re.sub(r"(?m)(Thanks|Regards|Sincerely),?\n.*", "", text)

    # Remove URLs, emails, phone numbers
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"\+?\d[\d\s.-]{7,}\d", "", text)

    # Normalize spaces
    text = re.sub(r"[^a-zA-Z0-9.,!?'\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# --- Preprocess and update in DB ---
email = emails_col.find_one({"_id": ObjectId("6892fe052589ce0138d7759d")})
if email:
    clean_body = clean_email(email.get("message", ""))
    emails_col.update_one(
        {"_id": email["_id"]},
        {"$set": {"clean_message": clean_body}}
    )
    print("✅ Preprocessing done for single email.")
