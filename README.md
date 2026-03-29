# FailOS AI

FailOS is an AI-powered Django platform designed to analyze startup failures. By feeding the AI your failed business ideas, it structure the input, estimates market demand, evaluates competition, calculates a risk score, and provides actionable pivot suggestions.

## Features
- **AI-Powered Analysis**: Integrates Google's Gemini 2.0 Flash-Lite API to generate structured startup assessments and risk factors from messy, unstructured text (including Hinglish).
- **Failure Resilience**: Built-in deterministic Python fallback algorithm guaranteeing 100% platform uptime even if external LLM APIs fail or exceed rate limits.
- **Dynamic Geographic Forms**: Asynchronous, chained REST API dropdowns to specify precise launch locations (Country -> State -> City).
- **Serverless Production Infrastructure**: Fully configured for Vercel deployment with Supabase PostgreSQL connection poolers, bypassing strict IPv6 serverless restrictions using custom `urllib` parsers.
- **Glassmorphism UI**: Modern, responsive dashboard and landing pages built without heavy component libraries.

## Tech Stack
- **Backend Framework**: Django (Python)
- **Database**: PostgreSQL (Hosted on Supabase)
- **AI Integration**: Google Generative AI (Gemini)
- **Deployment**: Vercel Serverless Edge
- **Frontend**: HTML5, Vanilla JavaScript, CSS3 Glassmorphism

---

## Running Locally

### 1. Requirements
Ensure you have Python 3.9+ and `pip` installed.

### 2. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory (`FAILOS/.env`) with the following variables:
```env
# Gemini AI Configuration
GEMINI_API_KEY="your-gemini-api-key"

# Database Configuration (Supabase or Local Postgres)
DATABASE_URL="postgresql://postgres.[project_ref]:[password]@aws-0-pooler.supabase.com:6543/postgres"

# Django Security
SECRET_KEY="your-secret-key"
DEBUG="True"
```

### 4. Database Initialization
Run the Django migrations to create the required database tables:
```bash
python manage.py migrate
```

To use the dynamic location dropdowns, you must seed the initial geographic data:
```bash
python tmp_populate_data.py
```

### 5. Running the Application
Start the Django development server:
```bash
python manage.py runserver
```
Visit `http://localhost:8000/` in your browser.

---

## Production Deployment (Vercel)

This application is structurally configured for Vercel deployment. 
1. Use the `vercel.json` file to dictate WSGI server configurations and static file routing.
2. The `package.json` includes a custom `vercel-build` script to automatically run `collectstatic` during deployment.
3. Ensure the `DATABASE_URL` in Vercel utilizes the **IPv4 Connection Pooler (Port 6543)** and the password is correctly URL-encoded (e.g. `@` becomes `%40`) to prevent 500 Server Errors due to Django connection string truncations.
