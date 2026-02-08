import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()


# Configure API key
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def list_available_models():
    print("📦 Available Google Gemini Models:\n")

    for model in genai.list_models():
        # Only show models that support text generation
        if "generateContent" in model.supported_generation_methods:
            print(f"Model name      : {model.name}")
            print(f"Display name    : {model.display_name}")
            print(f"Description     : {model.description}")
            print(f"Input token lim : {model.input_token_limit}")
            print(f"Output token lim: {model.output_token_limit}")
            print("-" * 60)

if __name__ == "__main__":
    list_available_models()
