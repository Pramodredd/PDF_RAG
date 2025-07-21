import streamlit as st
import requests
import json # Import json for sending payload in json format

# --- Configuration ---
FASTAPI_BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{FASTAPI_BASE_URL}/upload"
RETRIEVE_ENDPOINT = f"{FASTAPI_BASE_URL}/retrieve" # New endpoint for RAG
CLEAR_DATABASE_ENDPOINT = f"{FASTAPI_BASE_URL}/clear-database"


# --- Helper Functions ---
def upload_file_to_fastapi(file, description):
    files = {"file": (file.name, file.getvalue(), file.type)} # .getvalue() for bytes content
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        error_details = response.text if 'response' in locals() and response is not None else "No response details"
        return {"error": str(e), "details": error_details}

def retrieve_answer_from_fastapi(query_text: str):
    payload = {"query": query_text} # This matches your RetrieveQuery Pydantic model
    try:
        params = {"query": query_text}

        response = requests.get(RETRIEVE_ENDPOINT, params=params) # Use GET and params
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        error_details = response.text if 'response' in locals() and response is not None else "No response details"
        return {"error": str(e), "details": error_details}
    
def clear_pinecone_database():
    try:
        response = requests.post(CLEAR_DATABASE_ENDPOINT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        error_details = response.text if 'response' in locals() and response is not None else "No response details"
        return {"error": str(e), "details": error_details}


# --- Streamlit UI ---
st.set_page_config(page_title="Document QA System", layout="centered")
st.title("📄🔍 Document Uploader & QA")

st.markdown("Upload a document, then ask a question to get an AI-generated answer based on the document's content.")

# Initialize messages for chat-like interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# File Uploader
uploaded_file = st.file_uploader("Upload a .pdf or .docx file", type=["pdf", "docx"], key="file_uploader")
# description = st.text_input("Document description (optional)", key="doc_description") # Removed if FastAPI /upload doesn't take it

# User Query Input
query_text = st.chat_input("Enter your question here...") # Using chat_input for a more natural feel

# Process logic (triggered by query_text or a button if preferred)
if query_text:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query_text})
    with st.chat_message("user"):
        st.markdown(query_text)

    # Validate query length (this validation should ideally be on backend too)
    if not (3 <= len(query_text) <= 100): # Increased max query length for realism
        st.error("Query must be between 3 and 100 characters.")
        st.session_state.messages.pop() # Remove invalid query from history
    else:
        if uploaded_file and "file_processed" not in st.session_state:
            with st.spinner("Uploading and processing document..."):
                # Pass the raw file object from Streamlit
                upload_result = upload_file_to_fastapi(uploaded_file, "N/A") # Description might not be used
                if "error" in upload_result:
                    st.error(f"Document upload failed: {upload_result['error']}")
                    if "details" in upload_result:
                        st.error(upload_result["details"])
                    st.stop() # Stop execution if upload fails
                else:
                    st.success("✅ Document uploaded and processed successfully!")
                    st.session_state.file_processed = True # Mark as processed

        if "file_processed" not in st.session_state and not uploaded_file:
            st.warning("Please upload a document first to enable Q&A.")
            st.stop()


        # Step 2: Call the retrieve endpoint to get LLM answer
        with st.spinner("Getting answer from LLM..."):
            # Call the new retrieve function
            answer_result = retrieve_answer_from_fastapi(query_text)
            
            if "error" in answer_result:
                st.error(f"Failed to get answer: {answer_result['error']}")
                if "details" in answer_result:
                    st.error(answer_result["details"])
                # Add a generic error message to chat if retrieve fails
                st.session_state.messages.append({"role": "assistant", "content": "I apologize, but I could not retrieve an answer at this time. Please try again."})
                with st.chat_message("assistant"):
                    st.markdown("I apologize, but I could not retrieve an answer at this time. Please try again.")
            else:
                llm_answer = answer_result.get("response", "No response found.")
                st.session_state.messages.append({"role": "assistant", "content": llm_answer})
                with st.chat_message("assistant"):
                    st.markdown(llm_answer)

st.sidebar.markdown("---")
st.sidebar.info("Ensure your FastAPI backend is running on `http://localhost:8000`.")

# Optional: Clear chat history button
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.session_state.pop("file_processed", None) # Also clear file processed state
    st.rerun()

if st.sidebar.button("🧹 Clear Pinecone Database"):
    with st.spinner("Clearing the Pinecone vector database..."):
        result = clear_pinecone_database()
        if "error" in result:
            st.sidebar.error(f"❌ Failed: {result['error']}")
            if "details" in result:
                st.sidebar.error(result["details"])
        else:
            st.sidebar.success("✅ Pinecone database cleared successfully!")
