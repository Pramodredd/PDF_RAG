from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()
from sentence_transformers import SentenceTransformer
from langchain.llms.base import LLM
from pydantic import Field
from typing import Any
# from langchain.schema import Generation, LLMResult
model = SentenceTransformer("all-MiniLM-L6-v2")

client = OpenAI(
    base_url="https://api.studio.nebius.com/v1/",
    api_key=os.getenv("NEBIUS_API_KEY"),
)

class NebiusLLM(LLM):
    client: Any = Field(exclude=True)  # exclude=True prevents Pydantic serialization issues
    model_name: str

    def __init__(self, client, model_name: str):
        # Use `super().__init__` to properly initialize BaseModel
        super().__init__(client=client, model_name=model_name)

    def _call(self, prompt: str, context: str = "", stop=None) -> str:
        # Combine the context and the original prompt into a single user message.
        # This is a standard and effective RAG pattern.
        formatted_prompt = f"""Based on the context below, please answer the question. If the answer is not in the context, say you don't know.

Context:
{context}

Question:
{prompt}"""

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions based on the provided context.",
            },
            {"role": "user", "content": formatted_prompt},
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )
        return response.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        return "nebius"
    
def get_llm():
    return NebiusLLM(client=client, model_name="mistralai/Mistral-Nemo-Instruct-2407")
