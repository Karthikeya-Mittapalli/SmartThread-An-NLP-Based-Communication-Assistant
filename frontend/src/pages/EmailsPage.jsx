// frontend/src/EmailsPage.js
import React, { useEffect, useState } from "react";
import "./EmailsPage.css";

const EmailsPage = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [replyMap, setReplyMap] = useState({});

  const handleReplyGen = async (email) => {
    const existing = replyMap[email.id];
    if (existing && existing.reply) {
      setReplyMap((prev) => ({
        ...prev,
        [email.id]: { ...existing, visible: true },
      }));
      return;
    }
    setReplyMap((prev) => ({
      ...prev,
      [email.id]: { loading: true, reply: "", visible: true },
    }));
    try {
      const res = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/generate_reply`,
        {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message_id: email.id }),
        }
      );
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setReplyMap((prev) => ({
        ...prev,
        [email.id]: { loading: false, reply: data.reply, visible: true },
      }));
    } catch (err) {
      console.error("Failed to generate reply:", err);
      setReplyMap((prev) => ({
        ...prev,
        [email.id]: {
          loading: false,
          reply: "Failed to generate reply. Please try again.",
          visible: true,
        },
      }));
    }
  };

  const sendReply = async (email) => {
    const replyText = replyMap[email.id]?.reply || "";
    if (!replyText) {
      alert("No reply text to send!");
      return;
    }
    try {
      const res = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/reply_email`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            message_id: email.id,
            reply_text: replyText,
          }),
        }
      );
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      await res.json();
      setReplyMap((prev) => ({
        ...prev,
        [email.id]: { visible: false },
      }));
      alert("Reply sent successfully!");
    } catch (err) {
      console.error("Failed to send reply:", err);
      alert("Failed to send reply. Please try again.");
    }
  };

  const hideReply = (emailId) => {
    setReplyMap((prev) => ({
      ...prev,
      [emailId]: { ...prev[emailId], visible: false },
    }));
  };

  useEffect(() => {
    const fetchEmails = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await fetch(
          `${process.env.REACT_APP_BACKEND_URL}/fetch_emails`,
          {
            credentials: "include",
          }
        );
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
  if (emails.length === 0)
    return <div className="no-emails">No unread emails found.</div>;

  return (
    <div className="emails-page">
      <header className="emails-header">
        <div className="logo-container">
          <img src="/smart-mail.png" alt="SmartMail" className="app-logo" />
          <h1>SmartMail Inbox</h1>
        </div>
      </header>

      <div className="emails-container">
        {emails.map((email) => {
          const replyState = replyMap[email.id] || {};
          const isVisible = replyState.visible;

          return (
            <div key={email.id} className="email-card">
              <div className="email-header">
                <p className="email-field">
                  <strong>From:</strong> {email.from}
                </p>
                <span
                  className={`priority-badge ${
                    email.priority?.toLowerCase() || "low"
                  }`}
                >
                  {email.priority}
                </span>
              </div>
              <p className="email-field subject">
                <strong>Subject:</strong> {email.subject}
              </p>
              <p className="email-body">{email.body}</p>
              <div className="email-summary">
                <strong>Summary:</strong>
                <br />
                {email.summary}
              </div>

              {isVisible ? (
                <div className="reply-section">
                  <strong>Generated Reply:</strong>
                  {replyState.loading ? (
                    <p>⏳ Generating reply...</p>
                  ) : (
                    <>
                      <textarea
                        className="reply-textarea"
                        value={replyState.reply}
                        onChange={(e) =>
                          setReplyMap((prev) => ({
                            ...prev,
                            [email.id]: {
                              ...prev[email.id],
                              reply: e.target.value,
                            },
                          }))
                        }
                        rows={4}
                      />
                      <div className="reply-buttons">
                        <button
                          onClick={() => sendReply(email)}
                          disabled={!replyState.reply?.trim()}
                        >
                          Send Reply
                        </button>
                        <button
                          className="hide-reply-btn"
                          onClick={() => hideReply(email.id)}
                        >
                          Hide Reply
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <button
                  onClick={() => handleReplyGen(email)}
                  disabled={replyState.loading}
                  className="generate-reply-btn"
                >
                  {replyState.loading ? "Generating..." : "Generate Reply"}
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default EmailsPage;
