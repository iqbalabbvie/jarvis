
import dotenv    # loads our .env file into environment variables
import os        # reads environment variables
import pathlib   # navigates the file system and opens files
import pprint    # for inspecting Iliad response messages
import requests  # for communicating with the Iliad API
import json
import re


from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import partial

dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

ILIAD_KEY = os.getenv("ILIAD_API_KEY")
ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
USER_TOKEN = os.getenv("USER_TOKEN")

@app.route('/api/post-data', methods=['POST'])
def post_data():
    data = request.json
    user_input = data.get('message')
    payload = {
      "chat_model": "gpt-4o",
      "messages": [{"role": "user", "content": user_input}],
      "minimum_score ": 0
    }
    # Process the input text and return the response
    #response = f"You entered: {user_input}" 
    try: 
      resp = requests.post(
      url=f"{ILIAD_URL}/api/v1/sources/my-new-source-admp/rag",
      headers={"x-api-key": ILIAD_KEY, "x-user-token": USER_TOKEN},
      json={
        "chat_model": "gpt-4o",
        #   "messages": [{"role": "user", "content": "what is name of the release pipeline"}],
        #   "messages": [{"role": "user", "content": "what is name of the build pipeline"}],
        #   "messages": [{"role": "user", "content": "differnt type of utilities"}],
        #"messages": [{"role": "user", "content": "which utility class increases bottom border width to 5 pixels"}],
            # "messages": [{"role": "user", "content": "Which icon class we need to use for Add Location"}],
            # "messages": [{"role": "user", "content": "Which component we can use for Display progress of multiple activities"}],
          "messages": [{"role": "user", "content": user_input}],
          "minimum_score ": 0
          
        }
        )
      pprint.pprint(resp.json())
      response = resp.json() 
      
      #resp = {
      #  'message': data,
      #  'items': 'dummy data being passed'
      #}
      #pprint.pprint(resp.json())
      #response = resp.json()
    except requests.RequestException as e :
       return jsonify({'response' : 'Error retrieving response'}), 500
     

    return jsonify(response)
                                  

if __name__ == "__main__":
  app.run(debug=True)