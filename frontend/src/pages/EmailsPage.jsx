// frontend/src/EmailsPage.js
import React, { useEffect, useState } from "react";
import "./EmailsPage.css";

const EmailsPage = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchEmails = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/fetch_emails`, {
          credentials: "include"
        });
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        const data = await res.json();
        setEmails(data);
      } catch (err) {
        console.error("Failed to fetch emails:", err);
        setError("Failed to fetch emails. Try logging in again.");
      } finally {
        setLoading(false);
      }
    };
    fetchEmails();
  }, []);

  if (loading) return <div className="loading">📬 Fetching your emails...</div>;
  if (error) return <div className="error">{error}</div>;
  if (emails.length === 0) return <div className="no-emails">No unread emails found.</div>;

  return (
    <div className="emails-page">
      <header className="emails-header">
        <div className="logo-container">
          <img src="/smart-mail.png" alt="SmartMail" className="app-logo" />
          <h1>SmartMail Inbox</h1>
        </div>
      </header>

      <div className="emails-container">
        {emails.map((email) => (
          <div key={email.id} className="email-card">
            <div className="email-header">
              <p className="email-field"><strong>From:</strong> {email.from}</p>
              <span
                className={`priority-badge ${
                  email.priority?.toLowerCase() || "low"
                }`}
              >
                {email.priority}
              </span>
            </div>
            <p className="email-field subject"><strong>Subject:</strong> {email.subject}</p>
            <p className="email-snippet">{email.snippet}</p>
            <div className="email-summary">
              <strong>Summary:</strong>
              <br />
              {email.summary}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EmailsPage;
