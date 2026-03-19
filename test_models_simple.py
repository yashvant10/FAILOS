import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def test_model(model_name):
    print(f"Testing {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"Success: {response.text}")
        return True
    except Exception as e:
        print(f"Failed with {model_name}: {e}")
        return False

if __name__ == "__main__":
    models = ['gemini-2.0-flash-lite', 'gemini-1.5-flash', 'gemini-1.5-flash-latest']
    for m in models:
        if test_model(m):
            break
