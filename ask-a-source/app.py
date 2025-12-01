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

import time      # for timing key activities
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

@app.route('/api/llmscheckold', methods=['POST'])
def llmcheckold():

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
    
@app.route('/api/llmscheck', methods=['POST'])
def llmcheck():
    # Start overall timing
    function_start_time = time.time()
    print(f"\n=== LLMCHECK FUNCTION STARTED ===")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(function_start_time))}")
    
    data = request.json
    user_input = data.get('input')
    modeldetails = data.get('model').split(':', 1) # Split only at the first colon
    
    print(f"User input length: {len(user_input)} characters")
    print(f"Model: {modeldetails[1]}")

    try:
        # Step 1: First, get documents using the RAG endpoint to retrieve with scores
        print("\n--- STEP 1: RAG DOCUMENT RETRIEVAL ---")
        rag_start_time = time.time()
        print(f"RAG search started at: {time.strftime('%H:%M:%S', time.localtime(rag_start_time))}")
        
        rag_resp = requests.post(
            url=f"{ILIAD_URL}/api/v1/sources/my-new-source-rinvoq/rag?k=10",
            headers={"x-api-key": ILIAD_KEY, "x-user-token": USER_TOKEN},
            json={
                "chat_model": modeldetails[1],
                "messages": [{"role": "user", "content": user_input}],
                "minimum_score": 0.1,
                "return_sources": True  # Request source information
            }
        )
        
        rag_end_time = time.time()
        rag_duration = rag_end_time - rag_start_time
        print(f"RAG search completed in: {rag_duration:.2f} seconds")
        
        if rag_resp.status_code != 200:
            print(f"RAG search failed with status: {rag_resp.status_code}")
            print(f"RAG response: {rag_resp.text}")
            return jsonify({'response': 'Error retrieving documents from RAG'}), 500
            
        rag_data = rag_resp.json()
        print(f"RAG response keys: {rag_data.keys()}")
        
        # Step 2: Extract documents and scores from RAG response
        print("\n--- STEP 2: DOCUMENT PROCESSING ---")
        doc_processing_start_time = time.time()
        print(f"Document processing started at: {time.strftime('%H:%M:%S', time.localtime(doc_processing_start_time))}")
        
        documents = []
        sources_info = []
        
        # Check different possible response structures
        if 'references' in rag_data:
            sources_info = rag_data['references']
        elif 'context' in rag_data:
            sources_info = rag_data['context']
        elif 'retrieved_documents' in rag_data:
            sources_info = rag_data['retrieved_documents']
        
        # Extract document information
        for i, source in enumerate(sources_info):
            if isinstance(source, dict):
                documents.append({
                    'content': source.get('content', source.get('text', '')),
                    'score': source.get('score', source.get('score', 1.0 - i*0.1)),  # Fallback scoring
                    'metadata': source.get('metadata', {}),
                    'source': source.get('source', source.get('filename', f'Document_{i+1}'))
                })
            else:
                # If source is just text
                documents.append({
                    'content': str(source),
                    'score': 1.0 - i*0.1,  # Assign decreasing scores
                    'metadata': {},
                    'source': f'Document_{i+1}'
                })
        
        # If no documents found in sources, try to extract from the response itself
        if not documents and 'completion' in rag_data:
            # Fallback: create a single document from the response
            documents.append({
                'content': rag_data['completion'].get('content', ''),
                'score': 1.0,
                'metadata': {},
                'source': 'RAG_Response'
            })
        
        # Step 3: Sort documents by score in descending order (highest relevance first)
        documents.sort(key=lambda x: x['score'], reverse=True)
        
        doc_processing_end_time = time.time()
        doc_processing_duration = doc_processing_end_time - doc_processing_start_time
        print(f"Document processing completed in: {doc_processing_duration:.2f} seconds")
        print(f"Found {len(documents)} documents, sorted by relevance score")
        
        # Step 4: Select top documents (top 5 highest scoring)
        top_documents = documents[:5]
        print(f"Selected top {len(top_documents)} documents for context")
        
        if not top_documents:
            return jsonify({
                'response': 'No relevant documents found for your query.',
                'documents_found': 0,
                'scores': []
            })
        
        # Step 5: Create enhanced context from top documents
        print("\n--- STEP 3: CONTEXT CREATION ---")
        context_start_time = time.time()
        
        context_parts = []
        source_list = []
        scores = []
        
        for i, doc in enumerate(top_documents, 1):
            context_parts.append(f"Document {i} (Relevance Score: {doc['score']:.3f}):\n{doc['content']}")
            source_list.append(f"Document {i}: {doc['source']} (Score: {doc['score']:.3f})")
            scores.append(doc['score'])
        
        enhanced_context = "\n\n---\n\n".join(context_parts)
        
        context_end_time = time.time()
        context_duration = context_end_time - context_start_time
        print(f"Context creation completed in: {context_duration:.2f} seconds")
        print(f"Enhanced context length: {len(enhanced_context)} characters")
        # Step 6: Create enhanced system prompt with document context
        sys_prompt = f"""
You are a medically-grounded AI assistant. You must answer ONLY using the retrieved context from the company's approved medical content below, which has been sorted by relevance score.

RETRIEVED CONTEXT (sorted by relevance):
{enhanced_context}

Your responsibilities:
1. Provide accurate, detailed, and easy-to-understand medical answers based ONLY on the above context.
2. ALWAYS include safety-related information when available:
   - Warnings and precautions
   - Contraindications
   - Side effects
   - Black box warnings (if applicable)
   - Age or population restrictions
   - Drug interactions (only if provided in retrieved content)
3. NEVER provide clinical judgement, diagnosis, or personalized medical advice.
4. NEVER hallucinate or infer medical information not directly supported by the retrieved context above.

Response Format (MUST follow exactly):
**1. Answer**
- Provide a detailed and factual explanation using the retrieved context.
- Stay strictly within the bounds of the provided medical content.
- Feel Free to follow links in the retrieved content to formulate a better resposne
- Use clear, patient-friendly language unless the content specifies clinical terminology.
- Reference which documents (by number) or webpage support your answer.

**2. Safety Information**
- Summarize ALL relevant safety details found in the retrieved context.
- Include warnings, precautions, contraindications, side effects, or monitoring instructions.
- If the retrieved context lacks safety information, state:
  "No additional safety information was available in the retrieved medical content."

**3. Important Notes**
- Include the following standard regulatory disclaimer:
  "This information is for educational purposes only and not a substitute for professional medical advice. Always consult a qualified healthcare provider for diagnosis, treatment, or medical decisions."

**4. Sources Used**
- List the document names and their relevance scores that supported your answer.
- List any webpage used for this context

Core Rules:
- Do NOT guess or speculate about safety or efficacy.
- If context is insufficient, say: "I do not have enough information in the retrieved medical content to provide a complete answer."
- Do NOT provide dosage, treatment, or instructions unless explicitly in retrieved data.
- Do NOT offer any off-label, investigational, or non-approved use information.
- If a user asks for personal medical guidance, respond with: "I can only provide information from approved medical content. For personal medical advice, please consult a healthcare professional."

Tone: Professional, medically accurate, neutral, and empathetic.
"""

        # Step 7: Generate LLM response using the enhanced context
        print("\n--- STEP 4: LLM RESPONSE GENERATION ---")
        llm_start_time = time.time()
        print(f"LLM request started at: {time.strftime('%H:%M:%S', time.localtime(llm_start_time))}")
        print(f"System prompt length: {len(sys_prompt)} characters")
        
        llm_resp = requests.post(
            url=f"{ILIAD_URL}/api/v1/chat/{modeldetails[1]}",
            headers={"x-api-key": ILIAD_KEY, "x-user-token": USER_TOKEN},
            json={
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_input}
                ]
            }
        )
        
        llm_end_time = time.time()
        llm_duration = llm_end_time - llm_start_time
        print(f"LLM response completed in: {llm_duration:.2f} seconds")
        
        if llm_resp.status_code != 200:
            print(f"LLM request failed with status: {llm_resp.status_code}")
            return jsonify({'response': 'Error generating LLM response'}), 500
        llm_data = llm_resp.json()
        
        # Step 8: Return enhanced response with document metadata
        print("\n--- STEP 5: RESPONSE PREPARATION ---")
        response_prep_start_time = time.time()
        
        response = {
            'response': llm_data.get('completion', {}).get('content', 'No response generated'),
            'documents_used': len(top_documents),
            'document_scores': scores,
            'sources': source_list,
            'total_documents_found': len(documents),
            'original_rag_response': rag_data.get('completion', {}).get('content', '') if 'completion' in rag_data else ''
        }
        
        response_prep_end_time = time.time()
        response_prep_duration = response_prep_end_time - response_prep_start_time
        
        # Calculate total function execution time
        function_end_time = time.time()
        total_duration = function_end_time - function_start_time
        
        # Print comprehensive timing summary
        print(f"\n=== TIMING SUMMARY ===")
        print(f"RAG Document Retrieval: {rag_duration:.2f}s")
        print(f"Document Processing: {doc_processing_duration:.2f}s")
        print(f"Context Creation: {context_duration:.2f}s")
        print(f"LLM Response Generation: {llm_duration:.2f}s")
        print(f"Response Preparation: {response_prep_duration:.2f}s")
        print(f"TOTAL EXECUTION TIME: {total_duration:.2f}s")
        print(f"Function completed at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(function_end_time))}")
        print(f"Response generated successfully using {len(top_documents)} top-scoring documents")
        print("=== LLMCHECK FUNCTION COMPLETED ===\n")
        
        return jsonify(response)
        
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return jsonify({'response': 'Error retrieving response'}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'response': 'An unexpected error occurred'}), 500

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
