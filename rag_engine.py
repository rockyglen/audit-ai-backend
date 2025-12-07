import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

# --- Configuration ---
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
COLLECTION_NAME = "compliance_audit"

def get_rag_chain():
    # 1. Setup the Brain (LLM)
    llm = ChatGroq(
        temperature=0, 
        model_name="llama-3.3-70b-versatile"
    )

    # 2. Setup the Memory (Smart Toggle)
    # If we are on Render, use the API (Save RAM) with the NEW URL.
    # If we are Local, use the CPU (Stable).
    
    if os.getenv("RENDER"):
        print("☁️  Running on Render: Using HuggingFace API (Router URL)")
        from langchain_huggingface import HuggingFaceEndpointEmbeddings
        
        # FIXED: We explicitly point to the new 2025 Router URL
        model_url = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2"
        
        embeddings = HuggingFaceEndpointEmbeddings(
            model=model_url,
            task="feature-extraction",
            huggingfacehub_api_token=HF_TOKEN,
        )
    else:
        print("💻 Running Locally: Using CPU Embeddings")
        # We import this inside the 'else' so Render doesn't need to install it
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