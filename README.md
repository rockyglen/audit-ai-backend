# AuditAI Backend API

The core intelligence engine for **AuditAI**—an autonomous **Agentic RAG** system designed to audit internal policies against the **NIST Cybersecurity Framework (CSF 2.0)**.

This FastAPI application orchestrates a directed graph workflow using **LangGraph** to route queries, retrieve semantic contexts via **Qdrant**, and generate hallucination-free responses using **Llama-3 (via Groq)**.

## ⚡ Key Capabilities
* **Agentic Workflow:** Intelligently routes user intent between casual conversation and deep compliance search.
* **Semantic Retrieval:** Chunks and embeds NIST PDF documents using Google Gemini embeddings (`text-embedding-004`).
* **Zero Hallucinations:** Strictly enforces page-level citations; refuses to answer off-topic queries.
* **Smart Filtering:** Dynamically suppresses citation cards if the model determines information is missing.
* **Real-time Streaming:** Asynchronous token streaming via Server-Sent Events (SSE).

## 🛠️ Tech Stack
* **Language:** Python 3.11
* **API Framework:** FastAPI
* **LLM:** Llama-3.3 70B (via Groq)
* **Vector Database:** Qdrant
* **Orchestration:** LangGraph & LangChain
