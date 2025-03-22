// src/App.js

import React, { useState, useEffect } from "react";
import axios from "axios";
import Chatbot from "./components/Chatbot/Chatbot";
import LoginPage from "./components/LoginPage/LoginPage";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if the user is logged in by calling the backend
  useEffect(() => {
    axios
      .get("http://localhost:5050/api/user", { withCredentials: true })
      .then((res) => {
        if (res.data.status === "success") {
          setUser(res.data.user);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("User not logged in", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  // If not logged in, show the LoginPage
  if (!user) {
    return <LoginPage />;
  }

  // Once logged in, show the Chatbot component (optionally pass user info)
  return (
    <div className="App">
      <Chatbot user={user} />

     
      
    </div>
  );
}

export default App;
