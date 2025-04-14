// src/App.js

import React, { useState, useEffect } from "react";
import axios from "axios";
import Chatbot from "./components/Chatbot/Chatbot";
import LoginPage from "./components/LoginPage/LoginPage";
import CollectionsPage from "./components/CollectionsPage/CollectionsPage";
import "./App.css";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCollection, setSelectedCollection] = useState(null);

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

  // Handle selecting a collection
  const handleSelectCollection = (collectionId) => {
    setSelectedCollection(collectionId);
  };

  // Handle going back to collections page
  const handleBackToCollections = () => {
    setSelectedCollection(null);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  // If not logged in, show the LoginPage
  if (!user) {
    return <LoginPage />;
  }

  // If logged in but no collection selected, show the CollectionsPage
  if (!selectedCollection) {
    return (
      <CollectionsPage
        user={user}
        onSelectCollection={handleSelectCollection}
      />
    );
  }

  // If logged in and collection selected, show the Chatbot component
  return (
    <div className="App">
      <Chatbot
        user={user}
        initialCollection={selectedCollection}
        onBackToCollections={handleBackToCollections}
      />
    </div>
  );
}

export default App;
