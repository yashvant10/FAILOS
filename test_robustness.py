import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Initialize Django for standalone script
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'failos_project.settings')
django.setup()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def test_robustness(title, description):
    print(f"\n--- Testing: {title} ---")
    try:
        from failures.ai_agent import analyze_failure
        # Use city and state if needed, but defaults are fine
        result = analyze_failure(title, description)
        
        print(f"Interpreted Title: {result['interpreted_idea']['title']}")
        print(f"Interpreted Desc: {result['interpreted_idea']['description']}")
        print(f"Business Type: {result['interpreted_idea']['business_type']}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Prediction: {result['prediction']}")
        print(f"Success Score: {result['success_score']}")
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    # Test Case 1: Messy Input (Normalization Layer)
    test_robustness("food delivry app small town low bugdet can work??", "placing order for food in towns where zomato not there")
    
    # Test Case 2: Language Flexibility (Hinglish/Short)
    test_robustness("coffee shop idea mysore 30k budget small", "mysore me badiya coffee stall kholna hai")
    
    # Test Case 3: Informal / Broken English
    test_robustness("i make app for people", "want buy stuff fast and cheap no wait time.")
