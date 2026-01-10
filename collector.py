import os
import csv
import json
import time
import pandas as pd
from rag_engine import process_query
from dotenv import load_dotenv

load_dotenv()


def load_test_csv(file_path):
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        f.readline()  # skip header
        reader = csv.reader(f)
        for line in reader:
            if line:
                # Clean prefix from the first column
                q = line[0].replace("", "").strip('"').strip()
                rows.append({"question": q, "ground_truth": line[1]})
    return rows


def collect_answers():
    test_questions = load_test_csv("test.csv")
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
    with open("rag_results.json", "w") as f:
        json.dump(collected_data, f, indent=4)

    print("✅ Collection complete! Data saved to 'rag_results.json'")


if __name__ == "__main__":
    collect_answers()
