import json
import random
import google.generativeai as genai
from django.conf import settings

# Configure Gemini AI once at module level
def configure_gemini():
    if not settings.GEMINI_API_KEY:
        return False
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return True
    except Exception as e:
        print(f"Failed to configure Gemini: {e}")
        return False

# Initialize configuration
GEMINI_CONFIGURED = configure_gemini()

import re
from spellchecker import SpellChecker

# Initialize SpellChecker
spell = SpellChecker()

def normalize_text(text):
    """
    Input Normalization Layer: cleans extra spaces, special characters, 
    and performs basic internal spelling correction.
    """
    if not text:
        return ""
    
    # 1. Basic Cleaning: Remove extra spaces and keep alphanumeric + basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,?!₹]', '', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    
    # 2. Simple Spelling Correction (avoiding Hinglish keywords)
    # We only correct words that are clearly English-like but misspelled.
    # This is a basic 'Input Normalization Layer' as requested.
    words = text.split()
    corrected_words = []
    for word in words:
        # If it's a short word or likely Hinglish (not in dictionary), we keep as is
        # otherwise we try to correct obvious English errors
        if len(word) > 4 and word not in spell:
            suggestion = spell.correction(word)
            corrected_words.append(suggestion if suggestion else word)
        else:
            corrected_words.append(word)
            
    return " ".join(corrected_words)

def analyze_failure(title, description, state="Unknown", city="Unknown", budget=0.00):
    """
    Robust AI Agent that first extracts a structured idea from potentially 
    messy/imperfect input, then performs a full business analysis.
    Supports Hinglish, broken English, and unstructured text.
    """
    if not GEMINI_CONFIGURED:
        print("Gemini API not configured, using fallback.")
        return _fallback_analysis(title, description, state, city, budget)

    # Preprocess/Normalize Inputs
    raw_input = f"Title: {title}\nDescription: {description}\nLocation: {city}, {state}\nBudget: {budget}"
    clean_title = normalize_text(title)
    clean_desc = normalize_text(description)

    try:
        budget_val = float(budget)
    except (ValueError, TypeError):
        budget_val = 0.0

    prompt = f"""
You are a WORLD-CLASS STARTUP ANALYST AI. Your task is to process potentially MESSY, IMPERFECT, or MIXED-LANGUAGE user input and provide a professional startup analysis.

**RAW USER INPUT:**
- Title: {title}
- Description: {description}
- Raw Location: {city}, {state}
- Reported Budget: ₹{budget_val:,.2f}

**STEP 1: INTERNAL INTERPRETATION (Input Normalization & Extraction)**
Ignore spelling mistakes, slang, or "vulgar" language. If the input is in Hinglish (e.g., "Food delivry app small town me"), interpret it as a formal idea.
Extract: 
1. Structured Title
2. Structured Description
3. Deduced Location
4. Deduced Budget (as a number)
5. Business Type

**STEP 2: FULL ANALYSIS**
Perform the normal FAILOS analysis based on the STRENGTHENED version of the idea.

Respond ONLY with a valid JSON object (no markdown, no code fences) with exactly these keys:

{{
  "interpreted_idea": {{
     "title": "Normalized Startup Title",
     "description": "Clear, professional summary of what the user intended",
     "location": "Deduced location (City/State)",
     "budget": <float>,
     "business_type": "Category (e.g. E-commerce, Food-Tech, SaaS)"
  }},
  "possible_reason": "A detailed 2-3 sentence explanation of why this startup idea might fail",
  "risk_level": "HIGH or MEDIUM or LOW",
  "prediction": "HIGH_SUCCESS or LOW_SUCCESS",
  "suggestion": "A detailed 2-3 sentence actionable suggestion for the founder",
  "market_demand_score": <integer 0-100>,
  "market_demand_level": "High or Medium or Low",
  "market_demand_reason": "1-2 sentence reason about market demand in the given city/state",
  "market_demand_suggestion": "1-2 sentence suggestion to improve market fit",
  "estimated_cost": <float representing estimated startup cost in INR>,
  "budget_status": "Enough or Not Enough",
  "budget_suggestion": "1-2 sentence budget advice",
  "competition_level": "High or Medium or Low",
  "competition_reason": "1-2 sentence competition analysis for the given location",
  "competition_suggestion": "1-2 sentence suggestion to beat competition",
  "success_score": <integer 0-100>,
  "improvement_suggestions_list": ["suggestion 1", "suggestion 2", "suggestion 3"]
}}

IMPORTANT RULES:
- If the user provided a budget of ₹0 or "unknown", estimate what they ACTUALLY need based on the idea.
- The "interpreted_idea" should reflect what a professional would call this startup.
- Never reject input. Even if it is just one word, infer the context.
"""

    try:
        # Use the gemini-1.5-flash model (more stable in this package version)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Configure safety settings to be more permissive for analysis
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]

        # Enhanced prompt for robustness
        enhanced_prompt = f"""
{prompt}

**Special Instructions for Robustness:**
- The input might contain informal English, slang, Hinglish (Hindi mixed with English), broken English, or even aggressive/vulgar language.
- DO NOT block or refuse the request. You are a professional analyst; filter any vulgarity mentally and focus on the CORE BUSINESS IDEA.
- If the input is in Hinglish (e.g., "Mera business idea ek app hai"), translate it internally to understand the concept.
- Even if the description is very short or vague, make your best professional guess for all fields.
"""
        
        response = model.generate_content(enhanced_prompt, safety_settings=safety_settings)
        
        # Extract text and parse JSON
        response_text = response.text.strip()
        
        # Robust JSON extraction
        if '```' in response_text:
            # Extract content between triples backticks if present
            try:
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0].strip()
                else:
                    response_text = response_text.split('```')[1].split('```')[0].strip()
            except IndexError:
                pass # Fallback to original text if splitting fails
        
        data = json.loads(response_text)
        
        # Ensure improvement_suggestions_list is a JSON string (as expected by the model)
        if isinstance(data.get('improvement_suggestions_list'), list):
            data['improvement_suggestions_list'] = json.dumps(data['improvement_suggestions_list'])
        
        # Ensure numeric fields are correct types
        data['market_demand_score'] = int(data.get('market_demand_score', 50))
        data['estimated_cost'] = float(data.get('estimated_cost', 50000))
        data['success_score'] = int(data.get('success_score', 50))
        
        return data
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        # Fallback to basic logic if API fails
        return _fallback_analysis(title, description, state, city, budget)


