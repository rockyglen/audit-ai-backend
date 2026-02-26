import os
import asyncio
from typing import List, Literal, TypedDict

from audit_ai.config import (
    GROQ_API_KEY, GOOGLE_API_KEY, QDRANT_URL, QDRANT_API_KEY, 
    LLM_MODEL, EMBEDDING_MODEL, COLLECTION_NAME
)

# --- LangChain & Qdrant Imports ---
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.runnables import RunnableConfig

# --- LangGraph Imports ---
from langgraph.graph import StateGraph, END

# =============================================================================
# 1. STATE DEFINITION
# =============================================================================

class GraphState(TypedDict):
    """
    Represents the state of our graph (the "Backpack").
    """
    question: str              # The user's original input
    search_query: str          # The query used for retrieval (can be rewritten)
    generation: str            # The final answer
    documents: List[Document]  # The retrieved context chunks
    grade: str                 # 'yes' or 'no' (Relevance check)
    retry_count: int           # Tracks retries

# =============================================================================
# 2. INITIALIZATION
# =============================================================================

# Initialize Components using Centralized Config
llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL,
    temperature=0,
    google_api_key=GOOGLE_API_KEY,
)

embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL, 
    google_api_key=GOOGLE_API_KEY
)

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

vector_store = QdrantVectorStore(
    client=client,
    collection_name=COLLECTION_NAME,
    embedding=embeddings,
)

# =============================================================================
# 2. DEFINE THE NODES (AGENTS)
# =============================================================================

def retrieve(state: GraphState):
    """
    Node 1: RETRIEVE
    Queries Qdrant using either the 'search_query' (if rewritten) or original 'question'.
    """
    print("---RETRIEVE NODE---")
    query = state.get("search_query") or state["question"]
    documents = vector_store.similarity_search(query, k=10)
    return {"documents": documents, "question": state["question"]}


def grade_documents(state: GraphState):
    """
    Node 2: GRADE DOCUMENTS (The Critic)
    Checks if retrieved documents are relevant.
    """
    print("---GRADE DOCUMENTS NODE---")
    question = state["question"]
    documents = state["documents"]

    prompt = ChatPromptTemplate.from_template(
        "You are a grader assessing relevance of a retrieved document to a user question. \n"
        "Here is the retrieved document: \n\n {context} \n\n"
        "Here is the user question: {question} \n"
        "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
        "Return ONLY the word 'yes' or 'no'."
    )

    chain = prompt | llm.with_config({"tags": ["grader"]}) | StrOutputParser()

    score = "no"
    for doc in documents:
        grade = chain.invoke({"question": question, "context": doc.page_content})
        if "yes" in grade.lower():
            score = "yes"
            break

    print(f"---RESULT: Documents relevant? {score.upper()}---")
    return {"grade": score}


def transform_query(state: GraphState):
    """
    Node 3: TRANSFORM QUERY (The Fixer)
    Rewrites the question to improve vector search if grading failed.
    """
    print("---TRANSFORM QUERY NODE---")
    question = state["question"]

    prompt = ChatPromptTemplate.from_template(
        "You are generating a specialized vector search query from a user question. \n"
        "The previous search for the question '{question}' failed to yield relevant results. \n"
        "Please re-phrase the question to focus on key technical terms for the NIST Cybersecurity Framework. \n"
        "Return ONLY the new query text."
    )

    chain = prompt | llm | StrOutputParser()
    better_query = chain.invoke({"question": question})
    current_retries = state.get("retry_count", 0)
    print(f"---REWRITTEN QUERY: {better_query}---")
    return {"search_query": better_query, "retry_count": current_retries + 1}


async def generate(state: GraphState, config: RunnableConfig):
    """
    Node 4: GENERATE
    Produces the final answer using retrieved context.
    """
    print("---GENERATE NODE---")
    question = state["question"]
    documents = state["documents"]

    context_text = "\n\n".join(
        [
            f"[Source: {doc.metadata.get('source_file', 'Unknown')}]\n{doc.page_content}"
            for doc in documents
        ]
    )

    prompt = ChatPromptTemplate.from_template(
        "You are a strict Compliance Auditor AI. "
        "Answer the user's question using ONLY the context provided below. "
        "When answering, refer to the specific document names (e.g., 'According to the NIST framework...' or 'The Acme Policy states...')."
        "If the documents conflict, point out the difference."
        "If the context is empty, simply state that the specific information is missing from the database."
        "\n\nContext:\n{context}\n\n"
        "Question: {question}\n"
        "Answer:"
    )

    rag_chain = prompt | llm.with_config({"tags": ["generator"]}) | StrOutputParser()

    response = await rag_chain.ainvoke(
        {"context": context_text, "question": question}, config=config
    )

    return {"generation": response}


# =============================================================================
# 3. BUILD THE GRAPH LOGIC
# =============================================================================

workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("transform_query", transform_query)

# Define Entry Point
workflow.set_entry_point("retrieve")

# Add Edges
workflow.add_edge("retrieve", "grade_documents")
workflow.add_edge("transform_query", "retrieve")

def decide_to_generate(state: GraphState):
    grade = state.get("grade")
    retries = state.get("retry_count", 0)

    if grade == "yes":
        return "generate"
    elif retries >= 3:
        return "generate"
    else:
        return "transform_query"

workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {"generate": "generate", "transform_query": "transform_query"},
)

workflow.add_edge("generate", END)

# Compile the Graph
app = workflow.compile()

# =============================================================================
# 4. PUBLIC INTERFACE (Used by API)
# =============================================================================

def process_query(user_query: str):
    """
    Helper function for non-streaming execution (e.g., for evals).
    Note: API uses astream_events directly for latency optimization.
    """
    inputs = {"question": user_query}
    try:
        final_state = asyncio.run(app.ainvoke(inputs))
        return {
            "answer": final_state["generation"],
            "context": final_state["documents"],
        }
    except Exception as e:
        print(f"Graph Error: {e}")
        return {"answer": "Error processing request.", "context": []}
