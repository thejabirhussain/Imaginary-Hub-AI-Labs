import os
from pathlib import Path
from dotenv import load_dotenv

# Find workspace root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    """
    RAG System Configuration Loader.
    Responsible for loading environment variables and establishing system-wide defaults.
    """
    
    # Project Paths
    DATA_DIR = BASE_DIR / "data"
    UPLOADS_DIR = DATA_DIR / "uploads"
    VECTOR_DB_DIR = DATA_DIR / "vector_db"
    
    # Ensure standard directories exist
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Qdrant DB Settings
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "pdf_rag_collection")
    
    # Local Embedding Model Settings (Sentence-Transformers)
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # Ollama Local LLM Settings
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    # Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
    
    # Retrieval Settings
    TOP_K = int(os.getenv("TOP_K", 4))

    @classmethod
    def display_config(cls):
        """Helper to print out configurations for educational validation."""
        print("=" * 60)
        print("          RAG SYSTEM CONFIGURATION (LOCAL STACK)")
        print("=" * 60)
        print(f"Base Directory:       {BASE_DIR}")
        print(f"Uploads Directory:    {cls.UPLOADS_DIR}")
        print(f"Qdrant DB:            {cls.QDRANT_HOST}:{cls.QDRANT_PORT} (Collection: '{cls.QDRANT_COLLECTION}')")
        print(f"Embedding Model:      {cls.EMBEDDING_MODEL_NAME}")
        print(f"Ollama Endpoint:      {cls.OLLAMA_HOST} (Model: '{cls.OLLAMA_MODEL}')")
        print(f"Chunk Config:         Size={cls.CHUNK_SIZE}, Overlap={cls.CHUNK_OVERLAP}")
        print(f"Retrieval Top-K:      {cls.TOP_K}")
        print("=" * 60)

# Self-test when executing config directly
if __name__ == "__main__":
    Config.display_config()
