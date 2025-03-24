import React, { useState, useEffect } from "react";
import axios from "axios";
import { FiLogOut, FiPlus, FiFolder } from "react-icons/fi";

const Chatbot = () => {
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState(null); // 👤 To store logged-in user info
  const [collections] = useState(["Simulation Basics", "Traffic Lights", "Intersection Rules"]);

  // 👤 Fetch user info on component mount
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await axios.get("http://localhost:5050/api/user", {
          withCredentials: true,
        });
        setUser(res.data.user);
      } catch (err) {
        console.error("Failed to fetch user", err);
      }
    };

    fetchUser();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    setIsLoading(true);
    setConversation((prev) => [...prev, { sender: "user", text: message }]);

    try {
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
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md p-4 flex flex-col">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Collections
          </h2>
          <ul className="space-y-2">
            {collections.map((name, idx) => (
              <li
                key={idx}
                className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded cursor-pointer transition"
              >
                <FiFolder className="text-blue-500" />
                {name}
              </li>
            ))}
            <li className="flex items-center gap-2 px-3 py-2 text-sm text-blue-600 hover:bg-blue-100 rounded cursor-pointer transition">
              <FiPlus />
              New Collection
            </li>
          </ul>
        </div>
        <button
          onClick={() => (window.location.href = "http://localhost:5050/logout")}
          className="mt-auto flex items-center gap-2 text-sm bg-red-100 hover:bg-red-200 text-red-600 px-3 py-2 rounded-md transition"
        >
          <FiLogOut />
          Logout
        </button>
      </aside>

      {/* Chat Section */}
      <main className="flex flex-col flex-1">
        {/* Header */}
        <header className="px-6 py-4 bg-white shadow flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-800">
            Transportation Chatbot
          </h1>
          {user && (
            <span className="text-sm text-gray-600">
              Welcome, <span className="font-large">{user.name}</span>
            </span>
          )}
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 bg-gray-50">
          {conversation.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xl px-4 py-3 rounded-xl shadow ${
                  msg.sender === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-white text-gray-800 border rounded-bl-none"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-xl px-4 py-3 rounded-xl bg-white text-gray-500 border shadow rounded-bl-none">
                Thinking...
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="flex items-center gap-2 px-6 py-4 bg-white border-t shadow-inner"
        >
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me about traffic simulation..."
            disabled={isLoading}
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg transition disabled:opacity-50"
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </form>
      </main>
    </div>
  );
};

export default Chatbot;
