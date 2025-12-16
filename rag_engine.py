import os
from typing import List, Literal, TypedDict
from dotenv import load_dotenv

# --- LangChain Imports ---
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# --- LangGraph Imports ---
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

# =============================================================================
# 1. INITIALIZATION & SETUP
# =============================================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GROQ_API_KEY or not QDRANT_URL or not QDRANT_API_KEY or not GOOGLE_API_KEY:
    raise ValueError("Missing API Keys in .env file")

# Initialize Llama-3 (Groq)
# We use temperature=0 for strict, reliable logic
llm = ChatGroq(
    temperature=0, model_name="llama-3.3-70b-versatile", api_key=GROQ_API_KEY
)

# Initialize Embeddings (Google Gemini 004)
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Initialize Vector DB (Qdrant)
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

vector_store = QdrantVectorStore(
    client=client,
    collection_name="compliance_audit",
    embedding=embeddings,
)

# =============================================================================
# 2. DEFINE THE GRAPH STATE
# =============================================================================


class GraphState(TypedDict):
    """
    Represents the state of our graph (the "Backpack").
    """

    question: str  # The user's original input
    search_query: str  # The query used for retrieval (can be rewritten)
    generation: str  # The final answer
    documents: List[Document]  # The retrieved context chunks
    grade: str  # 'yes' or 'no' (Relevance check)
    retry_count: int


# =============================================================================
# 3. DEFINE THE NODES (AGENTS)
# =============================================================================


def retrieve(state):
    """
    Node 1: RETRIEVE
    Queries Qdrant using either the 'search_query' (if rewritten) or original 'question'.
    """
    print("---RETRIEVE NODE---")
    # If a rewritten query exists, use it. Otherwise, use the original.
    query = state.get("search_query") or state["question"]

    # Retrieve top 3 documents
    documents = vector_store.similarity_search(query, k=3)
    return {"documents": documents, "question": state["question"]}


def grade_documents(state):
    """
    Node 2: GRADE DOCUMENTS (The Critic)
    Checks if retrieved documents are relevant.
    """
    print("---GRADE DOCUMENTS NODE---")
    question = state["question"]
    documents = state["documents"]

    # Simple Grader Prompt
    prompt = ChatPromptTemplate.from_template(
        "You are a grader assessing relevance of a retrieved document to a user question. \n"
        "Here is the retrieved document: \n\n {context} \n\n"
        "Here is the user question: {question} \n"
        "If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n"
        "Return ONLY the word 'yes' or 'no'."
    )

    chain = prompt | llm | StrOutputParser()

    # Logic: If at least ONE document is relevant, we proceed.
    # Otherwise, we assume retrieval failed.
    score = "no"
    for doc in documents:
        grade = chain.invoke({"question": question, "context": doc.page_content})
        if "yes" in grade.lower():
            score = "yes"
            break

    print(f"---RESULT: Documents relevant? {score.upper()}---")
    return {"grade": score}


def transform_query(state):
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


def generate(state):
    """
    Node 4: GENERATE (The Speaker)
    Generates the final answer using the valid context.
    """
    print("---GENERATE NODE---")
    question = state["question"]
    documents = state["documents"]

    # Context Construction
    context_text = "\n\n".join([doc.page_content for doc in documents])

    # Final Answer Prompt
    prompt = ChatPromptTemplate.from_template(
        "You are a strict Compliance Auditor AI. "
        "Answer the user's question using ONLY the context provided below. "
        "Do not apologize. Do not say 'I cannot find this'. "
        "If the context is empty, simply state that the specific information is missing from the database."
        "\n\nContext:\n{context}\n\n"
        "Question: {question}\n"
        "Answer:"
    )

    rag_chain = prompt | llm | StrOutputParser()
    response = rag_chain.invoke({"context": context_text, "question": question})

    return {"generation": response}


# =============================================================================
# 4. BUILD THE GRAPH LOGIC
# =============================================================================

workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_documents", grade_documents)
workflow.add_node("generate", generate)
workflow.add_node("transform_query", transform_query)

# Define Entry Point
workflow.set_entry_point("retrieve")

# Add Normal Edges
workflow.add_edge("retrieve", "grade_documents")
workflow.add_edge("transform_query", "retrieve")  # The loop back!


# Add Conditional Edge Logic
def decide_to_generate(state):
    print("---DECISION LOGIC---")
    grade = state.get("grade")
    retries = state.get("retry_count", 0)  # Get current count (default 0)

    if grade == "yes":
        print("---DECISION: Documents are Good -> Generate---")
        return "generate"

    # NEW: Check if we hit the limit
    elif retries >= 3:
        print("---DECISION: Max Retries Hit -> Give Up (Generate anyway)---")
        # We send it to generate, but the generator will see irrelevant docs
        # and its System Prompt will force it to say "I cannot find this".
        return "generate"

    else:
        print(f"---DECISION: Retry #{retries + 1} -> Rewrite Query---")
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
# 5. PUBLIC INTERFACE (Used by Main.py)
# =============================================================================


def route_query(query: str) -> Literal["chat", "search"]:
    """
    Fast Semantic Router to skip the heavy graph for greetings.
    """
    router_prompt = (
        "You are a router. Classify the user's input. "
        "Return 'chat' for: greetings, pleasantries, small talk, OR questions about your identity (e.g., 'who are you?', 'what can you do?'). "
        "Return 'search' for: questions seeking information, rules, definitions, or compliance data from the NIST framework. "
        "Return ONLY the word 'chat' or 'search'."
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", router_prompt), ("human", "{input}")]
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"input": query}).strip().lower()


def run_chat_logic(query: str):
    return {
        "answer": "I am AuditAI, an autonomous NIST Compliance Engine. I can verify rules, definitions, and functions from the CSF 2.0 framework.",
        "context": [],
    }


def process_query(user_query: str):
    """
    Main function called by FastAPI.
    1. Checks Router.
    2. If 'search', runs the Agent Graph.
    """
    # 1. Fast Route Check
    intent = route_query(user_query)
    print(f"---ROUTER: {intent.upper()}---")

    if intent == "chat":
        return run_chat_logic(user_query)

    # 2. Run the Agent Graph
    inputs = {"question": user_query}

    # Invoke the graph
    try:
        final_state = app.invoke(inputs)
        return {
            "answer": final_state["generation"],
            "context": final_state["documents"],
        }
    except Exception as e:
        # Fallback if graph fails
        print(f"Graph Error: {e}")
        return {
            "answer": "I encountered an error while processing your request internally.",
            "context": [],
        }
