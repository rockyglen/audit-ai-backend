import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

# --- Configuration ---
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "compliance_audit"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_rag_chain():
    # 1. Setup the Brain (LLM)
    llm = ChatGroq(
        temperature=0,  # Strict mode for compliance
        model_name="llama-3.3-70b-versatile",
    )

    # 2. Setup the Memory Access (Retriever)
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    vector_store = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=COLLECTION_NAME,
        prefer_grpc=True,
    )

    # "k=3" means "Give me the top 3 most relevant pages"
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 3. The "System Prompt" (The Personality)
    # This tells the AI how to behave.
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

    # 4. Build the Chain
    # "Stuff" documents chain simply stuffs the retrieved text into the prompt
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain


# --- Test Function (Runs only if you execute this file directly) ---
if __name__ == "__main__":
    chain = get_rag_chain()

    # A tough question specific to NIST (not general knowledge)
    query = "What is the primary purpose of the 'Govern' function in the CSF 2.0?"

    print(f"🕵️  Auditing Query: {query} ...\n")
    response = chain.invoke({"input": query})

    print("📋 AUDIT REPORT:")
    print(response["answer"])

    # BONUS: Show sources!
    print("\n\n📄 SOURCES CITED:")
    for doc in response["context"]:
        print(f"- Page {doc.metadata.get('page', '?')}: {doc.page_content[:100]}...")
