import os
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

# Optionally load environment variables from a .env file:
# from dotenv import load_dotenv
# load_dotenv()

# ------------------------------------------
# Flask App Setup
# ------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "5c10e992e83a9cb776c3e8e0eb2621e378e1d5e1cd086eb9"
)

# Configure session cookie settings for local development.
# 'Lax' helps ensure the cookie is sent back during cross-site redirects.
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# ------------------------------------------
# Google OAuth Setup
# ------------------------------------------
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.environ.get("GOOGLE_CLIENT_ID", "949161818506-1g6q16me5kt8vvpnv3tivs982df6tivi.apps.googleusercontent.com"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET", "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"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# ------------------------------------------
# OAuth Routes
# ------------------------------------------

@app.route("/login")
def login():
    redirect_uri = url_for("authorize", _external=True)
    # For debugging, check what is in the session before redirecting.
    print("Session before redirect:", dict(session), flush=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/authorize")
def authorize():
    try:
        token = google.authorize_access_token()  # Exchange the code for a token
        
        # Explicitly load the server metadata from Google
        metadata = google.load_server_metadata()
        userinfo_endpoint = metadata.get("userinfo_endpoint")
        print("Loaded userinfo endpoint:", userinfo_endpoint, flush=True)
        
        # If for some reason it's missing, fall back to the known endpoint
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
        user_message = data.get("message", "")
        response = f"{user_message}"
        return jsonify({"response": response, "status": "success"})
    except Exception as e:
        print("Error:", str(e), flush=True)
        return jsonify({"response": f"Error processing your request: {str(e)}", "status": "error"}), 500

@app.route("/api/user", methods=["GET"])
def get_user():
    user = session.get("user")
    if user:
        return jsonify({"status": "success", "user": user})
    return jsonify({"status": "error", "message": "User not logged in"}), 401

@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"status": "success", "message": "Backend is working!"})

# ------------------------------------------
# Run App
# ------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
