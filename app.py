# import streamlit as st
# import os
#
# from domains.injestion.routes import injest_doc
# from domains.agents.routes import react_orchestrator
# from domains.retreival.routes import run_rag
#
# st.header("Multi Conversational Tool")
# st.markdown("---")
#
# # Set the page title and layout
# # This sets the title of the page and the layout
#
#
# def upload_and_deleted():
#     """
#     Uploads a file to the server and deletes it after processing.
#     """
#     uploaded_file = st.file_uploader("Upload a file", type=["pdf", "txt", "docx"])
#     if uploaded_file is not None:
#         # Save the file to a temporary location
#         temp_file_path = os.path.join("temp", uploaded_file.name)
#         with open(temp_file_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())
#         st.success("File uploaded successfully!")
#
#         return temp_file_path
#
#         # # Delete the file after processing
#         # os.remove(temp_file_path)
#         # st.success("File deleted successfully!")
#         # # Set the page title and layout
#         # st.set_page_config(
#         #     page_title="Multi Conversational Tool",
#         #     page_layout="wide",
#         #     initial_sidebar_state="expanded",
#         #     layout="centered",
#         # )
#
# st.set_page_config(
#     page_title="Multi Conversational Tool",
#     initial_sidebar_state="expanded",
#     layout="centered",
# )
#
# # Set the page title and layout
# st.title("Multi Conversational Tool")
#
# upload_and_deleted()
#
#

# app.py
import streamlit as st
import os
from pathlib import Path
import uuid
from dotenv import load_dotenv
from typing import Optional
import time
from datetime import datetime

load_dotenv()

from domains.injestion.models import InjestRequestDto
from domains.injestion.routes import injest_doc
from domains.agents.routes import react_orchestrator
from domains.retreival.routes import run_rag
from pathlib import Path

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'chat_mode' not in st.session_state:
    st.session_state.chat_mode = 'agent'  # or 'streaming'
if 'messages' not in st.session_state:
    st.session_state.messages = []


def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Simplified login logic - replace with proper authentication
        if username == "admin" and password == "admin":
            st.session_state.user = username
            st.session_state.role = "admin"
            st.rerun()
        elif username == "user" and password == "user":
            st.session_state.user = username
            st.session_state.role = "user"
            st.rerun()
        else:
            st.error("Invalid credentials")


def upload_files():
    uploaded_files = st.file_uploader("Upload documents",
                                      type=["pdf", "txt", "docx"],
                                      accept_multiple_files=True)

    if uploaded_files:
        for file in uploaded_files:
            file_path = Path("temp") / file.name
            file_path.parent.mkdir(exist_ok=True)

            # Save file
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            # Prepare ingestion request
            request = InjestRequestDto(
                request_id=int(uuid.uuid4()),
                pre_signed_url=Path(file_path),
                file_name=file.name,
                original_file_name=file.name,
                file_type=file.name.split('.')[-1],
                namespace=st.session_state.user,  # Use username as namespace
                response_data_api_path="/status"  # Placeholder status endpoint
            )

            try:
                # Attempt ingestion
                response = injest_doc(request=request, background_tasks=None)

                if response:
                    st.success(f"File {file.name} uploaded and ingestion started")

                    # Poll for ingestion status
                    max_retries = 3
                    retry_count = 0

                    while retry_count < max_retries:
                        time.sleep(2)  # Wait before checking status
                        # Replace with actual status check
                        ingestion_complete = True  # Placeholder

                        if ingestion_complete:
                            break
                        retry_count += 1

                    if retry_count == max_retries:
                        st.warning(f"Ingestion status unknown for {file.name}")

            except Exception as e:
                st.error(f"Failed to ingest {file.name}: {str(e)}")
                # Implement retry logic here

            finally:
                # Cleanup temp file
                if file_path.exists():
                    file_path.unlink()


def chat_interface():
    st.sidebar.title("Chat Settings")
    st.session_state.chat_mode = st.sidebar.selectbox(
        "Select Chat Mode",
        ["Agent-based RAG", "Streaming RAG"]
    )

    # Chat interface
    st.title("Chat with Documents")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            if st.session_state.chat_mode == "Agent-based RAG":
                response = react_orchestrator(prompt, str(uuid.uuid4()))
            else:
                response = run_rag(
                    question=prompt,
                    language="en",
                    namespace=st.session_state.user
                )

            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Error processing request: {str(e)}")


def main():
    st.set_page_config(
        page_title="Document Chat System",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if not st.session_state.user:
        login()
    else:
        st.sidebar.title(f"Welcome {st.session_state.user}")
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

        tab1, tab2 = st.tabs(["Upload Documents", "Chat"])

        with tab1:
            upload_files()

        with tab2:
            chat_interface()


if __name__ == "__main__":
    main()
