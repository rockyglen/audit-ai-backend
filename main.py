import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_engine import get_rag_chain

os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = FastAPI(title="AuditAI API")

# CORS Setup
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


print("🚀 Loading RAG Engine...")
chain = get_rag_chain()
print("✅ Engine Ready!")


@app.post("/chat", response_model=QueryResponse)
def chat_endpoint(request: QueryRequest):
    # --- LOGIC CHANGE: THE GREETING TRAP ---
    # If the user just says "hi", don't waste AI power searching for documents.
    # Return an instant response with NO sources.
    greetings = ["hi", "hello", "hey", "greetings", "good morning", "good evening"]
    cleaned_query = request.query.strip().lower().replace("!", "").replace(".", "")

    if cleaned_query in greetings:
        return QueryResponse(
            answer="Hello! I am your NIST Compliance Auditor. I can help you navigate security frameworks, risk management rules, and governance policies. What would you like to check?",
            sources=[],  # Force empty sources
        )
    # ---------------------------------------

    try:
        response = chain.invoke({"input": request.query})

        sources_list = []

        # Only add sources if the AI actually found an answer (filtering out short "I don't know" responses)
        # This keeps the UI clean if the AI just apologizes.
        if "I cannot find this" not in response["answer"]:
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
