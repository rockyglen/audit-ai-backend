# 🤖 AuditAI: Autonomous Agentic RAG for NIST Compliance

[![Live Demo](https://img.shields.io/badge/Demo-Live-green?style=for-the-badge)](https://audit-ai-frontend-pi.vercel.app)

AuditAI is a production-grade **Agentic RAG** system designed to audit internal organizational policies against the **NIST Cybersecurity Framework (CSF 2.0)**. 

Unlike standard RAG pipelines, AuditAI utilizes a **Self-Correcting Graph Architecture** to ensure 100% faithfulness, strictly enforced reasoning, and dynamic retrieval optimization.

---

## 🏗️ Advanced Architecture: The "Agentic" Core

AuditAI is powered by a directed acyclic graph (DAG) orchestrated via **LangGraph**. This allows the system to move beyond "one-shot" retrieval into a multi-step reasoning process.

### 1. The Self-Correction Loop
The system implements a **CRAG (Corrective RAG)** pattern to handle low-quality retrieval:

```mermaid
graph TD
    A[User Query] --> B{Semantic Router}
    B -- Small Talk/ID --> C[Direct Response]
    B -- Compliance Query --> D[Retrieve from Qdrant]
    D --> E[Document Grader]
    E -- Relevant Docs Found --> F[RAG Generation]
    E -- No Relevant Docs --> G[Query Transformer]
    G -- Rewritten Query --> D
    F --> H[Citations & Streaming]
    C --> H
```

*   **Semantic Router**: A fast-path LLM classifier that identifies intent. It bypasses the heavy graph for greetings or identity questions, reducing latency and cost.
*   **Document Grader**: Evaluates retrieved chunks for semantic relevance to the query. 
*   **Query Transformer**: If the grader lacks sufficient context, this node re-phrases the user's question into a more optimized search query for vector retrieval, triggering a loop-back.

### 2. Hallucination Control & Citations
AuditAI implements a "Strict Evidence" policy:
*   **Page-Level Citations**: Every claim is mapped back to specific PDF page numbers and document names.
*   **Refusal-Aware Suppression**: If the model determines (based on cross-referencing) that the answer is missing from the database, the backend **dynamically suppresses** citation cards to prevent misleading the user with irrelevant "sources".

---

## 🧠 AI Engineering Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Orchestration** | LangGraph | Complex state management and cyclic loops (Self-Correction). |
| **LLM** | Llama-3.3 70B (Groq) | Ultra-low latency inference with high reasoning capabilities. |
| **Embeddings** | Google Gemini `text-embedding-004` | State-of-the-art semantic density for technical compliance text. |
| **Vector DB** | Qdrant Cloud | High-performance vector search with metadata filtering support. |
| **Performance** | FastAPI (Async) | Supports Server-Sent Events (SSE) for real-time token streaming. |

---

## 📊 Evaluation Framework (RAGAS)

To ensure production stability, the system is evaluated using the **RAGAS** (RAG Assessment Series) framework.

### Key Metrics Tracked:
1.  **Faithfulness**: Measures if the answer is derived strictly from the retrieved context (Zero Hallucination).
2.  **Answer Relevancy**: Assesses how well the response addresses the user's intent.
3.  **Context Precision**: Evaluates the signal-to-noise ratio in retrieved chunks.
4.  **Context Recall**: Checks if all necessary information to answer the question was actually retrieved.

### Engineering Challenge: Custom LLM Wrappers
The evaluation suite includes a **Custom Groq Wrapper** to handle API limitations (like the `n=1` constraint), allowing RAGAS to run "LLM-as-a-judge" simulations reliably on top of Groq's high-speed infrastructure.

---

## 📂 Modular Project Structure

```text
audit-ai-backend/
├── src/audit_ai/
│   ├── api/            # FastAPI entry points & SSE streaming logic
│   ├── core/           # LangGraph state machine & RAG nodes
│   └── data/           # PDF processing & vector ingestion pipeline
├── scripts/            # Data collection & utility wrappers
├── evals/              # RAGAS evaluation suite & test datasets
├── data/               # Raw NIST PDF documents
└── Dockerfile          # Multi-stage production build
```

---

## 🚀 Getting Started

### Installation
1.  **Install dependencies** using [uv](https://github.com/astral-sh/uv):
    ```bash
    uv sync
    ```
2.  **Setup Environment**:
    ```bash
    cp .env.example .env
    ```

### Execution
*   **Run Backend**: 
    ```bash
    export PYTHONPATH=$PYTHONPATH:$(pwd)/src
    uv run python src/audit_ai/api/main.py
    ```
*   **Run Evaluator**:
    ```bash
    export PYTHONPATH=$PYTHONPATH:$(pwd)/src
    uv run python evals/ragas_eval.py
    ```

---

## 🛠️ Deployment

- **Containerization**: Optimized with multi-stage Docker builds.
- **CI/CD**: Configured for Render/Vercel with automatic health checks.
