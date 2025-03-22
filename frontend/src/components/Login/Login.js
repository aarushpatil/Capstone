import React from "react";
import "./Login.css";

const Login = ({ setIsAuthenticated }) => {
  const handleLogin = () => {
    window.location.href = "http://localhost:5050/login";
  };

  return (
    <div className="login-container">
      <h1>Welcome to the Transportation Chatbot</h1>
      <p>Please login to continue</p>
      <button onClick={handleLogin}>Login with Google</button>
    </div>
  );
};

export default Login;
