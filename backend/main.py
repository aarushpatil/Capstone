import os, sys
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

# Import the helper from llm.py to generate responses from the LLM.
from LLM.LLM import get_llm_response

# ------------------------------------------
# Flask App Setup
# ------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")  # Loaded from .env

# Configure session cookie settings for local development.
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

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
        print("Logged in user:", user_info, flush=True)
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

# ------------------------------------------
# Run App
# ------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
