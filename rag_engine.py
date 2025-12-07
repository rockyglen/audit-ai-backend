import os
import requests
from typing import List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.embeddings import Embeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

# --- Configuration ---
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
COLLECTION_NAME = "compliance_audit"

# --- CUSTOM CLASS: Robust API Wrapper ---
class LightweightHFEmbeddings(Embeddings):
    def __init__(self, api_key, model_url):
        self.api_key = api_key
        self.api_url = model_url
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Simplified payload (No 'options' to avoid 400 errors)
        payload = {"inputs": texts}
        
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        
        # ERROR HANDLING: Print the actual error message from Hugging Face
        if response.status_code != 200:
            print(f"❌ HF API Error: {response.status_code}")
            print(f"❌ Details: {response.text}") # <--- This will show in Render logs
            response.raise_for_status()
            
        return response.json()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

def get_rag_chain():
    # 1. Setup the Brain (LLM)
    llm = ChatGroq(
        temperature=0, 
        model_name="llama-3.3-70b-versatile"
    )

    # 2. Setup the Memory (Smart Toggle)
    if os.getenv("RENDER"):
        print("☁️  Running on Render: Using Lightweight API Wrapper")
        # Switch to the standard Model URL (More reliable than Router)
        model_url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        
        embeddings = LightweightHFEmbeddings(
            api_key=HF_TOKEN,
            model_url=model_url
        )
    else:
        print("💻 Running Locally: Using CPU Embeddings")
        from langchain_huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 3. Connect to Qdrant
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        prefer_grpc=True
    )
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 4. System Prompt
    system_prompt = (
        "You are a strict Compliance Auditor AI. "
        "Use the following pieces of retrieved context to answer the question. "
        "If the answer is not in the context, say 'I cannot find this in the compliance documents.' "
        "Do not invent rules. Keep the answer concise and professional."
        "\n\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    # 5. Build Chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain