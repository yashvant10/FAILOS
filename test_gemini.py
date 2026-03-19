import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def test_api():
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in .env")
        return
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        response = model.generate_content("Hello, respond with 'Valid'")
        print(f"Response: {response.text.strip()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
