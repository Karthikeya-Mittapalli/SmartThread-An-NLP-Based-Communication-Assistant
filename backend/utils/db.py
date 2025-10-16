# src/db.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "emails_cache.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            user_id TEXT,
            id TEXT,
            thread_id TEXT,
            subject TEXT,
            sender TEXT,
            body TEXT,
            summary TEXT,
            priority TEXT,
            PRIMARY KEY (user_id, id)
        )
    """)
    conn.commit()
    conn.close()

def save_email(user_id, email_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO emails (user_id, id, thread_id, subject, sender, body, summary, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        email_data["id"],
        email_data.get("thread_id"),
        email_data.get("subject"),
        email_data.get("from"),
        email_data.get("body", ""),
        email_data.get("summary", ""),
        email_data.get("priority", "Medium"),
    ))
    conn.commit()
    conn.close()

def get_email_body(user_id, message_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT body FROM emails WHERE user_id = ? AND id = ?", (user_id, message_id))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_emails_from_db(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, thread_id, subject, sender, body, summary, priority FROM emails WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    emails = []
    for r in rows:
        emails.append({
            "id": r[0],
            "threadId": r[1],
            "subject": r[2],
            "from": r[3],
            "body": r[4],
            "summary": r[5],
            "priority": r[6]
        })
    return emails
