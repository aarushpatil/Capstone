import React from "react";
import { FcGoogle } from "react-icons/fc"; // Google icon

const LoginPage = () => {
  const handleLogin = () => {
    window.location.href = "http://localhost:5050/login";
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-100 to-white">
      <div className="bg-white rounded-2xl shadow-2xl p-10 max-w-md w-full text-center transform transition-all duration-300 hover:scale-[1.01]">
        <h1 className="text-3xl font-extrabold text-gray-800 mb-3">
     <div className="flex flex-col items-center text-center">
  <span className="text-2xl font-extrabold text-gray-800 mb-3">Welcome to</span>
  <span className="text-blue-600 text-2xl font-bold">The Transportation Chatbot</span>
</div>

        </h1>
        <p className="text-gray-600 mb-8 text-sm">
          Your AI assistant for seamless travel. Log in with Google to begin.
        </p>
        <button
          onClick={handleLogin}
          className="flex items-center justify-center gap-2 bg-white border border-gray-300 hover:border-gray-400 text-gray-700 hover:shadow-md font-medium py-2 px-4 rounded-md w-full transition duration-200"
        >
          <FcGoogle className="text-xl" />
          Continue with Google
        </button>
      </div>
    </div>
  );
};

export default LoginPage;
