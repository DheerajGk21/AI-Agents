import os
import warnings
import logging
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

print("Loading environment variables...")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DOCUMENT_PATH = os.getenv("DOCUMENT_PATH")
VECTOR_DB_PATH = "./chroma_db"

EMBEDDING_MODEL = "gemini-embedding-001"
LLM_MODEL = "gemini-3.5-flash"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_COUNT = 2

SYSTEM_INSTRUCTIONS = """
Strictly make use of the pieces of retrieved context provided to answer the question. 
If you dont know the answer, explicitly respond that the answer is not known.
Dont hallucinate.
Keep the answers brief to less than five sentences.

Context: {context}

Question: {question}

Answer:
"""

# --- Disable all warnings -----
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)