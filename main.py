import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <--- THE MISSING PIECE
from pydantic import BaseModel
from rag_engine import process_query

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = FastAPI(title="AuditAI API")

# --- CORS MIDDLEWARE (Fixes the 405/Network Error) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Your local frontend
        "https://audit-ai-frontend.vercel.app",  # Your Vercel frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------------------------------------


class QueryRequest(BaseModel):
    query: str


class Source(BaseModel):
    page: int
    text: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.post("/chat", response_model=QueryResponse)
def chat_endpoint(request: QueryRequest):
    try:
        # The 'process_query' function now handles the AI routing automatically
        response = process_query(request.query)

        sources_list = []

        # Router Logic: 'chat' intent returns empty context, so this loop will skip
        if "context" in response:
            for doc in response["context"]:
                sources_list.append(
                    Source(
                        page=doc.metadata.get("page", 0),
                        text=doc.page_content[:200] + "...",
                    )
                )

        return QueryResponse(answer=response["answer"], sources=sources_list)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
