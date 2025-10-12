// frontend/src/EmailsPage.js
import React, { useEffect, useState } from "react";
import "./EmailPage.css";

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
          credentials: "include" // include cookies for session
        });

        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }

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

  if (loading) {
    return <div>Loading emails...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>{error}</div>;
  }

  if (emails.length === 0) {
    return <div>No unread emails found.</div>;
  }

  return (
    <div className="emails-page">
      <h2>Unread Emails</h2>
      {emails.map((email) => (
        <div key={email.id} className="email-card">
          <p className="email-field"><strong>From:</strong> {email.from}</p>
          <p className="email-field"><strong>Subject:</strong> {email.subject}</p>
          <p className="email-snippet">{email.snippet}</p>
          <div className="email-summary">
            <strong>Summary:</strong>
            <br />
            {email.summary}
          </div>
          <div className="email-priority">
            <strong>Priority:</strong>{" "}
            <span
              className={
                email.priority === "High"
                  ? "high"
                  : email.priority === "Medium"
                  ? "medium"
                  : "low"
              }
            >
              {email.priority}
            </span>
          </div>
        </div>
    )
  )
  }
</div>
  );
};

export default EmailsPage;
