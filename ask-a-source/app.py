import os
import dotenv
import requests
import pprint

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Load environment variables
dotenv.load_dotenv()

# Set up Flask app
app = Flask(__name__, static_folder='chat-bot-ui/build', static_url_path='')
CORS(app)

# Environment variables
ILIAD_KEY = os.getenv("ILIAD_API_KEY")
ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
USER_TOKEN = os.getenv("USER_TOKEN")

# Validate environment variables
if not ILIAD_KEY or not USER_TOKEN:
    raise EnvironmentError("Missing ILIAD_API_KEY or USER_TOKEN in environment")

# Serve React frontend
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Health check route
@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200

# API route
@app.route('/api/post-data', methods=['POST'])
def post_data():
    data = request.json
    print("Received data:", data)

    user_input = data.get('message')
    if not user_input or not isinstance(user_input, str):
        return jsonify({'response': 'Invalid input'}), 400

    try:
        print("Sending request to Iliad API...")
        resp = requests.post(
            url=f"{ILIAD_URL}/api/v1/sources/my-new-source-admp/rag",
            headers={
                "x-api-key": ILIAD_KEY,
                "x-user-token": USER_TOKEN
            },
            json={
                "chat_model": "gpt-4o",
                "messages": [{"role": "user", "content": user_input}],
                "minimum_score": 0
            }
        )
        print("Status code:", resp.status_code)
        print("Response text:", resp.text)

        resp.raise_for_status()
        return jsonify(resp.json())

    except requests.RequestException as e:
        print("RequestException:", e)
        if hasattr(e, 'response') and e.response is not None:
            print("Error response status:", e.response.status_code)
            print("Error response body:", e.response.text)
        return jsonify({'response': 'Error retrieving response'}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
