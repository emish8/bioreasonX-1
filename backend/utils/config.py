import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# Base directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# DB paths
FAISS_INDEX_DIR = DATA_DIR / "faiss_index"
LITERATURE_DB_PATH = DATA_DIR / "literature_db.json"
GRAPH_DB_PATH = DATA_DIR / "networkx_graph.gpickle"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)

# API keys & model configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_PRO = "gemini-2.5-pro"
GEMINI_MODEL_FLASH = "gemini-2.5-flash"

# Local LLM configuration
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
LOCAL_LLM_API_BASE = os.getenv("LOCAL_LLM_API_BASE", "http://localhost:8000/v1")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "deepseek-r1-distill-qwen-32b-awq")

# Neo4j settings
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Logging Configuration
LOG_FILE = DATA_DIR / "bioreason_x.log"
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BioReason-X")

def has_gemini_credentials() -> bool:
    """Returns True if the Gemini API Key is available in the environment."""
    return bool(GEMINI_API_KEY)

def has_neo4j_credentials() -> bool:
    """Returns True if Neo4j parameters are configured."""
    return bool(NEO4J_URI and NEO4J_PASSWORD)
