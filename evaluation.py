import requests
import json
import pandas as pd
import os
import re
from dotenv import load_dotenv

# Load Env for the Judge
load_dotenv()
from langchain_groq import ChatGroq

# --- CONFIGURATION ---
API_URL = "http://localhost:8000/chat"
JUDGE_MODEL = "llama-3.3-70b-versatile"  # The latest stable model

# --- THE TEST DATASET ---
test_cases = [
    {
        "type": "retrieval",
        "question": "What are the 6 functions of NIST CSF 2.0?",
        "expected_intent": "Must list: Govern, Identify, Protect, Detect, Respond, Recover.",
    },
    {
        "type": "retrieval",
        "question": "What is the definition of the Protect function?",
        "expected_intent": "Must define it as safeguards to manage cybersecurity risk.",
    },
    {
        "type": "router",
        "question": "Who are you?",
        "expected_intent": "Must identify as AuditAI or NIST Compliance Engine. MUST NOT cite sources.",
    },
    {
        "type": "negative",
        "question": "What is the recipe for chocolate cake?",
        "expected_intent": "Must refuse to answer or state that information is missing/not in the database.",
    },
]


def get_agent_response(question):
    """Calls your Agentic Backend and reconstructs the streaming text."""
    try:
        response = requests.post(
            API_URL, json={"query": question, "history": []}, stream=True
        )

        full_text = ""
        sources = []

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if data["type"] == "token":
                        full_text += data["content"]
                    elif data["type"] == "sources":
                        sources = data["content"]
                except:
                    pass
        return full_text, sources
    except Exception as e:
        return f"Error: {e}", []


def evaluate_answer(question, actual_answer, expected_intent):
    """Asks the Judge LLM to grade the response using strict JSON."""

    # We ask for JSON to prevent parsing errors
    judge_prompt = (
        f"You are a strict QA Auditor grading an AI Bot.\n"
        f"1. QUESTION: {question}\n"
        f"2. ACTUAL ANSWER: {actual_answer}\n"
        f"3. SUCCESS CRITERIA: {expected_intent}\n\n"
        f"Task: Compare the ACTUAL ANSWER to the SUCCESS CRITERIA.\n"
        f"Return a JSON object with two fields:\n"
        f'- "score": "PASS" or "FAIL"\n'
        f'- "reason": "Short explanation"\n\n'
        f"JSON OUTPUT:"
    )

    llm = ChatGroq(
        temperature=0, model_name=JUDGE_MODEL, api_key=os.getenv("GROQ_API_KEY")
    )
    try:
        # Get raw response
        result = llm.invoke(judge_prompt).content

        # Extract JSON using Regex (in case the model adds extra text)
        json_match = re.search(r"\{.*\}", result, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            return data["score"], data["reason"]
        else:
            return "UNKNOWN", "Could not parse JSON"
    except Exception as e:
        return "ERROR", str(e)


# --- MAIN LOOP ---
results = []

print(f"🚀 Starting Auto-Eval on {len(test_cases)} cases...\n")

for case in test_cases:
    print(f"Testing: {case['question']}...", end=" ", flush=True)

    # 1. Get Actual Answer
    actual_text, citations = get_agent_response(case["question"])

    # 2. Judge It
    score, reason = evaluate_answer(
        case["question"], actual_text, case["expected_intent"]
    )

    # 3. Special Check for "Router" tests (Must have 0 citations)
    if case["type"] == "router" and score == "PASS":
        if len(citations) > 0:
            score = "FAIL"
            reason = "Router Failed: It cited sources when it should have just chatted."

    # 4. Special Check for "Negative" tests (Must have 0 citations)
    if case["type"] == "negative" and score == "PASS":
        if len(citations) > 0:
            score = "FAIL"
            reason = "Hallucination Check Failed: It refused to answer but still cited fake sources."

    # 5. Save Result
    results.append(
        {
            "Type": case["type"],
            "Question": case["question"],
            "Answer Preview": actual_text[:50].replace("\n", " ") + "...",
            "Citations": len(citations),
            "Score": score,
            "Reason": reason,
        }
    )
    print(f"[{score}]")

# --- REPORT ---
df = pd.DataFrame(results)
print("\n--- 📊 EVALUATION REPORT ---")
print(df.to_markdown(index=False))

# Calculate Accuracy
pass_count = df[df["Score"] == "PASS"].shape[0]
print(f"\nFinal Score: {pass_count}/{len(df)} ({pass_count/len(df)*100:.0f}%)")
