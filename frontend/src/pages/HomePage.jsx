import "./HomePage.css";
import { useEffect, useState } from "react";

function HomePage() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Trigger fade-in animation
    setTimeout(() => setVisible(true), 200);
  }, []);

  const handleLogin = () => {
    console.log("Redirecting to backend for Google OAuth...", process.env.REACT_APP_BACKEND_URL);
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/login`;
  };

  return (
    <div className={`homepage ${visible ? "fade-in" : ""}`}>
      <div className="card">
        <div className="logo-section">
          <img
            src="https://cdn-icons-png.flaticon.com/512/893/893292.png"
            alt="SmartMail Logo"
            className="logo"
          />
          <h1>SmartMail</h1>
          <p className="subtitle">
            Your intelligent inbox assistant — Summarize, prioritize, and focus on what truly matters.
          </p>
        </div>

        <button onClick={handleLogin} className="login-btn">
          <img
            src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/google/google-original.svg"
            alt="Google"
            className="google-icon"
          />
          Login with Google
        </button>
      </div>

      <footer>
        <p>© 2025 SmartMail. All Rights Reserved.</p>
      </footer>
    </div>
  );
}

export default HomePage;
