import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

# --- PATH LOGIC ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_FILE_NAME = os.path.join(BASE_DIR, "data", "nist_framework.pdf")
COLLECTION_NAME = "compliance_audit"


def ingest_docs():
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_key = os.getenv("QDRANT_API_KEY")

    print(f"📄 Loading PDF: {PDF_FILE_NAME}...")
    loader = PyPDFLoader(PDF_FILE_NAME)
    documents = loader.load()

    print("✂️  Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(documents)
    print(f"   Created {len(splits)} chunks.")

    # CHANGED: Use Google Embeddings
    print(f"🧠 Initializing Google Gemini Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    print("☁️  Connecting to Qdrant Cloud...")

    # Force Recreation of Collection (to fix dimension mismatch)
    QdrantVectorStore.from_documents(
        splits,
        embeddings,
        url=qdrant_url,
        api_key=qdrant_key,
        collection_name=COLLECTION_NAME,
        prefer_grpc=True,
        force_recreate=True,  # <--- IMPORTANT: Overwrites the old incompatible vectors
    )
    print("✅ Ingestion Complete! New Google vectors stored.")


if __name__ == "__main__":
    ingest_docs()
