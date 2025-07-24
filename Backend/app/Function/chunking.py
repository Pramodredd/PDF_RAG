
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
import uuid
from fastapi import HTTPException
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.db.pinecone import pinecone  # Assuming pinecone is already initialized
from app.model.model import model  # SentenceTransformer model (shared)


tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

import fitz  # PyMuPDF

def convert_document(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz).
    """
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text


def chunk_document(text: str, max_tokens=512) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_tokens,
        chunk_overlap=50,
    )
    chunks = splitter.split_text(text)
    return [chunk for chunk in chunks if is_within_token_limit(chunk, max_tokens)]

def is_within_token_limit(text, max_tokens=512):
    tokens = tokenizer.encode(text, add_special_tokens=False)
    return len(tokens) <= max_tokens

def embed_store_chunks(chunks):
    for chunk in chunks:
        vector = model.encode(chunk)
        pinecone.upsert(vectors=[
            {
                "id": str(uuid.uuid4()),
                "values": vector.tolist(),  # Pinecone expects list, not np.ndarray
                "metadata": {"text": chunk}
            }
        ])


from typing import List # Important for type hinting

def query_chunks(query_text: str) -> List[str]:
    """
    Queries the Pinecone index with the given text and returns a list of
    the text content from the relevant chunks.
    """
    if not query_text:
        return [] # Handle empty query gracefully

    try:
        vector = model.encode(query_text) # Assuming 'model' is your embedding model
        
        # Perform the Pinecone query
        results = pinecone.query(
            vector=vector.tolist(),
            top_k=2, # You might want to make top_k configurable
            include_metadata=True
        )

        # Extract the text content from the metadata of each match
        # Assuming your chunk text is stored under the 'text' key in metadata
        relevant_texts = []
        for match in results.matches:
            if 'text' in match.metadata:
                relevant_texts.append(match.metadata['text'])


        return relevant_texts # This will now be a List[str]

    except Exception as e:
        # Log the error for debugging
        import traceback
        traceback.print_exc()
        print(f"Error in query_chunks: {e}")
        # Re-raise or return an empty list depending on desired error handling
        raise HTTPException(status_code=500, detail=f"Failed to query chunks: {e}")
    

