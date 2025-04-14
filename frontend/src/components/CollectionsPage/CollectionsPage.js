import React, { useState, useEffect } from "react";
import axios from "axios";
import { FiLogOut, FiPlus, FiFolder, FiSearch } from "react-icons/fi";

const CollectionsPage = ({ user, onSelectCollection }) => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newCollectionName, setNewCollectionName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        "http://localhost:5050/api/collections",
        { withCredentials: true }
      );
      if (response.data.status === "success") {
        setCollections(response.data.collections);
      }
    } catch (error) {
      console.error("Error fetching collections", error);
    } finally {
      setLoading(false);
    }
  };

  const createCollection = async () => {
    try {
      const response = await axios.post(
        "http://localhost:5050/api/collections",
        { name: newCollectionName || "New Collection" },
        { withCredentials: true }
      );
      if (response.data.status === "success") {
        fetchCollections();
        setNewCollectionName("");
        setIsCreating(false);
      }
    } catch (error) {
      console.error("Error creating collection", error);
    }
  };

  const handleCollectionClick = (collectionId) => {
    onSelectCollection(collectionId);
  };

  const filteredCollections = collections.filter((collection) =>
    collection.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md p-4 flex flex-col">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Navigation
          </h2>
          <ul className="space-y-2">
            <li className="flex items-center px-3 py-2 bg-blue-100 text-blue-700 rounded">
              <FiFolder className="mr-2" />
              Collections
            </li>
          </ul>
        </div>
        <div className="mt-auto">
          {user && (
            <div className="mb-4 py-3 px-3 bg-gray-100 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Signed in as</p>
              <p className="font-medium text-gray-900 truncate">{user.name}</p>
            </div>
          )}
          <button
            onClick={() =>
              (window.location.href = "http://localhost:5050/logout")
            }
            className="w-full flex items-center justify-center gap-2 text-sm bg-red-100 hover:bg-red-200 text-red-600 px-3 py-2 rounded-md transition"
          >
            <FiLogOut />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="px-6 py-4 bg-white shadow flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-800">
            Transportation Chatbot
          </h1>
          <div className="relative flex items-center">
            <FiSearch className="absolute left-3 text-gray-400" />
            <input
              type="text"
              placeholder="Search collections..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </header>

        {/* Collections Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-6xl mx-auto">
            <div className="mb-6 flex justify-between items-center">
              <h2 className="text-2xl font-semibold text-gray-800">
                Your Collections
              </h2>
              {!isCreating && (
                <button
                  onClick={() => setIsCreating(true)}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition shadow-sm"
                >
                  <FiPlus />
                  New Collection
                </button>
              )}
            </div>

            {/* New Collection Form */}
            {isCreating && (
              <div className="mb-6 p-6 bg-white rounded-lg shadow-md border border-gray-200">
                <h3 className="text-lg font-medium text-gray-800 mb-4">
                  Create New Collection
                </h3>
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={newCollectionName}
                    onChange={(e) => setNewCollectionName(e.target.value)}
                    placeholder="Collection name"
                    className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                  <button
                    onClick={createCollection}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-5 py-2 rounded-lg transition shadow-sm"
                  >
                    Create
                  </button>
                  <button
                    onClick={() => {
                      setIsCreating(false);
                      setNewCollectionName("");
                    }}
                    className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium px-5 py-2 rounded-lg transition"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {loading ? (
              <div className="text-center py-20">
                <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="mt-4 text-gray-600">Loading collections...</p>
              </div>
            ) : filteredCollections.length === 0 ? (
              <div className="text-center py-16 bg-white rounded-lg shadow-md border border-gray-200">
                {searchTerm ? (
                  <p className="text-gray-600 mb-4">
                    No collections found matching "{searchTerm}"
                  </p>
                ) : (
                  <>
                    <FiFolder className="text-blue-500 text-5xl mx-auto mb-4" />
                    <p className="text-gray-600 mb-4 text-lg">
                      You don't have any collections yet.
                    </p>
                    <button
                      onClick={() => setIsCreating(true)}
                      className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg transition mx-auto shadow-sm"
                    >
                      <FiPlus />
                      Create Your First Collection
                    </button>
                  </>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {filteredCollections.map((collection) => (
                  <div
                    key={collection.collectionId}
                    onClick={() =>
                      handleCollectionClick(collection.collectionId)
                    }
                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all duration-200 cursor-pointer border border-gray-200 hover:border-blue-400 transform hover:-translate-y-1"
                  >
                    <div className="flex items-center gap-3 mb-3">
                      <div className="p-3 bg-blue-100 rounded-lg">
                        <FiFolder className="text-blue-600 text-xl" />
                      </div>
                      <h3 className="text-lg font-medium text-gray-800">
                        {collection.name}
                      </h3>
                    </div>
                    <div className="pt-2 border-t border-gray-100">
                      <p className="text-sm text-gray-600">
                        Click to start chatting
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default CollectionsPage;
