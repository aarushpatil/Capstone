import React, { useState, useEffect } from "react";
import axios from "axios";
import { FiLogOut, FiPlus, FiFolder, FiSearch, FiTrash } from "react-icons/fi";

const CollectionsPage = ({ user, onSelectCollection }) => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newCollectionName, setNewCollectionName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [deletingCollectionId, setDeletingCollectionId] = useState(null);

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

  const deleteCollection = async (collectionId) => {
    setDeletingCollectionId(collectionId);
    try {
      await axios.delete(`http://localhost:5050/api/collections/${collectionId}`, { withCredentials: true });
      fetchCollections();
    } catch (error) {
      console.error("Error deleting collection", error);
    } finally {
      setDeletingCollectionId(null);
    }
  };

  const handleCollectionClick = (collectionId) => {
    onSelectCollection(collectionId);
  };

  const filteredCollections = collections.filter((collection) =>
    collection.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header
        className="
          px-6 py-6           /* Increased padding for breathing room */
          bg-white shadow
          flex items-center
          justify-between
          mb-4                /* Added margin-bottom to separate header from content */
        "
      >
        <h1 className="text-xl font-semibold text-gray-800">
          Transportation Chatbot
        </h1>
        <div className="flex items-center gap-8">
          {" "}
          {/* Changed gap from 4 to 8 for more space */}
          {/* Search */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search collections..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
          </div>
          {/* User/Logout */}
          {user && (
            <div className="flex items-center gap-2">
              <button
                onClick={async () => {
                  try {
                    await axios.post(
                      "http://localhost:5050/api/logout",
                      {},
                      { withCredentials: true }
                    );
                    window.location.reload();
                  } catch (error) {
                    console.error("Logout error:", error);
                  }
                }}
                className="flex items-center justify-center gap-1 text-sm bg-red-100 hover:bg-red-200 text-red-600 px-3 py-2 rounded-md transition"
              >
                <FiLogOut />
                Logout
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto px-6 pb-6">
        <div className="max-w-6xl mx-auto">
          {/* Collections heading and "New Collection" button */}
          <div className="mb-8 flex justify-between items-center">
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

          {/* Loading / No Collections / Collections Grid */}
          {loading ? (
            <div className="text-center py-20">
              <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="mt-4 text-gray-600">Loading collections...</p>
            </div>
          ) : filteredCollections.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-lg shadow-md border border-gray-200">
              <p>No Collections Yet!</p>
            </div>
          ) :(
            <div className="w-full">
              {filteredCollections.map((collection) => (
                <div
                  key={collection.collectionId}
                  onClick={() =>
                    handleCollectionClick(collection.collectionId)
                  }
                  className="bg-white flex w-full items-center p-4 mb-4 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer border border-gray-200 hover:border-blue-400 transform hover:-translate-y-1"
                >
                  {/* <div className="bg-blue-100 w-10 h-10">
                    <FiFolder className="text-blue-600" />
                  </div> */}
                  <span className="text-lg font-medium text-gray-800 pl-10 ml-100">
                    {`\t${collection.name}`}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default CollectionsPage;