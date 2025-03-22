// src/components/LoginPage/LoginPage.js

import React from "react";
import "./LoginPage.css";

const LoginPage = () => {
  const handleLogin = () => {
    window.location.href = "http://localhost:5050/login";
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h1>Welcome to Transportation Chatbot</h1>
        <p>Please log in with Google to continue</p>
        <button className="login-button" onClick={handleLogin}>
          Login with Google
        </button>
      </div>
    </div>
  );
};

export default LoginPage;
