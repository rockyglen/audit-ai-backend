import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <--- CRITICAL IMPORT
from pydantic import BaseModel
from rag_engine import get_rag_chain

# 1. Suppress those annoying tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 2. Initialize the App
app = FastAPI(
    title="AuditAI API",
    description="A RAG system for auditing NIST compliance",
    version="1.0",
)

# --- 3. ADD CORS MIDDLEWARE (The Fix) ---
# This tells the server: "It is okay to accept requests from localhost:3000"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Your local frontend
        "https://audit-ai-frontend.vercel.app",  # Your future Vercel deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, GET, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)
# ----------------------------------------


# 4. Define the Data Models
class QueryRequest(BaseModel):
    query: str


class Source(BaseModel):
    page: int
    text: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


# 5. Load the Brain (Runs once when server starts)
print("🚀 Loading RAG Engine...")
chain = get_rag_chain()
print("✅ Engine Ready!")


# 6. The Endpoint
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
                    text=doc.page_content[:200] + "...",  # Preview only
                )
            )

        return QueryResponse(answer=response["answer"], sources=sources_list)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
