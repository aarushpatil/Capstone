import React, { useState, useEffect } from "react";
import axios from "axios";
import { FiLogOut, FiPlus, FiFolder, FiTrash } from "react-icons/fi";

const Chatbot = ({ user }) => {
  const [message, setMessage] = useState("");
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [collections, setCollections] = useState([]);
  const [activeCollection, setActiveCollection] = useState(null);
  const [editingCollection, setEditingCollection] = useState(null);
  const [newCollectionName, setNewCollectionName] = useState("");

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      const response = await axios.get("http://localhost:5050/api/collections", { withCredentials: true });
      if (response.data.status === "success") {
        setCollections(response.data.collections);
      }
    } catch (error) {
      console.error("Error fetching collections", error);
    }
  };

  const createCollection = async () => {
    try {
      const response = await axios.post("http://localhost:5050/api/collections", { name: "New Collection" }, { withCredentials: true });
      if (response.data.status === "success") {
        fetchCollections();
      }
    } catch (error) {
      console.error("Error creating collection", error);
    }
  };

  const deleteCollection = async (collectionId) => {
    try {
      await axios.delete(`http://localhost:5050/api/collections/${collectionId}`, { withCredentials: true });
      setCollections(collections.filter(collection => collection.collectionId !== collectionId));
      if (activeCollection === collectionId) {
        setActiveCollection(null);
        setConversation([]);
      }
    } catch (error) {
      console.error("Error deleting collection", error);
    }
  };

  const fetchChatHistory = async (collectionId) => {
    setActiveCollection(collectionId);
    try {
      const response = await axios.get(`http://localhost:5050/api/collections/${collectionId}/history`, { withCredentials: true });
      if (response.data.status === "success") {
        setConversation(response.data.chatHistory);
      }
    } catch (error) {
      console.error("Error fetching chat history", error);
    }
  };

  const truncateName = (name) => {
    return name.length > 30 ? name.substring(0, 30) + "..." : name;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading || !activeCollection) return;

    setIsLoading(true);
    setConversation((prev) => [...prev, { role: "user", content: message }]);

    try {
      const response = await axios.post(
        `http://localhost:5050/api/collections/${activeCollection}/chat`,
        { message },
        { withCredentials: true }
      );
      setConversation((prev) => [...prev, { role: "assistant", content: response.data.response }]);
    } catch (error) {
      console.error("Error sending message", error);
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
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Collections</h2>
          <ul className="space-y-2">
            {collections.map((collection) => (
              <li
                key={collection.collectionId}
                className={`flex items-center justify-between px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded cursor-pointer transition ${
                  activeCollection === collection.collectionId ? "bg-gray-200" : ""
                }`}
              >
                <div className="flex items-center gap-2" onClick={() => fetchChatHistory(collection.collectionId)}>
                  <FiFolder className="text-blue-500" />
                  {truncateName(collection.name)}
                </div>
                <FiTrash
                  className="text-red-500 hover:text-red-700 cursor-pointer"
                  onClick={() => deleteCollection(collection.collectionId)}
                />
              </li>
            ))}
            <li
              className="flex items-center gap-2 px-3 py-2 text-sm text-blue-600 hover:bg-blue-100 rounded cursor-pointer transition"
              onClick={createCollection}
            >
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
        <header className="px-6 py-4 bg-white shadow">
          <h1 className="text-xl font-semibold text-gray-800">Transportation Chatbot</h1>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 bg-gray-50">
          {conversation.map((msg, index) => (
            <div key={index} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-xl px-4 py-3 rounded-xl shadow ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-white text-gray-800 border rounded-bl-none"
                }`}
              >
                {msg.content}
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
        <form onSubmit={handleSubmit} className="flex items-center gap-2 px-6 py-4 bg-white border-t shadow-inner">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me about traffic simulation..."
            disabled={isLoading || !activeCollection}
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !activeCollection}
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
