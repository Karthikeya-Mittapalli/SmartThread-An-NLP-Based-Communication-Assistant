import re
from pymongo import MongoClient
from bson import ObjectId
from email.utils import getaddresses, parseaddr

# --- MongoDB Connection ---
client = MongoClient("mongodb://localhost:27017/")
db = client["enron_email"]
emails_col = db["mails"]


def clean_email_body(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # Remove everything before first blank line (headers)
    parts = re.split(r"\n\s*\n", text, maxsplit=1)
    text = parts[1] if len(parts) > 1 else parts[0]

    # Remove quoted replies, forwards, signatures
    text = re.sub(r"(?m)^>.*\n?", "", text)
    text = re.sub(r"-{2,}\s*Original Message\s*-{2,}", "", text, flags=re.I)
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


def clean_name(name: str) -> str:
    if not name:
        return ""
    # Remove junk like "/ENRON@enronXgate"
    # Remove anything in angle brackets
    name = re.sub(r"<.*?>", "", name)
    # Remove junk like "/ENRON@enronXgate"
    name = re.sub(r"/ENRON.*", "", name)
    # Remove extra quotes and spaces
    return name.strip().strip('"').strip()


def parse_address_field(raw_str: str) -> list[dict]:
    """Return list of {name, email} dicts"""
    results = []
    if not raw_str:
        return results

    parsed = getaddresses([raw_str])
    for name, email in parsed:
        results.append({
            "name": clean_name(name),
            "email": email.lower().strip() if email else ""
        })
    return results


def parse_headers(raw_text: str) -> dict:
    """Extract headers including X-From, X-To, From, To, Subject"""
    headers = {}
    if not raw_text:
        return headers

    header_block = re.split(r"\n\s*\n", raw_text, maxsplit=1)[0]
    for line in header_block.splitlines():
        parts = line.split(":", 1)
        if len(parts) == 2:
            key, value = parts
            headers[key.strip()] = value.strip()
    return headers


def preprocess_email(email_doc):
    raw_message = email_doc.get("message", "")
    headers = parse_headers(raw_message)

    # --- Extract sender info ---
    from_field = {
        "name": clean_name(headers.get("X-From", "")) or clean_name(parseaddr(headers.get("From", ""))[0]),
        "email": headers.get("From", "").lower().strip()
    }

# --- Extract recipients ---
    to_field = {
        "name": clean_name(headers.get("X-To", "")) or clean_name(parseaddr(headers.get("From", ""))[0]),
        "email": headers.get("To", "").lower().strip()
    }

    
    # to_field = parse_address_field(headers.get("X-To", "") or headers.get("To", ""))
    # cc_field = parse_address_field(headers.get("X-cc", "") or headers.get("Cc", ""))
    # bcc_field = parse_address_field(headers.get("X-bcc", "") or headers.get("Bcc", ""))

    return {
        "from": from_field,
        "to": to_field,
        # "cc": cc_field,
        # "bcc": bcc_field,
        "subject": headers.get("Subject", "").strip(),
        # "date": headers.get("Date", ""),
        "clean_message": clean_email_body(raw_message)
    }


# --- Example Run ---
email = emails_col.find_one({"_id": ObjectId("6892fe052589ce0138d7759e")})
if email:
    processed = preprocess_email(email)
    emails_col.update_one({"_id": email["_id"]}, {"$set": processed})
    print("✅ Preprocessing done for single email.")
