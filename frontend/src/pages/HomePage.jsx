import "./HomePage.css";
function HomePage() {
  const handleLogin = () => {
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/login`;
  };

  return (
    <div>
      <h1>SmartMail</h1>
      <button onClick={handleLogin}>Login with Google</button>
    </div>
  );
}

export default HomePage;
