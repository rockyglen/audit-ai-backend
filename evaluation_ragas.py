import os
import json
import pandas as pd
from datasets import Dataset
from dotenv import load_dotenv

# MODERN RAGAS IMPORTS
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import llm_factory
from ragas.embeddings import GoogleEmbeddings
from ragas.run_config import RunConfig
from google import genai

load_dotenv()


# --- FIX: THE DUCK-TYPE ADAPTER ---
class RagasGoogleEmbeddings(GoogleEmbeddings):
    """Adapts GoogleEmbeddings to the interface Ragas expects."""

    def embed_query(self, text: str):
        return self.embed_text(text)

    def embed_documents(self, texts: list[str]):
        return [self.embed_text(t) for t in texts]


def run_evaluation():
    if not os.path.exists("rag_results.json"):
        print("❌ Error: 'rag_results.json' not found.")
        return

    with open("rag_results.json", "r") as f:
        data = json.load(f)
    dataset = Dataset.from_pandas(pd.DataFrame(data))

    # 1. INITIALIZE NATIVE CLIENT
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

    # 2. CREATE STABLE LLM
    evaluator_llm = llm_factory(
        model="gemini-2.0-flash", provider="google", client=client
    )
    evaluator_llm.bypass_n = True

    # 3. USE THE ADAPTED EMBEDDINGS (Fixes the AttributeError)
    evaluator_embeddings = RagasGoogleEmbeddings(
        client=client, model="text-embedding-004"
    )

    # 4. MANUAL BINDING
    faithfulness.llm = evaluator_llm
    answer_relevancy.llm = evaluator_llm
    answer_relevancy.embeddings = evaluator_embeddings
    context_precision.llm = evaluator_llm
    context_precision.embeddings = evaluator_embeddings
    context_recall.llm = evaluator_llm

    metrics = [faithfulness, answer_relevancy, context_precision, context_recall]

    print("📊 Evaluating 50 questions (Compatibility Mode)...")

    try:
        run_config = RunConfig(timeout=180, max_workers=1)

        score = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
            run_config=run_config,
        )

        print("\n🏆 EVALUATION SUCCESSFUL!")
        print(score)
        score.to_pandas().to_csv("nist_audit_final_report.csv", index=False)
        print("✅ Report saved to 'nist_audit_final_report.csv'")

    except Exception as e:
        print(f"\n❌ Final attempt error: {e}")


if __name__ == "__main__":
    run_evaluation()
