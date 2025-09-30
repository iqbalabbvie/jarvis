import os
import dotenv
import requests
import traceback

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
    try:
        # Log raw request body for debugging
        print("Raw request body:", request.data)

        # Safely decode JSON
        try:
            data = request.get_json(force=True)
        except Exception as json_error:
            print("JSON decode error:", json_error)
            return jsonify({'response': f'Invalid JSON: {str(json_error)}'}), 400

        print("Received data:", data)

        user_input = data.get('message')
        if not user_input or not isinstance(user_input, str):
            print("Invalid input received.")
            return jsonify({'response': 'Invalid input'}), 400

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

        print("Iliad response status code:", resp.status_code)
        print("Iliad response body:", resp.text)

        # Raise error if status code is not 2xx
        resp.raise_for_status()

        # Return Iliad response
        return jsonify(resp.json())

    except requests.RequestException as e:
        print("RequestException:", e)
        try:
            print("Error response status:", e.response.status_code)
            print("Error response body:", e.response.text)
            return jsonify({
                'response': 'Iliad API error',
                'status_code': e.response.status_code,
                'details': e.response.text
            }), 500
        except Exception as inner:
            print("No response object in exception:", inner)
            return jsonify({'response': 'Request failed and no error body was returned'}), 500

    except Exception as e:
        print("Unexpected error occurred:")
        traceback.print_exc()
        return jsonify({'response': f'Unexpected error: {str(e)}'}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
