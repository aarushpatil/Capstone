import os, sys
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
# from werkzeug.exceptions import ClientDisconnected

# Import the helper from llm.py to generate responses from the LLM.
from LLM.LLM import get_llm_response
from CollectionManager import *

# ------------------------------------------
# Flask App Setup
# ------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")  # Loaded from .env

# Configure session cookie settings for local development.
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

@app.errorhandler(ConnectionResetError)
def handle_client_disconnect(error):
    print("Client disconnected abruptly.", flush=True)
    return "", 499  # Custom status for aborted requests

# ------------------------------------------
# Google OAuth Setup
# ------------------------------------------
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),  # Loaded from .env
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),  # Loaded from .env
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ------------------------------------------
# OAuth Routes
# ------------------------------------------

@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    print("Session before redirect:", dict(session), flush=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/authorize")
def authorize():
    try:
        token = google.authorize_access_token()  # Exchange the code for a token
        metadata = google.load_server_metadata()
        userinfo_endpoint = metadata.get("userinfo_endpoint")
        print("Loaded userinfo endpoint:", userinfo_endpoint, flush=True)
        if not userinfo_endpoint:
            userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
            print("Using fallback userinfo endpoint:", userinfo_endpoint, flush=True)
        resp = google.get(userinfo_endpoint)
        user_info = resp.json()
        session["user"] = user_info
        print("Logged in user:", user_info["sub"], flush=True)


        #add to db
        makeUser(user_info["sub"])

        return redirect("http://localhost:3000")  # Redirect back to your React app
    except Exception as e:
        print("Error during authorization:", e, flush=True)
        return f"An error occurred during authorization: {e}", 500

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("http://localhost:3000")

# ------------------------------------------
# Auth-Protected API Routes
# ------------------------------------------

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
        return jsonify({"response": f"Error processing your request: {str(e)}", "status": "error"}), 500

@app.route("/api/user", methods=["GET"])
def get_user():
    user = session.get("user")
    if user:
        return jsonify({"status": "success", "user": user})
    return jsonify({"status": "error", "message": "User not logged in"}), 401


#non auth protected routes:

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
        return jsonify({"response": f"Error processing your request: {str(e)}", "status": "error"}), 500


@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"status": "success", "message": "Backend is working!"})



#Get collections for user
#Add Collection for user
#delete collection for user

#ChatHistory for Collection
#Add to chatHistory for collection

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
        return jsonify({"response": f"Error processing your request: {str(e)}", "status": "error"}), 500

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
        {"$set": {"collections.$.name": new_name}}
    )

    return jsonify({"status": "success", "message": "Collection renamed"})



# ------------------------------------------
# Run App
# ------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
