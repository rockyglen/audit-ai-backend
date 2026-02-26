import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# --- Database & Model Configs ---
EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "gemini-2.5-flash-lite"
EVAL_JUDGE_MODEL = "gemini-2.5-flash-lite"
COLLECTION_NAME = "compliance_audit"

# --- Project Base Directory ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Validation ---
if not QDRANT_URL or not QDRANT_API_KEY or not GOOGLE_API_KEY or not GROQ_API_KEY:
    raise ValueError("Missing critical API Keys in .env file")
