import os
import sys
from pathlib import Path

# Add project root to path for local imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.utils.config import GEMINI_API_KEY, logger
import google.generativeai as genai

print(f"Loaded API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-5:] if GEMINI_API_KEY else ''}")

if not GEMINI_API_KEY:
    print("Error: No GEMINI_API_KEY found!")
    sys.exit(1)

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    print("Testing connection to Gemini API...")
    response = model.generate_content("Hello! Are you online?")
    print("Response from Gemini:")
    print(response.text)
    print("SUCCESS: Gemini API is fully functional!")
except Exception as e:
    print(f"FAILURE: Gemini API test failed with error: {e}")
