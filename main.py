import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_engine import process_query  # <--- Changed Import

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = FastAPI(title="AuditAI API")

# CORS (Keep your specific origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://audit-ai-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        # Use the new Smart Router function
        response = process_query(request.query)

        sources_list = []

        # Only process sources if they exist (The Router ensures 'chat' returns [])
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
        raise HTTPException(status_code=500, detail="Internal Server Error")
