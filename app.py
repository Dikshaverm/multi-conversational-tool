# import streamlit as st
# import requests
# import tempfile
# import json
# import os
# import base64
# from pydub import AudioSegment
# from io import BytesIO
# import whisper
#
# # Load Whisper model once
# @st.cache_resource
# def load_whisper_model():
#     return whisper.load_model("base")
#
# whisper_model = load_whisper_model()
#
# # Backend FastAPI server URL
# FASTAPI_URL = "http://localhost:8081"
#
# # Function to transcribe audio using Whisper
# def transcribe_audio(file_bytes, file_ext):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as temp_audio:
#         temp_audio.write(file_bytes)
#         temp_audio_path = temp_audio.name
#
#     result = whisper_model.transcribe(temp_audio_path)
#     return result["text"]
#
# # Function to call the RAG WebSocket API
# # def run_rag(question, namespace="default", language="en", chat_context=[]):
# #     import websocket
# #     ws = websocket.create_connection(f"{FASTAPI_URL}/ws/run_rag")
# #     payload = json.dumps({
# #         "language": language,
# #         "chat_context": chat_context,
# #         "namespace": namespace,
# #         "question": question
# #     })
# #     ws.send(payload)
# #     response = ws.recv()
# #     ws.close()
# #     return json.loads(response)
#
# # Function to call the Agent API
# def run_agents(query, thread_id):
#     response = requests.get(f"{FASTAPI_URL}/run_agents", params={"query": query, "thread_id": thread_id})
#     return response.json()
#
# # Streamlit App
# st.set_page_config(page_title="Voice-Enabled Chatbot", layout="wide")
# st.title("🎙️ Voice-Enabled Chatbot")
#
# mode = st.sidebar.radio("Select Input Mode:", ["Text", "Voice"])
# query = ""
#
# if mode == "Text":
#     query = st.text_input("Enter your query:")
#
# elif mode == "Voice":
#     audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])
#     if audio_file is not None:
#         file_bytes = audio_file.read()
#         file_ext = audio_file.name.split(".")[-1]
#         with st.spinner("Transcribing using Whisper model..."):
#             query = transcribe_audio(file_bytes, file_ext)
#         st.success("Transcription complete!")
#         st.write("**Transcribed Text:**", query)
#
# # Process input
# if st.button("Get Response") and query:
#     with st.spinner("Running agent-based reasoning..."):
#         response = run_agents(query, thread_id="1234")
#         st.write("### Response:")
#         st.write(response.get("result", "No response received"))


import streamlit as st
import requests
import json

# Backend FastAPI server URL
FASTAPI_URL = "http://localhost:8081"


# Function to call the Agent API
def run_agents(query, thread_id):
    response = requests.get(f"{FASTAPI_URL}/run_agents", params={"query": query, "thread_id": thread_id})
    return response.json()

# Streamlit App
st.set_page_config(page_title="Voice-Enabled Chatbot", layout="wide")
st.title("💬 Chatbot Interface")

mode = st.sidebar.radio("Select Input Mode:", ["Text"], index=0)
query = ""

if mode == "Text":
    query = st.text_input("Enter your query:")

# Voice upload section removed for this version

# Process input
if st.button("Get Response") and query:
    with st.spinner("Running agent-based reasoning..."):
        response = run_agents(query, thread_id="1234")
        st.write("### Response:")
        st.write(response.get("result", "No response received"))
