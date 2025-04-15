import os, sys
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS

# Import the helper from llm.py to generate responses from the LLM.
from LLM.LLM import get_llm_response
from CollectionManager import *

## Flask Setup

app = Flask(__name__)
app.secret_key = "664cb08f7c25c9a63ab8630e18c21881a9a358318d62580bc3e80a479edad489"

# Configure session cookie settings for local development.
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production with HTTPS

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


@app.errorhandler(ConnectionResetError)
def handle_client_disconnect(error):
    print("Client disconnected abruptly.", flush=True)
    return "", 499  # Custom status for aborted requests

## Authentication Routes

@app.route("/api/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        # Basic validation
        if not email or not password:
            return (
                jsonify(
                    {"status": "error", "message": "Email and password are required"}
                ),
                400,
            )

        # Check if email already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({"status": "error", "message": "Email already exists"}), 400

        # Create the user
        user_id = create_user(email, password)
        if user_id:
            # Set up the session
            user_info = {"sub": user_id, "email": email}
            session["user"] = user_info
            return jsonify({"status": "success", "user": user_info})
        else:
            return jsonify({"status": "error", "message": "Failed to create user"}), 500
    except Exception as e:
        print("Error during registration:", e, flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        # Basic validation
        if not email or not password:
            return (
                jsonify(
                    {"status": "error", "message": "Email and password are required"}
                ),
                400,
            )

        # Get user
        user = get_user_by_email(email)
        if not user or user["password"] != password:
            return (
                jsonify({"status": "error", "message": "Invalid email or password"}),
                401,
            )

        # Set up the session
        user_info = {"sub": user["id"], "email": user["email"]}
        session["user"] = user_info
        return jsonify({"status": "success", "user": user_info})
    except Exception as e:
        print("Error during login:", e, flush=True)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"status": "success"})

## API Routes

@app.route("/api/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"status": "error", "response": "Not authorized"}), 401
    try:
        data = request.get_json()
        print("Received request:", data, flush=True)
        user_message = data.get("message", "").strip()

        # Call the helper from llm.py to get the response from the LLM.
        llm_response = get_llm_response(user_message)

        return jsonify({"response": llm_response, "status": "success"})
    except Exception as e:
        print("Error in /api/chat:", str(e), flush=True)
        return (
            jsonify(
                {
                    "response": f"Error processing your request: {str(e)}",
                    "status": "error",
                }
            ),
            500,
        )


@app.route("/api/user", methods=["GET"])
def get_user():
    user = session.get("user")
    if user:
        return jsonify({"status": "success", "user": user})
    return jsonify({"status": "error", "message": "User not logged in"}), 401

## Non auth protected routes:

@app.route("/chatNoAuth", methods=["POST"])
def chatNoAuth():
    try:
        data = request.get_json()
        print("Received request:", data, flush=True)
        user_message = data.get("message", "").strip()
        print("**************")
        print(user_message)
        print("**************")

        # Call the helper from llm.py to get the response from the LLM.
        llm_response = get_llm_response(user_message)

        return jsonify({"response": llm_response, "status": "success"})
    except Exception as e:
        print("Error in /api/chat:", str(e), flush=True)
        return (
            jsonify(
                {
                    "response": f"Error processing your request: {str(e)}",
                    "status": "error",
                }
            ),
            500,
        )


@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"status": "success", "message": "Backend is working!"})

@app.route("/api/collections", methods=["POST"])
def create_collection():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Not authorized"}), 401

    user_id = session["user"]["sub"]
    data = request.get_json()
    collection_name = data.get("name", "New Collection")
    collection_id = add_collection(user_id, collection_name)

    return jsonify({"status": "success", "collectionId": collection_id})


@app.route("/api/collections", methods=["GET"])
def fetch_collections():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Not authorized"}), 401

    user_id = session["user"]["sub"]
    collections = get_collections(user_id)

    return jsonify({"status": "success", "collections": collections})


@app.route("/api/collections/<collection_id>", methods=["DELETE"])
def remove_collection(collection_id):
    if "user" not in session:
        return jsonify({"status": "error", "message": "Not authorized"}), 401

    user_id = session["user"]["sub"]
    delete_collection(user_id, collection_id)

    return jsonify({"status": "success", "message": "Collection deleted"})


@app.route("/api/collections/<collection_id>/history", methods=["GET"])
def fetch_chat_history(collection_id):
    if "user" not in session:
        return jsonify({"status": "error", "message": "Not authorized"}), 401

    user_id = session["user"]["sub"]
    history = get_chat_history(user_id, collection_id)

    return jsonify({"status": "success", "chatHistory": history})


@app.route("/api/collections/<collection_id>/chat", methods=["POST"])
def chat_in_collection(collection_id):
    try:
        if "user" not in session:
            return jsonify({"status": "error", "message": "Not authorized"}), 401
        user_id = session["user"]["sub"]
        data = request.get_json()
        user_message = data.get("message", "").strip()

        user_id = session["user"]["sub"]
        history = get_chat_history(user_id, collection_id)

        # Get response from the LLM
        llm_response = get_llm_response(user_message, history)

        # Save user message
        add_message(user_id, collection_id, "user", user_message)
        # Save assistant response
        add_message(user_id, collection_id, "assistant", llm_response)
    except Exception as e:
        return (
            jsonify(
                {
                    "response": f"Error processing your request: {str(e)}",
                    "status": "error",
                }
            ),
            500,
        )

    return jsonify({"response": llm_response, "status": "success"})


@app.route("/api/rename_collection", methods=["POST"])
def rename_collection():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Not authorized"}), 401

    data = request.get_json()
    user_id = session["user"]["sub"]
    collection_id = data.get("collectionId")
    new_name = data.get("newName", "").strip()

    if not collection_id or not new_name:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    user = users_collection.find_one({"_id": user_id})
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Update the collection name
    users_collection.update_one(
        {"_id": user_id, "collections.collectionId": collection_id},
        {"$set": {"collections.$.name": new_name}},
    )

    return jsonify({"status": "success", "message": "Collection renamed"})


# run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
