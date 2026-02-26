import sys
import os

# --- PATH HACK (Industrial Standard for standalone scripts) ---
# Adds the 'src' directory to the path so we can import 'audit_ai'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

import csv
import json
import time
import pandas as pd
from audit_ai.engine import process_query
from dotenv import load_dotenv

load_dotenv()


def load_test_csv(file_path):
    rows = []
    if not os.path.exists(file_path):
        print(f"❌ Error: '{file_path}' not found.")
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        f.readline()  # skip header
        reader = csv.reader(f)
        for line in reader:
            if line:
                # Clean prefix from the first column
                q = line[0].replace("", "").strip('"').strip()
                rows.append({"question": q, "ground_truth": line[1]})
    return rows


# --- PATH LOGIC (Flattened) ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILE = os.path.join(CURRENT_DIR, "test.csv")
RESULTS_FILE = os.path.join(CURRENT_DIR, "rag_results.json")


def collect_answers():
    test_questions = load_test_csv(TEST_FILE)
    collected_data = []

    print(f"🚀 Starting collection for {len(test_questions)} questions...")

    for i, item in enumerate(test_questions):
        print(f"[{i+1}/50] Processing: {item['question'][:50]}...")

        # Run your actual RAG system
        response = process_query(item["question"])

        collected_data.append(
            {
                "question": item["question"],
                "answer": str(response.get("answer", "")),
                "contexts": [
                    str(doc.page_content) for doc in response.get("context", [])
                ],
                "ground_truth": item["ground_truth"],
            }
        )

        # Prevent hitting Groq/Gemini rate limits during collection
        time.sleep(1)

    # Save to a local file
    with open(RESULTS_FILE, "w") as f:
        json.dump(collected_data, f, indent=4)

    print("✅ Collection complete! Data saved to 'rag_results.json'")


if __name__ == "__main__":
    collect_answers()
