import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

# 1. Load Environment Variables
load_dotenv()

# Configuration
# This is the real government document we just downloaded
PDF_FILE_NAME = "nist_framework.pdf"
# This runs on your CPU (Free)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# The name of the folder inside Qdrant
COLLECTION_NAME = "compliance_audit"


def ingest_docs():
    # --- Check Secrets ---
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_key:
        print("❌ Error: QDRANT_URL or QDRANT_API_KEY not found in .env file.")
        return

    # --- A. Load the Document ---
    print(f"📄 Loading PDF: {PDF_FILE_NAME}...")
    try:
        loader = PyPDFLoader(PDF_FILE_NAME)
        documents = loader.load()
        print(f"   Success! Loaded {len(documents)} pages.")
    except Exception as e:
        print(f"❌ Error loading PDF: {e}")
        return

    # --- B. Split the Document (Chunking) ---
    print("✂️  Splitting text into chunks...")
    # Complex legal docs need good overlap to keep context intact
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    print(f"   Created {len(splits)} chunks to embed.")

    # --- C. Create Embeddings ---
    print(f"🧠 Initializing Embedding Model ({EMBEDDING_MODEL_NAME})...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    # --- D. Connect to Qdrant ---
    print("☁️  Connecting to Qdrant Cloud...")
    try:
        # This function does three things:
        # 1. Connects to Qdrant
        # 2. Creates the collection if it doesn't exist
        # 3. Turns text -> numbers -> uploads them
        QdrantVectorStore.from_documents(
            splits,
            embeddings,
            url=qdrant_url,
            api_key=qdrant_key,
            collection_name=COLLECTION_NAME,
            prefer_grpc=True,  # Faster data transfer
        )
        print(
            "✅ Ingestion Complete! The NIST Framework is now in your Vector Database."
        )

    except Exception as e:
        print(f"❌ Error uploading to Qdrant: {e}")


if __name__ == "__main__":
    ingest_docs()
