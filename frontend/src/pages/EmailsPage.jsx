// frontend/src/EmailsPage.js
import React, { useEffect, useState } from "react";

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
    <div style={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
        <h2>Unread Emails</h2>
        {emails.map((email) => (
            <div
                key={email.id}
                style={{
                border: "1px solid #ccc",
                borderRadius: "8px",
                padding: "1rem",
                marginBottom: "1rem",
                backgroundColor: "#f9f9f9",
                }}
            >
            <p><strong>From:</strong> {email.from}</p>
            <p><strong>Subject:</strong> {email.subject}</p>
            <p><strong>Snippet:</strong> {email.snippet}</p>
            <hr />
            <p>
            <strong>Summary:</strong>
            <br />
            {email.summary.split("\n").map((line, idx) => (
                <span key={idx}>
                {line}
                <br />
                </span>
            ))}
            </p>
            <p>
            <strong>Priority:</strong>{" "}
            <span
                style={{
                color:
                    email.priority === "High"
                    ? "red"
                    : email.priority === "Medium"
                    ? "orange"
                    : "green",
                fontWeight: "bold",
                }}
            >
                {email.priority}
            </span>
            </p>
        </div>
        ))}
    </div>
  );
};

export default EmailsPage;
