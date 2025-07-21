
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
from app.Function.chunking import query_chunks, convert_document, chunk_document, embed_store_chunks
from typing import List

# Assuming these are correctly imported and initialized
from app.db.pinecone import pinecone
from app.model.model import get_llm # We only need the get_llm function
from app.schemas.schema1 import QueryRequest, RetrieveQuery, QueryResponse, LLMResponse

router = APIRouter()

@router.get("/")
async def read_root():
    """Root endpoint for the API."""
    return {"message": "Welcome to the RAG API Backend!"}

@router.post("/query", response_model=QueryResponse)
async def handle_query(payload: QueryRequest):
    """
    Queries the vector database for relevant chunks based on a text query,
    without involving the LLM.
    """
    try:
        results = query_chunks(payload.text_query)
        
        if not isinstance(results, list) or not all(isinstance(item, str) for item in results):
            raise HTTPException(status_code=500, detail="Internal error: query_chunks did not return a list of strings.")

        return {"query": payload.text_query, "results": results}
    except Exception as e:
        print(f"Error in /query endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chunks from the database.")


ALLOWED_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
MAX_FILE_SIZE_MB = 50

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles file uploads, validates them, converts them to text,
    chunks the text, and stores the embeddings in Pinecone.
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE_MB} MB limit.")

    # Create a temporary directory if it doesn't exist
    temp_dir = Path("./temp_uploads")
    temp_dir.mkdir(exist_ok=True)
    
    suffix = Path(file.filename).suffix
    
    # Use a context manager for the temporary file to ensure it's handled safely
    with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=suffix) as tmp:
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    try:
        print(f"Processing temporary file: {tmp_path}")
        document_text = convert_document(str(tmp_path))
        chunks = chunk_document(document_text)
        embed_store_chunks(chunks)
        return {"message": f"Document '{file.filename}' processed successfully. {len(chunks)} chunks were stored."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred while processing the document: {e}")
    finally:
        # Ensure the temporary file is always removed
        print(f"Cleaning up temporary file: {tmp_path}")
        os.remove(tmp_path)

@router.get("/retrieve", response_model=LLMResponse)
async def fetch_response(payload: RetrieveQuery = Depends()):
    """
    Retrieves relevant context from the database, passes it to the LLM with the user's query,
    and returns the generated response.
    """
    query = payload.query
    
    try:
        # 1. Retrieve relevant context from the vector database
        relevant_chunks = query_chunks(query)
        context = "\n".join(relevant_chunks)
        
        # If no context is found, we can optionally short-circuit
        if not context.strip():
            return {"response": "I could not find any relevant information in the uploaded documents to answer your question."}

        # 2. Get the initialized LLM
        llm = get_llm()

        # 3. Prepare the final prompt for the LLM
        final_prompt = (
            f"You are a helpful assistant. Please provide a concise answer to the user's question "
            f"based ONLY on the following context. If the answer is not in the context, "
            f"state that you cannot find an answer in the provided documents.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}"
        )

        # Use the modern .invoke() method, which is the correct way.
        llm_response = llm.invoke(final_prompt)
        
        # 4. Return the response.
        # No need to parse the response here; the LLM class should return a clean string.
        return {"response": llm_response}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during LLM inference: {e}")

@router.post("/clear-database")
async def clear_database():
    """
    Clears all vectors from the Pinecone index. Use with extreme caution!
    """
    try:
        print("Received request to clear entire Pinecone index.")
        # Assuming your pinecone object has an index attached to it
        # The exact method might vary based on your pinecone client version
        pinecone.delete(delete_all=True)
        print("Pinecone index successfully cleared.")
        return JSONResponse(status_code=200, content={"message": "Pinecone database cleared successfully."})
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to clear Pinecone database: {e}")
