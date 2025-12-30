"""
Configuration du projet Auris Chatbot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins du projet
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

# Créer les répertoires s'ils n'existent pas
PDF_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Configuration API Google
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY non configurée. "
        "Créez un fichier .env avec votre clé API Google."
    )

# Configuration du modèle
EMBEDDING_MODEL = "models/embedding-001"
LLM_MODEL = "models/gemini-2.0-flash"

# Configuration du chunking
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Configuration ChromaDB
COLLECTION_NAME = "toyota_auris_docs"

# Configuration du RAG
TOP_K_RESULTS = 5
