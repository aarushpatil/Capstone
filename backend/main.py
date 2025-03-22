from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/test", methods=["GET"])
def test():
    return jsonify("Working!")

@app.route("/echo", methods=["POST"])
def echo():
    content = request.json
    return jsonify({"you_sent": content})

if __name__ == "__main__":
    app.run(debug=True)
