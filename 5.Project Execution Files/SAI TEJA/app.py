from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(
    __name__,
    static_folder="static",  # Specify the folder for static files
    static_url_path="/static",  # URL path for accessing static files
    template_folder="templates",  # Specify the folder for templates
)

CORS(app)  # Enable CORS for the Flask app

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# About page route
@app.route("/about")
def about():
    return render_template("about.html")

# Contact Us page route
@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

# Chatbot page route
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

# Chat route (for handling user messages)
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Rasa endpoint
    rasa_url = "http://localhost:5055/webhooks/rest/webhook"
    payload = {"sender": "user", "message": user_message}
    
    try:
        # Send the message to Rasa's endpoint
        response = requests.post(rasa_url, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors

        responses = response.json()
        messages = [resp.get("text") for resp in responses if "text" in resp]
        return jsonify({"responses": messages})
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Failed to connect to Rasa server. Ensure Rasa is running."}), 500
    except requests.exceptions.Timeout:
        return jsonify({"error": "Rasa server took too long to respond."}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=8080, debug=True)
