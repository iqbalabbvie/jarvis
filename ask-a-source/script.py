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

#'source': 'my-new-source-admp-chatbot'}
#'source': 'my-new-source-admp'}

# ====================Create a New source=====================
# resp = requests.post(
#     url=f"{ILIAD_URL}/api/v1/sources",
#     headers={
#         "x-api-key": ILIAD_KEY,
#         "x-user-token": USER_TOKEN
#     },
#     json={
#         "source": "my-new-source-admp-chatbot",
#         "description": "Just an example for the Iliad docs!",
#         "custom_fields": json.dumps({
#           "owning_facility": {"type": "text"},
#           "location": {"type": "text"}
#         })
#     }
# )
# resp.raise_for_status()

# pprint.pprint(resp.json())

#==========Upload documents to your source=====================
# for file in pathlib.Path("files").iterdir():
#     #custom_fields = {"owning_facility": "ABV1", "location": "Mettawa"}
#     resp = requests.post(
#         url=f"{ILIAD_URL}/api/v1/sources/my-new-source-admp/documents",
#         headers={"x-api-key": ILIAD_KEY, "x-user-token": USER_TOKEN},
#         files={"file": file.open("rb")},
#         #params={"custom_fields": json.dumps(custom_fields)}
#     )
#     resp.raise_for_status()

#============Delete a document from source=========================
# resp = requests.DELETE(
#     url=f"{ILIAD_URL}/api/v1/sources/my-new-source-admp/documents/218d7d4b-cdc3-4603-9e9e-b6a254442f8b",
#     headers={"x-api-key": ILIAD_KEY, "x-user-token": USER_TOKEN}
# )
# pprint.pprint(resp.json())

#===============List all the documents in your source============================
resp = requests.get(
    url=f"{ILIAD_URL}/api/v1/sources/my-new-source-admp/documents",
    headers={"x-api-key": ILIAD_KEY, "x-user-token": USER_TOKEN}
)
pprint.pprint(resp.json())

#===============Asking your source============================

# resp = requests.post(
#     url=f"{ILIAD_URL}/api/v1/sources/my-new-source-admp/rag",
#     headers={"x-api-key": ILIAD_KEY, "x-user-token": USER_TOKEN},
#     json={
#       "chat_model": "gpt-4o",
#     #   "messages": [{"role": "user", "content": "what is name of the release pipeline"}],
#     #   "messages": [{"role": "user", "content": "what is name of the build pipeline"}],
#     #   "messages": [{"role": "user", "content": "differnt type of utilities"}],
#     #"messages": [{"role": "user", "content": "which utility class increases bottom border width to 5 pixels"}],
#         "messages": [{"role": "user", "content": "Which icon class we need to use for Add Location"}],
#         # "messages": [{"role": "user", "content": "Which component we can use for Display progress of multiple activities"}],
#       "minimum_score ": 0
      
#     }
# )
# pprint.pprint(resp.json())

#==============================================================

#Streamlit : http://localhost:8501/