import os
import json
import asyncio
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the graph AND the router logic from your engine
from rag_engine import app as audit_graph, route_query, run_chat_logic

# 1. Initialize FastAPI
app = FastAPI(
    title="AuditAI Agent API",
    description="A Streaming Agentic RAG API for NIST Compliance",
    version="2.0",
)

# 2. CORS Setup (Crucial for Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Request Model
class ChatRequest(BaseModel):
    query: str
    history: Optional[List[Dict[str, str]]] = []


# 4. The Smart Generator Logic
async def run_agent_stream(query: str):
    """
    Smart Generator:
    1. Checks Router (Chat vs Search).
    2. If Chat -> Streams static response instantly.
    3. If Search -> Streams the heavy Graph execution.
    """

    # --- STEP A: THE ROUTER CHECK ---
    # We run the router first to see if we can skip the graph
    intent = route_query(query)

    if intent == "chat":
        # Fast Path: Stream the static greeting
        response = run_chat_logic(query)
        answer_text = response["answer"]

        # Simulate token streaming so the UI animation works
        tokens = answer_text.split(" ")
        for token in tokens:
            payload = json.dumps({"type": "token", "content": token + " "})
            yield f"{payload}\n"
            await asyncio.sleep(0.05)  # Tiny delay to make it feel "alive"

        # Send empty sources
        payload = json.dumps({"type": "sources", "content": []})
        yield f"{payload}\n"
        return

    # --- STEP B: THE GRAPH PATH (Search) ---
    captured_sources = []

    # Run the LangGraph agent and listen for events
    async for event in audit_graph.astream_events({"question": query}, version="v1"):
        kind = event["event"]

        # Capture Sources from 'retrieve' node finishing
        if kind == "on_chain_end" and event["name"] == "retrieve":
            if "output" in event["data"] and event["data"]["output"]:
                docs = event["data"]["output"].get("documents", [])
                captured_sources = [
                    {
                        "page": d.metadata.get("page", 0),
                        "text": d.page_content[:200] + "...",
                    }
                    for d in docs
                ]

        # Stream Answer from 'generate' node streaming tokens
        if kind == "on_chat_model_stream":
            if event["metadata"].get("langgraph_node") == "generate":
                chunk_content = event["data"]["chunk"].content
                if chunk_content:
                    payload = json.dumps({"type": "token", "content": chunk_content})
                    yield f"{payload}\n"

    # Send Captured Sources at the very end
    if captured_sources:
        payload = json.dumps({"type": "sources", "content": captured_sources})
        yield f"{payload}\n"


# 5. The Endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        return StreamingResponse(
            run_agent_stream(request.query), media_type="application/x-ndjson"
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 6. Health Check
@app.get("/health")
def health_check():
    return {"status": "healthy", "mode": "agentic"}


if __name__ == "__main__":
    import uvicorn

    # Verify API Keys exist before starting
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Error: GROQ_API_KEY is missing!")
    else:
        print("🚀 Starting AuditAI Agent...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
