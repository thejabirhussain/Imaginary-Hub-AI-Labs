import sys
import argparse
from pathlib import Path
from tqdm import tqdm

# Adjust path to enable absolute package structure execution
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import Config
from src.document_processor import DocumentProcessor
from src.chunker import Chunker
from src.embeddings import EmbeddingEngine
from src.vector_store import VectorStore
from src.retriever import Retriever
from src.generator import Generator
from src.utils import print_section_header, time_it

def build_knowledge_base(strategy: str = "recursive", force_recreate: bool = True):
    """
    Ingests PDFs from the uploads folder, chunks them, generates embeddings, 
    and indexes them inside the Qdrant vector store.
    """
    print_section_header(f"Building Knowledge Base (Strategy: {strategy})")
    
    # 1. Document Extraction
    processor = DocumentProcessor(Config.UPLOADS_DIR)
    pages = processor.load_all_pdfs()
    
    if not pages:
        print("\n❌ Ingestion cancelled: Place PDF files inside the uploads folder.")
        print(f"📁 Folder path: {Config.UPLOADS_DIR.absolute()}")
        return False
        
    # 2. Embedding Model Prep
    embedder = EmbeddingEngine(Config.EMBEDDING_MODEL_NAME)
    
    # 3. Text Chunking
    chunker = Chunker(chunk_size=Config.CHUNK_SIZE, chunk_overlap=Config.CHUNK_OVERLAP)
    print(f"⚙️ Splitting pages using strategy: '{strategy}'...")
    chunks = chunker.chunk_documents(pages, strategy=strategy, embedder=embedder)
    print(f"📦 Generated {len(chunks)} total text chunks.")
    
    if not chunks:
        print("❌ No valid text chunks extracted.")
        return False
        
    # 4. Generate Embeddings for Chunks
    print("🧠 Computing dense embeddings for chunks...")
    chunk_texts = [c["text"] for c in chunks]
    
    # Batch embedding creation
    embeddings = embedder.generate_embeddings(chunk_texts)
    
    # 5. Connect to Qdrant and Upsert
    vector_db = VectorStore(
        host=Config.QDRANT_HOST, 
        port=Config.QDRANT_PORT, 
        collection_name=Config.QDRANT_COLLECTION
    )
    
    # Initialize the database structure matching the vector dimensionality
    vector_dim = embedder.get_dimension()
    vector_db.init_collection(vector_dim=vector_dim, force_recreate=force_recreate)
    
    # Ingest data
    vector_db.upsert_chunks(chunks, embeddings)
    print("\n🎉 Knowledge base successfully built and stored in Qdrant!")
    return True

def run_qa_session():
    """
    Starts an interactive terminal session querying the local RAG pipeline.
    """
    print_section_header("Starting Q&A Retrieval Session")
    
    # Initialize Pipeline Components
    try:
        embedder = EmbeddingEngine(Config.EMBEDDING_MODEL_NAME)
        vector_db = VectorStore(
            host=Config.QDRANT_HOST, 
            port=Config.QDRANT_PORT, 
            collection_name=Config.QDRANT_COLLECTION
        )
        retriever = Retriever(embedder, vector_db, top_k=Config.TOP_K)
        generator = Generator(ollama_host=Config.OLLAMA_HOST, model_name=Config.OLLAMA_MODEL)
    except Exception as e:
        print(f"❌ Failed to initialize query services: {str(e)}")
        print("👉 Make sure Qdrant is running on port 6333 and Ollama on port 11434.")
        return

    print("\n🟢 RAG Session active. Ask your questions below! (type 'exit' or 'quit' to stop)")
    print("-" * 80)
    
    while True:
        try:
            query = input("\n🔎 Question: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
                
            print("\n🔄 Running semantic lookup...")
            # Retrieve relevant content
            search_results = retriever.retrieve(query)
            context = search_results["context_string"]
            raw_docs = search_results["raw_results"]
            
            if not raw_docs:
                print("⚠️ No matching content found in database. Is the database empty?")
                continue
                
            print(f"🎯 Retrieved {len(raw_docs)} matching chunks from database.")
            
            # Show sources retrieved with scores
            print("📚 Source Contexts:")
            for idx, doc in enumerate(raw_docs):
                doc_name = doc["metadata"].get("document_name", "Unknown")
                page_num = doc["metadata"].get("page_number", 0) + 1
                score = doc["score"]
                print(f"   [{idx+1}] {doc_name} (Page {page_num}) - Similarity Score: {score:.4f}")
                
            print("\n🤖 Answer: ", end="", flush=True)
            
            # Define streaming callback to output text as it generates
            def callback(token: str):
                print(token, end="", flush=True)
                
            # Call Ollama generator
            generator.generate_answer(context, query, stream_callback=callback)
            print("\n" + "-" * 80)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error handling query: {str(e)}")

def main():
    Config.display_config()
    
    parser = argparse.ArgumentParser(description="Local RAG System - PDF Q&A Command Line Tool")
    parser.add_argument("--mode", type=str, choices=["build", "qa", "all"], default="qa",
                        help="Operating mode: 'build' to process PDFs, 'qa' to start chat session, or 'all' for both.")
    parser.add_argument("--strategy", type=str, choices=["fixed", "recursive", "semantic"], default="recursive",
                        help="Chunking strategy to use: 'fixed', 'recursive' (default), or 'semantic'.")
    parser.add_argument("--keep", action="store_true", 
                        help="Keep existing collection records when building index (default deletes and recreates).")
    
    args = parser.parse_args()
    
    if args.mode in ["build", "all"]:
        success = build_knowledge_base(strategy=args.strategy, force_recreate=not args.keep)
        if not success and args.mode == "all":
            print("⚠️ Skipping Q&A mode since index building failed.")
            return

    if args.mode in ["qa", "all"]:
        run_qa_session()

if __name__ == "__main__":
    main()