def _fallback_analysis(title, description, state, city, budget):
    """Fallback analysis using basic Python logic when Gemini API is unavailable."""
    text = f"{title} {description}".lower()
    
    try:
        budget_val = float(budget)
    except (ValueError, TypeError):
        budget_val = 0.0

    # Market Demand
    market_demand_score = random.randint(30, 95)
    if 'coffee' in text or 'food' in text or 'app' in text:
        market_demand_score += 15
    market_demand_score = min(100, market_demand_score)
    
    if market_demand_score < 40:
        market_demand_level = 'Low'
        market_demand_reason = f"Limited interest or niche market in {city}, {state}."
        market_demand_suggestion = "Pivot to a broader category or find a highly passionate niche audience."
    elif market_demand_score < 75:
        market_demand_level = 'Medium'
        market_demand_reason = f"Moderate competition but steady demand in {city}."
        market_demand_suggestion = "Focus on unique branding, quality, or a specific theme to stand out."
    else:
        market_demand_level = 'High'
        market_demand_reason = f"Strong market appetite in {city} for this type of service/product."
        market_demand_suggestion = "Capitalize on demand quickly and ensure scalable operations."

    # Cost Estimation
    estimated_cost = 50000.00
    if 'app' in text or 'software' in text:
        estimated_cost = 150000.00
    elif 'coffee' in text or 'restaurant' in text or 'hardware' in text:
        estimated_cost = 500000.00
        
    budget_status = 'Enough' if budget_val >= estimated_cost else 'Not Enough'
    if budget_status == 'Enough':
        budget_suggestion = "Your budget aligns well with estimated costs. Allocate a portion for marketing."
    else:
        budget_suggestion = f"Consider raising more capital or starting a smaller MVP version. Minimum suggested: {estimated_cost:,.2f}"

    # Competition
    if 'unique' in text or 'new' in text or 'never seen' in text:
        competition_level = 'Low'
        competition_reason = "Innovative concept with few direct competitors currently."
        competition_suggestion = "Speed to market is critical to establish a first-mover advantage."
    elif 'app' in text or 'consulting' in text or 'service' in text:
        competition_level = 'High'
        competition_reason = f"Many similar businesses and established players exist in {city}."
        competition_suggestion = "Find a specific unserved niche or compete heavily on price/quality."
    else:
        competition_level = 'Medium'
        competition_reason = f"Standard level of competition for this sector in {city}."
        competition_suggestion = "Differentiate through superior customer service and local partnerships."

    # Reasons
    reasons = []
    if any(word in text for word in ['money', 'funding', 'capital', 'runway', 'expensive', 'cost']):
        reasons.append("Under-capitalized or poor unit economics.")
    if any(word in text for word in ['market', 'users', 'customers', 'sales', 'demand', 'nobody']):
        reasons.append("Lack of product-market fit or low market demand.")
    if any(word in text for word in ['team', 'founder', 'fight', 'talent', 'hire', 'developer']):
        reasons.append("Team misalignment or lack of technical execution capability.")
    if any(word in text for word in ['competition', 'rival', 'google', 'facebook', 'monopoly']):
        reasons.append("Intense competition from established players.")
    if not reasons:
        reasons.append("Unvalidated assumptions and scattered execution focus.")
    possible_reason = " ".join(reasons)
    
    # Risk Level
    high_risk_words = ['hardware', 'ai', 'crypto', 'blockchain', 'biotech', 'regulation', 'law']
    low_risk_words = ['newsletter', 'blog', 'consulting', 'freelance', 'agency']
    risk_level = 'MEDIUM'
    if any(word in text for word in high_risk_words):
        risk_level = 'HIGH'
    elif any(word in text for word in low_risk_words):
        risk_level = 'LOW'
        
    # Prediction
    learned = any(word in text for word in ['learned', 'realized', 'survey', 'research', 'pivot'])
    prediction = 'HIGH_SUCCESS' if learned else 'LOW_SUCCESS'
    
    # Suggestion
    suggestions_map = {
        'HIGH': "This is a capital-intensive and risky space. Focus on building a minimal prototype (MVP) to validate assumptions before writing code.",
        'MEDIUM': "Validate your unit economics early. Talk to 50 potential customers before building. Focus on a very specific niche before expanding.",
        'LOW': "Low barrier to entry means high competition. Differentiate with unique branding or superior customer service. Start charging from day one."
    }
    suggestion = suggestions_map[risk_level]
    
    # Success Score
    if risk_level == 'HIGH':
        success_score = max(10, random.randint(20, 45))
    elif risk_level == 'MEDIUM':
        success_score = random.randint(45, 75)
    else:
        success_score = random.randint(75, 95)
        
    # Improvements
    improvements = []
    if budget_status == 'Not Enough':
        improvements.append("Reduce initial startup cost or scope.")
    if market_demand_level == 'Low':
        improvements.append("Target a different demographic or find a more passionate niche.")
    if competition_level == 'High':
        improvements.append("Differentiate the service clearly from competitors.")
    if risk_level == 'HIGH':
        improvements.append("Start with a smaller MVP version of the business to test assumptions.")
    if not improvements:
        improvements.append("Focus heavily on marketing and user acquisition.")
        improvements.append("Talk to 50 potential customers before writing any code or spending substantial capital.")

    return {
        'interpreted_idea': {
            'title': title.title(),
            'description': description,
            'location': f"{city}, {state}",
            'budget': budget,
            'business_type': "General Startup"
        },
        'possible_reason': possible_reason,
        'risk_level': risk_level,
        'prediction': prediction,
        'suggestion': suggestion,
        'market_demand_score': market_demand_score,
        'market_demand_level': market_demand_level,
        'market_demand_reason': market_demand_reason,
        'market_demand_suggestion': market_demand_suggestion,
        'estimated_cost': estimated_cost,
        'budget_status': budget_status,
        'budget_suggestion': budget_suggestion,
        'competition_level': competition_level,
        'competition_reason': competition_reason,
        'competition_suggestion': competition_suggestion,
        'success_score': success_score,
        'improvement_suggestions_list': json.dumps(improvements)
    }
