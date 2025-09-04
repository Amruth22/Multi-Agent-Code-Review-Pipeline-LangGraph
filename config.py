# Configuration for Smart Code Review Pipeline
# Uses environment variables for secure credential management

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub settings
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_API_URL = os.getenv('GITHUB_API_URL', 'https://api.github.com')

# Email settings
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_TO = os.getenv('EMAIL_TO', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

# Gemini settings
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')

# Quality thresholds
PYLINT_THRESHOLD = float(os.getenv('PYLINT_THRESHOLD', '7.0'))
COVERAGE_THRESHOLD = float(os.getenv('COVERAGE_THRESHOLD', '80.0'))
AI_CONFIDENCE_THRESHOLD = float(os.getenv('AI_CONFIDENCE_THRESHOLD', '0.8'))

# Validation function to check if all required environment variables are set
def validate_config():
    """Validate that all required environment variables are configured"""
    required_vars = {
        'GITHUB_TOKEN': GITHUB_TOKEN,
        'EMAIL_FROM': EMAIL_FROM,
        'EMAIL_PASSWORD': EMAIL_PASSWORD,
        'EMAIL_TO': EMAIL_TO,
        'GEMINI_API_KEY': GEMINI_API_KEY
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please update your .env file with the required credentials.")
        print("   See README.md for setup instructions.")
        return False
    
    print("✅ All required environment variables are configured.")
    return True

# Optional: Validate configuration on import (uncomment if desired)
# validate_config()