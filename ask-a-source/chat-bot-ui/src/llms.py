import streamlit as st
import requests
import json

st.title(" ")

# User input
#user_text = st.text_input("Please enter your query")
#default_models = ["echo", "openai:gpt-4o-mini", "anthropic:claude-3-5-sonnet", "google:gemini-1.5-pro"]
default_models = ["openai:gpt-4o-mini", "anthropic:claude-3-sonnet", "anthropic:claude-3-haiku", "anthropic:claude-3-opus","anthropic:claude-3.5-sonnet", "anthropic:claude-3.5-haiku", "anthropic:claude-3.5-opus","google:gemini-1.5-pro"]

models = default_models

model = st.selectbox("Model", models)
includellms = st.radio(
    "Include llms.txt",
    ["Yes", "No"],
    captions=[
        "include llms in the search",
        "don't include the llms.txt in the search"
    ],
)

llmsfileref = st.radio(
    "Include llms.txt",
    ["Viiberzi", "Skyrizi","Rinvoq"],
    captions=[
        "include Viiberzi llms in the search",
         "include Skyrizi llms in the search",
         "include Rinvoq llms in the search"
    ],
)
#max_tokens = st.number_input("Max tokens", min_value=16, max_value=8192, value=512, step=16)
system = st.text_area("System prompt (optional)", value="You are a helpful assistant. The above is necessary context for the conversation. include important safety information as separate paragraph. Also include source urls for the information.")
user_text = st.text_area("Your prompt", height=160, placeholder="Ask your question here...")

# Submit button
if st.button("Submit"):
    if user_text.strip():
        try:
            response = requests.post(
            "http://jarvis-api-app.aws-k8s-d.abbvienet.com/api/llmscheck",
            json={"input": user_text,"model":model,"systemtext":system,"includellms":includellms,"llmsfileref":llmsfileref},
            timeout=90
            )
            if response.status_code == 200:
                #print(response.status_code)
                json_string = json.dumps(response.json(), indent=4)
                print('rajeev')
                print (response.json().get('content'))
                st.text(response.json().get('content'))
                #st.text(response.json().get('references'))
                references = response.json().get('references')
                for item1 in references:
                    st.text(item1.get('filename'))
                    st.text(item1.get('score'))
                    st.text(item1.get('text'))
                #st.text(references.filename)
                # print (response.json().get('content'))
                #print (json_string)
                #st.success(f"API Response: {response.json()}")
                #st.markdown(response.json())
                #respdata = response.json().get('completion')
                #st.text(respdata.get('content'))
                #refdata = response.json().get('references')
                #refdata1=json.loads(refdata)
                #st.text(refdata)
                #for item1 in refdata:
                #    st.text(item1.get('filename'))
                #    st.text(item1.get('meta'))
                #    st.text(item1.get('id'))
                #    st.markdown(item1.get('text'))
                #st.markdown(item1.get('text'))
                #    st.success(f"API Response: {refdata1}")
                
                #st.success(f"API Response: {json_string}")
            else:
                st.error(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to API: {e}")