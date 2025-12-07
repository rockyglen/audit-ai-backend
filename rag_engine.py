import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEndpointEmbeddings
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

    # 2. Setup the Memory Access (API-Based Embeddings)
    # CHANGED: We now use the API to save RAM
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2",
        task="feature-extraction",
        huggingfacehub_api_token=HF_TOKEN
    )
    
    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        prefer_grpc=True
    )
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 3. System Prompt
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

    # 4. Build Chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain