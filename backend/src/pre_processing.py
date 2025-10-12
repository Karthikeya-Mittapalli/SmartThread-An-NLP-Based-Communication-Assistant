# src/pre_processing.py
import re
from email import message_from_string
from email.utils import parseaddr, getaddresses, parsedate_to_datetime
from datetime import datetime
from pymongo import MongoClient

# If you prefer to use MONGO_URI from .env later, wire it up. For now hardcoded local:
client = MongoClient("mongodb://localhost:27017/")
db = client["enron_email"]
emails_col = db["mails"]
threads_col = db["threads"]


def clean_email_body(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # If the message contains headers+body, try to split by blank line
    parts = re.split(r"\n\s*\n", text, maxsplit=1)
    body = parts[1] if len(parts) > 1 else parts[0]

    # Remove quoted replies (lines starting with >)
    body = re.sub(r"(?m)^\s*>.*\n?", "", body)
    # Remove common forwarded/original markers
    body = re.sub(r"-{2,}\s*Original Message\s*-{2,}", "", body, flags=re.I)
    # Remove signature start (simple heuristic)
    body = re.sub(r"(?m)(--\s*\n.*$)", "", body)
    body = re.sub(
        r"(?mi)(^\s*(thanks|regards|sincerely|cheers)[\.,]?\s*$).*", "", body, flags=re.S)

    # Remove URLs/emails/phones
    body = re.sub(r"http\S+|www\S+", "", body)
    body = re.sub(r"\S+@\S+", "", body)
    body = re.sub(r"\+?\d[\d\s\-\(\)\.]{6,}\d", "", body)

    # Keep basic punctuation and letters/digits
    body = re.sub(r"[^a-zA-Z0-9.,!?'\n\s]", " ", body)
    body = re.sub(r"\s+", " ", body)
    return body.strip()


def clean_name(name: str) -> str:
    if not name:
        return ""
    name = re.sub(r"<.*?>", "", name)
    name = re.sub(r"/ENRON.*", "", name)
    return name.strip().strip('"').strip()


def parse_address_field(raw_str: str):
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


def normalize_subject(subj: str) -> str:
    if not subj:
        return ""
    subj = subj.lower().strip()
    subj = re.sub(r'^(re|fwd|fw):\s*', '', subj)
    subj = re.sub(r'\s+', ' ', subj)
    return subj


def parse_headers_with_email(raw_text: str) -> dict:
    """Use Python email parsing to extract headers robustly."""
    headers = {}
    if not raw_text:
        return headers
    try:
        msg = message_from_string(raw_text)
        for k, v in msg.items():
            headers[k] = v
    except Exception:
        # Fallback: simple header split
        header_block = re.split(r"\n\s*\n", raw_text, maxsplit=1)[0]
        for line in header_block.splitlines():
            parts = line.split(":", 1)
            if len(parts) == 2:
                key, value = parts
                headers[key.strip()] = value.strip()
    return headers


def preprocess_email(email_doc: dict) -> dict:
    raw_message = email_doc.get("message", "")
    headers = parse_headers_with_email(raw_message)

    # message-id
    message_id = (headers.get("Message-ID") or "").strip()
    message_id = message_id.strip("<>") if message_id else ""

    # from
    from_name, from_email = parseaddr(headers.get("From", ""))
    from_field = {
        "name": clean_name(headers.get("X-From", "") or from_name),
        "email": from_email.lower().strip() if from_email else ""
    }

    # to, cc, bcc as arrays
    to_list = []
    raw_to = headers.get("To", "")
    if raw_to:
        parsed_to = parse_address_field(raw_to)
        # if we also have X-To, use it to clean names where possible
        x_to = headers.get("X-To", "")
        if x_to:
            cleaned_x_to = [clean_name(n) for n, _ in getaddresses([x_to])]
            for i, entry in enumerate(parsed_to):
                if i < len(cleaned_x_to) and cleaned_x_to[i]:
                    entry["name"] = cleaned_x_to[i]
        to_list = parsed_to
    cc_list = parse_address_field(headers.get(
        "X-cc", "") or headers.get("Cc", ""))
    bcc_list = parse_address_field(headers.get(
        "X-bcc", "") or headers.get("Bcc", ""))

    # date
    try:
        date_val = headers.get("Date", "")
        timestamp = parsedate_to_datetime(
            date_val) if date_val else datetime.utcnow()
    except Exception:
        timestamp = datetime.utcnow()

    in_reply = headers.get("In-Reply-To", "")
    if in_reply:
        in_reply = in_reply.strip().strip("<>")

    refs = headers.get("References", "")
    references = [r.strip().strip("<>") for r in refs.split()] if refs else []

    return {
        "message_id": message_id,
        "from": from_field,
        "to": to_list,
        "cc": cc_list,
        "bcc": bcc_list,
        "subject": (headers.get("Subject") or "").strip(),
        "normalized_subject": normalize_subject(headers.get("Subject") or ""),
        "date": timestamp,
        "clean_message": clean_email_body(raw_message),
        "in_reply_to": in_reply or None,
        "references": references
    }
