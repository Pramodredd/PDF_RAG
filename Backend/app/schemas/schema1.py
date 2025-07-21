from pydantic import BaseModel, Field ,constr
from typing import List

class QueryRequest(BaseModel):
    text_query: constr(min_length=3, max_length=200)# type: ignore

class RetrieveQuery(BaseModel):
    query: constr(min_length=3, max_length=200) # type: ignore
    
class QueryResponse(BaseModel):
    query: str
    results: List[str]

class LLMResponse(BaseModel):
    response: str