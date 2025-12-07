import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_engine import get_rag_chain

# 1. Suppress those annoying tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 2. Initialize the App
app = FastAPI(
    title="AuditAI API",
    description="A RAG system for auditing NIST compliance",
    version="1.0"
)

# 3. Define the Data Models
# This ensures the API only accepts valid JSON
class QueryRequest(BaseModel):
    query: str

class Source(BaseModel):
    page: int
    text: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]

# 4. Load the Brain (Runs once when server starts)
print("🚀 Loading RAG Engine...")
chain = get_rag_chain()
print("✅ Engine Ready!")

# 5. The Endpoint
# This is the "Door" that the frontend will knock on
@app.post("/chat", response_model=QueryResponse)
def chat_endpoint(request: QueryRequest):
    try:
        # Ask the RAG chain
        response = chain.invoke({"input": request.query})
        
        # Format the sources cleanly
        sources_list = []
        for doc in response["context"]:
            sources_list.append(
                Source(
                    page=doc.metadata.get("page", 0),
                    text=doc.page_content[:200] + "..." # Preview only
                )
            )
            
        return QueryResponse(
            answer=response["answer"], 
            sources=sources_list
        )
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# To run: uvicorn main:app --reload