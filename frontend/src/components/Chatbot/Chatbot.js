import React, { useState } from "react";
import axios from "axios";
import "./Chatbot.css";

const Chatbot = () => {
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Trigger the Google OAuth login via Flask
  const handleLogin = () => {
    window.location.href = "http://localhost:5050/login";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    setIsLoading(true);
    setConversation((prev) => [...prev, { sender: "user", text: message }]);

    try {
      // Send the request with credentials to include the session cookie
   const response = await axios.post(
  "http://localhost:5050/api/chat",
  { message },
  { withCredentials: true }
);

      setConversation((prev) => [
        ...prev,
        { sender: "bot", text: response.data.response },
      ]);
    } catch (error) {
      console.error("Error details:", error);
      setConversation((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Connection error. Please check if you are logged in and the backend is running.",
        },
      ]);
    } finally {
      setMessage("");
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <h1>Transportation Chatbot</h1>
      {/* Login Button for Google OAuth */}
      <button onClick={handleLogin}>Login with Google</button>
      
      <div className="chat-window">
        {conversation.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            <div className="message-content">{msg.text}</div>
          </div>
        ))}
        {isLoading && (
          <div className="message bot">
            <div className="message-content">Thinking...</div>
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask me about traffic simulation..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Sending..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default Chatbot;
