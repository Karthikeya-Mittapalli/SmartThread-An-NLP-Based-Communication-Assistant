from flask import Flask, redirect, request, session, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
from flask_cors import CORS

from src.priority_detection_flask import detect_priority
from src.thread_summarization_flask import summarize_thread
from src.email_analyzer import analyze_email

import os
import time
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
            msg_data = service.users().messages().get(
                userId="me", id=msg["id"]).execute()
            headers = msg_data["payload"]["headers"]

            subject = next(
                (h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
            sender = next(
                (h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
            snippet = msg_data.get("snippet", "")

            analysis_result = analyze_email(snippet)

            # thread_messages = [{"from": sender, "text": snippet, "timestamp": ""}]

            # # Summarize
            # summary_raw = summarize_thread(thread_messages)
            # time.sleep(3)
            # # Clean formatting: add bullets and bold titles
            # summary_clean = f"Email Thread Summary:\nFrom: {sender}\nKey Points:\n{summary_raw}"

            # # Detect priority
            # priority = detect_priority(summary_clean)
            # time.sleep(5)

            emails.append({
                "id": msg["id"],
                "subject": subject,
                "from": sender,
                "snippet": snippet,
                "summary": analysis_result.get("summary", snippet),
                "priority": analysis_result.get("priority", "Medium")
            })

            time.sleep(5)

        except Exception as e:
            time.sleep(5)
            print(f"[FetchEmails] Error processing message {msg['id']}: {e}")

    # Sort emails by priority: High -> Medium -> Low
    emails_sorted = sorted(
        emails, key=lambda e: PRIORITY_ORDER.get(e["priority"], 3))

    return jsonify(emails_sorted)


if __name__ == "__main__":
    app.run(port=8000, debug=True)
