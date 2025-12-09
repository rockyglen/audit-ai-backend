import time
import ast  # <--- NEW: Using AST instead of JSON for safer parsing
from rag_engine import process_query, llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 1. The Golden Dataset ---
TEST_DATASET = [
    {
        "question": "What are the 6 functions of the NIST Cybersecurity Framework 2.0?",
        "expected_answer": "The 6 functions are Govern, Identify, Protect, Detect, Respond, and Recover.",
    },
    {
        "question": "What is the purpose of the Govern function?",
        "expected_answer": "The Govern function establishes and monitors the organization's cybersecurity risk management strategy, expectations, and policy.",
    },
    {
        "question": "Does the framework apply to small businesses?",
        "expected_answer": "Yes, the framework is designed to be applicable to organizations of all sizes and sectors, including small businesses.",
    },
    {
        "question": "Hi, how are you?",
        "expected_answer": "Greeting response (No sources).",
    },
]


# --- 2. The Judge (LLM Evaluation) ---
def evaluate_answer(question, actual_answer, expected_answer, context):
    eval_prompt = (
        "You are a strict grader for a RAG system. \n"
        "1. Compare the ACTUAL ANSWER with the EXPECTED ANSWER. \n"
        "2. Check if the ACTUAL ANSWER is supported by the RETRIEVED CONTEXT. \n"
        "3. Assign a score from 0 to 100. \n\n"
        "QUESTION: {question}\n"
        "EXPECTED ANSWER: {expected_answer}\n"
        "ACTUAL ANSWER: {actual_answer}\n"
        "RETRIEVED CONTEXT: {context}\n\n"
        "Return ONLY a Python dictionary string like this: {{'score': 95, 'reason': 'Correctly identified all functions.'}}"
    )

    prompt = ChatPromptTemplate.from_messages([("human", eval_prompt)])
    chain = prompt | llm | StrOutputParser()

    try:
        result = chain.invoke(
            {
                "question": question,
                "expected_answer": expected_answer,
                "actual_answer": actual_answer,
                "context": context,
            }
        )
        return result
    except Exception as e:
        return f"{{'score': 0, 'reason': 'Error during evaluation: {e}'}}"


# --- 3. The Execution Loop ---
def run_evaluation():
    print("🧪 STARTING RAG EVALUATION...\n")
    print(f"{'QUESTION':<50} | {'SCORE':<10} | {'REASON'}")
    print("-" * 100)

    total_score = 0

    for test in TEST_DATASET:
        rag_result = process_query(test["question"])

        context_text = ""
        if "context" in rag_result:
            for doc in rag_result["context"]:
                context_text += doc.page_content[:200] + " ... \n"

        eval_result = evaluate_answer(
            test["question"],
            rag_result["answer"],
            test["expected_answer"],
            context_text,
        )

        try:
            # ROBUST PARSING FIX:
            # 1. Strip whitespace
            clean_result = eval_result.strip()
            # 2. Find the dictionary part (starts with { and ends with })
            start = clean_result.find("{")
            end = clean_result.rfind("}") + 1
            clean_result = clean_result[start:end]

            # 3. Use ast.literal_eval which handles single quotes perfectly
            score_data = ast.literal_eval(clean_result)

            score = score_data.get("score", 0)
            reason = score_data.get("reason", "No reason provided")

            # Truncate reason for cleaner table display
            display_reason = (reason[:75] + "..") if len(reason) > 75 else reason

            print(f"{test['question'][:47]:<47}... | {score:<10} | {display_reason}")
            total_score += score

        except Exception as e:
            print(f"{test['question'][:47]:<47}... | ERROR      | Parse Error: {e}")
            print(f"Raw Output: {eval_result}\n")

    avg_score = total_score / len(TEST_DATASET)
    print("-" * 100)
    print(f"\n📊 FINAL ACCURACY SCORE: {avg_score:.2f}/100")


if __name__ == "__main__":
    run_evaluation()
