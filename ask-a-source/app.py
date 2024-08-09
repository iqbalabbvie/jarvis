import streamlit as st
import dotenv    # loads our .env file into environment variables
import os        # reads environment variables
import pathlib   # navigates the file system and opens files
import pprint    # for inspecting Iliad response messages
import requests  # for communicating with the Iliad API
import json

dotenv.load_dotenv()

ILIAD_KEY = os.getenv("ILIAD_API_KEY")
ILIAD_URL = "https://api-epic.ir-gateway.abbvienet.com/iliad"
USER_TOKEN = os.getenv("USER_TOKEN")


def process_input(input_text):
    # Process the input text and return the response
    response = f"You entered: {input_text}"
    
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
        "messages": [{"role": "user", "content": input_text}],
      "minimum_score ": 0
      
    }
    )
    pprint.pprint(resp.json())
    response = resp.json()
    return response

def main():
    st.title("JARVIS")
    
    # Get user input
    input_text = st.text_input("Enter your message...:")
    # Process the input and display the response
    if st.button("Process"):
        response = process_input(input_text)
        st.write("Response:")
        st.write(response)

if __name__ == "__main__":
    main()