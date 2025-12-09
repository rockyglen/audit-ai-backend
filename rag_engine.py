import os
import requests
from typing import List, Literal
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.embeddings import Embeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# --- Configuration ---
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
COLLECTION_NAME = "compliance_audit"

# --- 1. The Brain (Shared) ---
llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")


# --- 2. The Router (The Traffic Cop) ---
# This decides if we need to search the database or just chat.
def route_query(query: str) -> Literal["search", "chat"]:
    system_prompt = (
        "You are a router. Your job is to classify the user's input. "
        "If the input is a greeting, pleasantry, or small talk (e.g., 'hi', 'hello', 'who are you?'), return 'chat'. "
        "If the input asks for information, rules, or compliance data, return 'search'. "
        "Return ONLY the word 'chat' or 'search'."
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", "{input}")]
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"input": query})
    return result.strip().lower()


# --- 3. The RAG Chain (For Compliance Questions) ---
def get_rag_chain(query):
    # Setup Memory
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        prefer_grpc=True,
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # Strict Audit Prompt
    system_prompt = (
        "You are a strict Compliance Auditor AI. "
        "Use the following pieces of retrieved context to answer the question. "
        "If the answer is not in the context, say 'I cannot find this in the compliance documents.' "
        "Do not invent rules."
        "\n\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))
    return chain.invoke({"input": query})


# --- 4. The Chat Chain (For Greetings) ---
def get_chat_chain(query):
    # Friendly Chat Prompt (No Context Needed)
    system_prompt = (
        "You are a helpful NIST Compliance Assistant. "
        "Reply warmly and professionally to the user's greeting. "
        "Introduce yourself briefly and ask if they need to audit any specific policies."
        "Not more than 50 words."
    )
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", "{input}")]
    )
    chain = prompt | llm | StrOutputParser()
    response_text = chain.invoke({"input": query})

    # Return structure matching RAG response, but with empty context
    return {"answer": response_text, "context": []}


# --- 5. The Main Entry Point ---
def process_query(query: str):
    # Step A: AI decides what to do
    intent = route_query(query)
    print(f"🧠 AI Router decided: {intent.upper()}")

    # Step B: Execute the right chain
    if intent == "chat":
        return get_chat_chain(query)
    else:
        return get_rag_chain(query)
