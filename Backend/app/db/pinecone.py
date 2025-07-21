from pinecone import Pinecone
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get values from environment
api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")  # corrected key name

# Validate values
if not api_key:
    raise ValueError("PINECONE_API_KEY environment variable is not set.")
if not index_name:
    raise ValueError("PINECONE_INDEX_NAME environment variable is not set.")

# Initialize Pinecone
pc = Pinecone(api_key=api_key)

# Get or create the index
index = pc.Index(index_name)

# Export for use
pinecone = index
