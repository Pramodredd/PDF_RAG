import streamlit as st
import requests

FASTAPI_BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{FASTAPI_BASE_URL}/upload"
RETRIEVE_ENDPOINT = f"{FASTAPI_BASE_URL}/retrieve"
CLEAR_DATABASE_ENDPOINT = f"{FASTAPI_BASE_URL}/clear-database"
CONVERSATION_ENDPOINT = f"{FASTAPI_BASE_URL}/conversation"

def create_new_conversation_in_backend():
    try:
        response = requests.post(CONVERSATION_ENDPOINT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def get_latest_conversation():
    try:
        response = requests.get(CONVERSATION_ENDPOINT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def upload_file_to_fastapi(file, description):
    files = {"file": (file.name, file.getvalue(), file.type)}
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        error_details = response.text if 'response' in locals() and response is not None else "No response details"
        return {"error": str(e), "details": error_details}

def retrieve_answer_from_fastapi(query_text: str, convo_id: str):
    try:
        params = {"query": query_text, "convo_id": convo_id}
        response = requests.get(RETRIEVE_ENDPOINT, params=params)
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

st.set_page_config(page_title="Document QA System", layout="centered")
st.title("📄🔍 Document Uploader & QA")

def get_all_conversations_from_backend():
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/conversations")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.sidebar.error(f"Error fetching conversations: {e}")
        return []
    
# Add this function with your other API calls
def delete_conversation_from_backend(convo_id: str):
    try:
        response = requests.delete(f"{CONVERSATION_ENDPOINT}/{convo_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.sidebar.error("Delete failed.")
        return None
    
st.sidebar.title("Conversations")

# --- Sidebar ---
# This section now runs on every script execution

# Button to start a new conversation is always available
if st.sidebar.button("➕ New Conversation"):
    result = create_new_conversation_in_backend()
    if "id" in result:
        st.session_state.active_conversation_id = result["id"]
        st.session_state.messages = []
        st.session_state.pop("file_processed", None) 
        st.rerun()

st.sidebar.markdown("---")

# Display the list of existing conversations
all_conversations = get_all_conversations_from_backend()
# This is the updated loop in your sidebar
if all_conversations:
    st.sidebar.markdown("##### Previous Chats")
    for convo in all_conversations:
        created_at_str = convo.get("created_at", "No date")
        try:
            from dateutil.parser import parse
            label_date = parse(created_at_str).strftime("%b %d, %H:%M")
        except:
            label_date = "Unknown Date"
        
        convo_id = convo["id"]
        
        # Create two columns: one for the conversation label, one for the delete button
        col1, col2 = st.sidebar.columns([4, 1])

        # Column 1: The button to load the conversation
        with col1:
            if st.button(label_date, key=f"load_{convo_id}", use_container_width=True):
                response = requests.get(f"{CONVERSATION_ENDPOINT}?convo_id={convo_id}")
                if response.status_code == 200:
                    # (Your existing logic to load the conversation)
                    full_convo = response.json()
                    st.session_state.active_conversation_id = full_convo["id"]
                    st.session_state.messages = full_convo.get("messages", [])
                    st.session_state.pop("file_processed", None)
                    st.rerun()

        # Column 2: The delete button
        with col2:
            if st.button("🗑️", key=f"delete_{convo_id}", use_container_width=True):
                delete_conversation_from_backend(convo_id)
                # If the deleted conversation was the active one, create a new one
                if st.session_state.active_conversation_id == convo_id:
                    st.session_state.clear() # Clear session to start fresh
                st.rerun() # Refresh the sidebar to show the conversation is gone
# --- Initial Setup for a new session ---
# This block now automatically loads the latest or creates a new conversation
if "active_conversation_id" not in st.session_state:
    if all_conversations:
        # If conversations exist, load the latest one
        latest_convo = all_conversations[0] # The list is sorted by most recent
        st.session_state.active_conversation_id = latest_convo["id"]
        
        # Fetch the full details of the latest conversation
        response = requests.get(f"{CONVERSATION_ENDPOINT}?convo_id={latest_convo['id']}")
        if response.status_code == 200:
            st.session_state.messages = response.json().get("messages", [])
        else:
            st.session_state.messages = [] # Fallback to empty
    else:
        # If no conversations exist, create the very first one
        result = create_new_conversation_in_backend()
        if "id" in result:
            st.session_state.active_conversation_id = result["id"]
            st.session_state.messages = []
    
    # Rerun once at the end of the initial setup
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


# --- File Uploader ---
with st.container():
    uploaded_file = st.file_uploader(
        "Upload a .pdf or .docx file", type=["pdf", "docx"], key="file_uploader"
    )

# --- File Upload Logic ---
if uploaded_file and "file_processed" not in st.session_state:
    with st.spinner("Uploading and processing document..."):
        upload_result = upload_file_to_fastapi(uploaded_file, "N/A")
        if "error" in upload_result:
            st.error(f"Document upload failed: {upload_result['error']}")
            if "details" in upload_result:
                st.error(upload_result["details"])
            st.stop()
        else:
            st.success("✅ Document uploaded and processed successfully!")
            st.session_state.file_processed = True

if "file_processed" not in st.session_state:
    st.info("Please upload a document to enable Q&A.")
    st.stop()

# --- Main Chat UI ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

query_text = st.chat_input("Enter your question here...")

if query_text:
    st.session_state.messages.append({"role": "user", "content": query_text})
    with st.chat_message("user"):
        st.markdown(query_text)

    if not (3 <= len(query_text) <= 100):
        st.error("Query must be between 3 and 100 characters.")
        st.session_state.messages.pop()
    else:
        with st.spinner("Getting answer from LLM..."):
            answer_result = retrieve_answer_from_fastapi(query_text, st.session_state.active_conversation_id)
            if "error" in answer_result:
                st.error(f"Failed to get answer: {answer_result['error']}")
                if "details" in answer_result:
                    st.error(answer_result["details"])
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "I apologize, but I could not retrieve an answer at this time. Please try again."
                })
                with st.chat_message("assistant"):
                    st.markdown("I apologize, but I could not retrieve an answer at this time. Please try again.")
            else:
                llm_answer = answer_result.get("response", "No response found.")
                st.session_state.messages.append({"role": "assistant", "content": llm_answer})
                with st.chat_message("assistant"):
                    st.markdown(llm_answer)

