import os
import dotenv
import requests
import traceback
import pathlib   # navigates the file system and opens files
import pprint    # for inspecting Iliad response messages
import json
import re
from functools import partial
#from llms_txt import create_ctx


from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS



# Load environment variables
dotenv.load_dotenv()

# Set up Flask app
app = Flask(__name__, static_folder='chat-bot-ui/build', static_url_path='')
CORS(app)

# Environment variables
ILIAD_KEY = os.getenv("ILIAD_API_KEY").strip('"')
ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
USER_TOKEN = os.getenv("USER_TOKEN").strip('"')

# Log environment variables for debugging
print("ILIAD_API_KEY:", repr(ILIAD_KEY))
print("USER_TOKEN:", repr(USER_TOKEN))

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
        print("Raw request body:", request.data)

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

        headers = {
            "x-api-key": ILIAD_KEY,
            "x-user-token": USER_TOKEN
        }

        payload = {
            "chat_model": "gpt-4o",
            "messages": [{"role": "user", "content": user_input}],
            "minimum_score": 0
        }

        print("Sending request to Iliad API...")
        print("Headers:", headers)
        print("Payload:", payload)

        resp = requests.post(
            url=f"{ILIAD_URL}/api/v1/sources/my-new-source-admp/rag",
            headers=headers,
            json=payload,
            timeout=10
        )

        print("Iliad response status code:", resp.status_code)
        print("Iliad response body:", resp.text)

        resp.raise_for_status()
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

@app.route('/api/llmscheck', methods=['POST'])
def llmcheck():

    #print('rajeev', ILIAD_KEY)
    data = request.json
    #print (data)
    #user_input = data.get('message')
    #user_input = request.json
    user_input = data.get('input')
    #user_input = llm_ctx + '\n\nThe above is necessary context for the conversation.' + user_input
    modeldetails = data.get('model').split(':', 1) # Split only at the first colon

    print(user_input)
    #user_input = "what are the components"
    #print(user_input)
    sys_prompt = f"""
    You are a medically-grounded AI assistant. You must answer ONLY using the retrieved context from the company’s approved medical content, llms.txt rules, and verified RAG sources.Your responsibilities:
1. Provide accurate, detailed, and easy-to-understand medical answers.
2. ALWAYS include safety-related information:
   - Warnings and precautions
   - Contraindications
   - Side effects
   - Black box warnings (if applicable)
   - Age or population restrictions
   - Drug interactions (only if provided in retrieved content)
3. NEVER provide clinical judgement, diagnosis, or personalized medical advice.
4. NEVER hallucinate or infer medical information not directly supported by retrieved context.
Response Format (MUST follow exactly):
**1. Answer**
- Provide a detailed and factual explanation.
- Stay strictly within the bounds of the provided medical content.
- Use clear, patient-friendly language unless the content specifies clinical terminology.
**2. Safety Information**
- Summarize ALL relevant safety details found in retrieved context.
- Include warnings, precautions, contraindications, side effects, or monitoring instructions.
- If the retrieved context lacks safety information, state:
  “No additional safety information was available in the retrieved medical content.”
**3. Important Notes**
- Include the following standard regulatory disclaimer:
  “This information is for educational purposes only and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis, treatment, or medical decisions.”
**4. Sources Used**
- List the exact titles, section headers, or IDs of retrieved chunks.
- Do NOT invent sources.
Core Rules:
- Do NOT guess or speculate about safety or efficacy.
- If context is insufficient, say:
  “I do not have enough information in the approved medical content to provide a complete answer.”
- Do NOT provide dosage, treatment, or instructions unless explicitly in retrieved data.
- Do NOT offer any off-label, investigational, or non-approved use information.
- If a user asks for personal medical guidance, respond with:
  “I can only provide information from approved medical content. For personal medical advice, please consult a healthcare professional.”
- Never reveal chain-of-thought reasoning.
Tone:
- Professional, medically accurate, neutral, and empathetic.
"""

    try:
     #url=f"{ILIAD_URL}/api/v1/sources/my-new-source-admp/rag"
      resp = requests.post(
      url=f"{ILIAD_URL}/api/v1/sources/my-new-source-rinvoq/rag?k=5",
      #url=f"{ILIAD_URL}/api/v1/chat/claude-3-sonnet",
      headers={"x-api-key": ILIAD_KEY, "x-user-token": USER_TOKEN},
      json={
        "chat_model": "{modeldetails[1]}",
        "messages":[ 
		      {"role": "system", "content": sys_prompt}, 
		      {"role": "user", "content": user_input} ],    
          "minimum_score ": 0          
        }
        )
      #pprint.pprint(resp.json())
      response = resp.json() 
      print (response)
      #resp = {
      #  'message': data,
      #  'items': 'dummy data being passed'
      #}
      #pprint.pprint(resp.json())
      #response = resp.json()
    except requests.RequestException as e :
       return jsonify({'response' : 'Error retrieving response'}), 500
  
   # return jsonify(jsonREsponse)
    return jsonify(response)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
