import React, { useState } from "react";
import "./Chatbot.css";

const Chatbot = () => {
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Add user message to conversation
    setConversation((prev) => [...prev, { sender: "user", text: message }]);

    // TODO: Add API call to backend here
    // For now, we'll just add a dummy bot response
    setTimeout(() => {
      setConversation((prev) => [
        ...prev,
        { sender: "bot", text: "This is a dummy response" },
      ]);
    }, 500);

    setMessage("");
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
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask me about traffic simulation..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
};

export default Chatbot;
