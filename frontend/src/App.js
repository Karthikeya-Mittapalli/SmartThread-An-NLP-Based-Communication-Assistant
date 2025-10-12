import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import EmailsPage from "./pages/EmailsPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/emails" element={<EmailsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
