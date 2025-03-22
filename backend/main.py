from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for testing


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        print("Received request:", data)  # Add this for debugging
        user_message = data.get("message", "")

        # TODO: Add your actual LLM processing logic here
        # For now, we'll just echo the message with a prefix
        response = f"{user_message}"

        return jsonify({"response": response, "status": "success"})

    except Exception as e:
        print("Error:", str(e))  # Add this for debugging
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


if __name__ == "__main__":
    if __name__ == "__main__":
        app.run(host="0.0.0.0", debug=True)

