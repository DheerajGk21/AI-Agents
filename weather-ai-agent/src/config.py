import os
from dotenv import load_dotenv

load_dotenv()       # Read .env file and load environment variables

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")