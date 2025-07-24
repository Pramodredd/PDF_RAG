from pymongo.collection import Collection
from bson.objectid import ObjectId
from typing import List , IO, Union , Optional , Literal,Dict,Any
from datetime import datetime
from app.db.mongo import chat_history_collection

def create_conversation() -> str:
    """
    Creates a new conversation document and returns its convo_id.
    Returns:
        The string representation of the new conversation's ObjectId.
    """
    doc = {
        "created_at": datetime.now(),
    }
    result = chat_history_collection.insert_one(doc)
    return str(result.inserted_id)

def get_latest_conversation() -> Optional[Dict[str, Any]]:
    """
    Retrieves the most recent conversation document.
    Returns:
        The latest conversation document or None if no conversations exist.
    """
    return chat_history_collection.find_one(sort=[("created_at", -1)])

def store_user_message(convo_id: str, content: str, timestamp: datetime) -> ObjectId:
    """
    Stores a user message in the conversation document's messages array.
    Args:
        convo_id: The conversation identifier.
        content: The user's message text.
        timestamp: The message timestamp (UTC).
    Returns:
        The ObjectId of the inserted message.
    """
    message = {
        "_id": ObjectId(),
        "role": "user",
        "content": content,
        "timestamp": timestamp
    }
    chat_history_collection.update_one(
        {"_id": ObjectId(convo_id)},
        {"$push": {"messages": message}}
    )
    return message["_id"]

def store_bot_reply(convo_id: str, content: str, timestamp: datetime) -> ObjectId:
    """
    Stores a bot reply in the conversation document's messages array.
    Args:
        convo_id: The conversation identifier.
        content: The bot's reply text.
        timestamp: The reply timestamp (UTC).
    Returns:
        The ObjectId of the inserted message.
    """
    message = {
        "_id": ObjectId(),
        "role": "bot",
        "content": content,
        "timestamp": timestamp
    }
    chat_history_collection.update_one(
        {"_id": ObjectId(convo_id)},
        {"$push": {"messages": message}}
    )
    return message["_id"]


