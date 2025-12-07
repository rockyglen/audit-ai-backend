import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1. Load the secrets from .env
# Real World Note: This prevents your keys from leaking onto GitHub.
load_dotenv()

# 2. Initialize the LLM
# We use 'llama-3.3-70b-versatile'. It's the best open-source model currently available for free.
# temperature=0 means "be strict and factual". Higher numbers make it creative (bad for audits).
llm = ChatGroq(
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
)


# 3. Test Function
def test_llm():
    response = llm.invoke(
        "Explain the concept of 'Regulatory Compliance' in one sentence."
    )
    print("🤖 AI Response:\n", response.content)


if __name__ == "__main__":
    test_llm()
