from pymongo import MongoClient 
from gridfs import GridFS

try:
    client = MongoClient('mongodb://localhost:27017/')
    client.admin.command('ismaster')
    print("MongoDB connection successful.")
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")
    exit()

 
db = client['pdf_rag_db']
chat_history_collection = db['chat_history']
# chunks_collection = db['chunks']
# fs = GridFS(db)
