import React, { useState } from "react";
import "./Chatbot.css";
import axios from "axios";

const Chatbot = () => {
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    setIsLoading(true);
    setConversation((prev) => [...prev, { sender: "user", text: message }]);

    try {
      console.log("Sending request to:", "http://127.0.0.1:5000/api/chat");
      const response = await axios.post("http://127.0.0.1:5000/api/chat", {
        message: message,
      });
      console.log("Response received:", response.data);
      setConversation((prev) => [
        ...prev,
        { sender: "bot", text: response.data.response },
      ]);
    } catch (error) {
      console.error("Full Error Details:", error);
      console.error("Request Config:", error.config);
      if (error.response) {
        console.error("Response Data:", error.response.data);
        console.error("Response Status:", error.response.status);
        console.error("Response Headers:", error.response.headers);
      } else if (error.request) {
        console.error("Request:", error.request);
      }
      setConversation((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Connection error. Please check if the backend is running.",
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
