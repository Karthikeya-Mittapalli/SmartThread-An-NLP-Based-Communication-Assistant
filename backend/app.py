from flask import Flask, redirect, request, session, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from dotenv import load_dotenv
from flask_cors import CORS

from src.priority_detection_flask import detect_priority
from src.thread_summarization_flask import summarize_thread
from src.email_analyzer import analyze_email

import os
import time
import base64
load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

CLIENT_SECRET_FILE = os.getenv("GOOGLE_CLIENT_SECRET_FILE")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = [os.getenv("GOOGLE_SCOPES")]

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

@app.route("/")
def home():
    return "SmartMail Flask Backend is running!"

# Step 1: Redirect to Google OAuth
@app.route("/login")
def login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )
    # ✅ Save only the *state string*, not the whole flow object
    session["state"] = state
    return redirect(auth_url)

# Step 2: Handle callback and fetch token
@app.route("/auth/callback")
def auth_callback():
    state = session.get("state")
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )

    auth_response = request.url
    flow.fetch_token(authorization_response=auth_response)
    credentials = flow.credentials
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }
    frontend_url = os.getenv("REACT_APP_FRONTEND_URL", "http://localhost:3000")
    return redirect(f"{frontend_url}/emails")

# Step 3: Fetch unread emails
# backend/app.py (only fetch_emails route updated)
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}  # for sorting

@app.route("/fetch_emails")
def fetch_emails():
    creds_data = session.get("credentials")
    if not creds_data:
        return redirect("/login")

    creds = Credentials(**creds_data)
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me", labelIds=["UNREAD"], maxResults=10
    ).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        try:
            msg_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
            headers = msg_data["payload"]["headers"]

            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")

            payload = msg_data.get("payload", {})
            body_text = extract_message_body(payload) or msg_data.get("snippet", "")

            analysis_result = analyze_email(body_text)

            emails.append({
                "id": msg["id"],
                "threadId": msg_data.get("threadId"),
                "subject": subject,
                "from": sender,
                "body": body_text,
                "summary": analysis_result.get("summary", body_text[:200] + "..."),
                "priority": analysis_result.get("priority", "Medium")
            })

            time.sleep(5)

        except Exception as e:
            time.sleep(5)
            print(f"[FetchEmails] Error processing message {msg['id']}: {e}")

    # Sort emails by priority: High -> Medium -> Low
    emails_sorted = sorted(emails, key=lambda e: PRIORITY_ORDER.get(e["priority"], 3))

    return jsonify(emails_sorted)

# Step 4: Reply to an email
@app.route("/reply_email", methods=["POST"])
def reply_email():
    data = request.get_json()
    msg_id = data.get("message_id")
    reply_text = data.get("reply_text")

    creds_data = session.get("credentials")
    if not creds_data:
        return redirect("/login")

    creds = Credentials(**creds_data)
    service = build("gmail", "v1", credentials=creds)

    # 1️⃣ Fetch the original message
    original_msg = service.users().messages().get(userId="me", id=msg_id, format="metadata", metadataHeaders=["Subject", "From", "Message-ID"]).execute()
    headers = {h["name"]: h["value"] for h in original_msg["payload"]["headers"]}

    subject = headers.get("Subject", "(No Subject)")
    sender = headers.get("From")
    message_id = headers.get("Message-ID")
    thread_id = original_msg["threadId"]

    # 2️⃣ Build reply email
    reply_subject = f"Re: {subject}" if not subject.startswith("Re:") else subject
    reply_to = sender.split("<")[-1].replace(">", "").strip()  # Extract clean email address

    reply = MIMEText(reply_text)
    reply["To"] = reply_to
    reply["Subject"] = reply_subject
    reply["In-Reply-To"] = message_id
    reply["References"] = message_id

    raw_msg = base64.urlsafe_b64encode(reply.as_bytes()).decode()

    # 3️⃣ Send the message in the same thread
    sent_msg = service.users().messages().send(
        userId="me",
        body={
            "raw": raw_msg,
            "threadId": thread_id
        }
    ).execute()

    return jsonify({"status": "success", "sent_message_id": sent_msg["id"], "thread_id": thread_id})


def extract_message_body(payload):
    """Recursively extract plain text content from a Gmail message payload."""
    if payload.get("mimeType") == "text/plain":
        return base64.urlsafe_b64decode(payload["body"].get("data", "")).decode("utf-8", errors="ignore")

    elif "parts" in payload:
        parts_text = []
        for part in payload["parts"]:
            text = extract_message_body(part)
            if text:
                parts_text.append(text)
        return "\n".join(parts_text)

    return ""


if __name__ == "__main__":
    app.run(port=8000, debug=True)
