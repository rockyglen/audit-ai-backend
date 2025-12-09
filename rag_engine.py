import os
from typing import Literal
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
COLLECTION_NAME = "compliance_audit"

# --- Shared Brain ---
llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")


# --- 1. The Router (Decides: Chat vs Search) ---
def route_query(query: str) -> Literal["chat", "search"]:
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


# --- 2. The Chat Chain (No Sources) ---
def run_chat_logic(query: str):
    chat_prompt = (
        "You are a friendly NIST Compliance Assistant. "
        "Respond politely to the user's greeting. "
        "Do NOT cite sources. Just offer your help with auditing."
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", chat_prompt), ("human", "{input}")]
    )
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"input": query})
    return {"answer": answer, "context": []}  # Empty context = No sources


# --- 3. The RAG Chain (With Sources) ---
def run_rag_logic(query: str):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        prefer_grpc=True,
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # PROMPT FIX: Removed the negative constraint trigger that caused the "I cannot find..." bug
    rag_prompt = (
        "You are a strict Compliance Auditor AI. "
        "Answer the question based ONLY on the following context. "
        "Directly state the facts found in the text. "
        "\n\nContext:\n{context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", rag_prompt), ("human", "{input}")]
    )
    chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))
    return chain.invoke({"input": query})


# --- Main Entry Point ---
def process_query(query: str):
    intent = route_query(query)
    print(f"🧠 AI Router Decision: {intent.upper()}")

    if "chat" in intent:
        return run_chat_logic(query)
    else:
        return run_rag_logic(query)
