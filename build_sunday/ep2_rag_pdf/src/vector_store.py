import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.utils import time_it

class VectorStore:
    """
    Qdrant Vector Database controller.
    Manages collection lifecycles, vector insertions (upserts), and vector searches.
    
    EDUCATIONAL INSIGHT: How do Vector Databases Work?
    - A standard SQL database indexes scalars (e.g. integer IDs, dates, strings) via B-Trees.
    - A Vector DB indexes coordinates in multi-dimensional vector space using structures like 
      HNSW (Hierarchical Navigable Small World). This constructs a graph of nodes, allowing 
      logarithmic-time nearest-neighbor retrieval (Approximate Nearest Neighbors).
    
    COMPARING VECTOR STORES:
    - **FAISS**: Local memory-only library from Meta. Super fast, great for localized indexing, 
      but does not support remote server concurrency or dynamic payload updates out of the box.
    - **Chroma**: Lightweight, developer-friendly embedding database, but typically slower at scale.
    - **Pinecone**: Fully managed cloud service. Zero ops, scales globally, but closed-source and expensive.
    - **Qdrant**: High-performance, open-source, written in Rust. Supports hybrid filtering, 
      in-memory/on-disk storage, and has a sleek web dashboard (port 6333) ideal for both local dev and production.
    """

    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "pdf_rag_collection"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        
        # Connect to the local running Qdrant instance
        print(f"🔌 Connecting to Qdrant DB at {self.host}:{self.port}...")
        self.client = QdrantClient(host=self.host, port=self.port)
        print("✅ Connected to Qdrant Client.")

    def init_collection(self, vector_dim: int, force_recreate: bool = False):
        """
        Creates or resets the database collection with the correct dimensions.
        """
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name in collection_names:
                if force_recreate:
                    print(f"🗑️ Re-creating collection '{self.collection_name}'...")
                    self.client.delete_collection(self.collection_name)
                    self._create(vector_dim)
                else:
                    print(f"📦 Collection '{self.collection_name}' already exists. Skipping recreation.")
            else:
                self._create(vector_dim)
                
        except Exception as e:
            print(f"⚠️ Collection status lookup failed: {str(e)}. Attempting fresh creation.")
            self._create(vector_dim)

    def _create(self, vector_dim: int):
        """Helper to call collection creation endpoint."""
        print(f"🚀 Creating new Qdrant Collection: '{self.collection_name}' with {vector_dim} dimensions...")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_dim, 
                distance=Distance.COSINE
            )
        )
        print(f"✅ Collection '{self.collection_name}' successfully initialized.")

    @time_it
    def upsert_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Saves text chunks and their embeddings into the Qdrant database.
        Includes original text and metadata fields inside the payload.
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Size mismatch: Chunks and embeddings lists must be of equal length.")

        print(f"📤 Preparing to upsert {len(chunks)} chunks to Qdrant...")
        points = []
        
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
            # Create a point object for Qdrant ingestion
            # We generate a unique UUID for each point
            point_id = str(uuid.uuid4())
            
            # Combine the text and metadata fields as the point payload
            payload = {
                "text": chunk["text"],
                **chunk["metadata"]
            }
            
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            )
            
        # Perform bulk upload
        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True  # Blocks until the write operation is committed in database
        )
        print(f"✅ Upsert complete. Database Status: {operation_info.status}")

    @time_it
    def search_similarity(self, query_vector: List[float], top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Executes a vector search inside Qdrant and retrieves top nearest neighbors.
        """
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )
        
        formatted_results = []
        for scored_point in response.points:
            formatted_results.append({
                "score": scored_point.score,
                "text": scored_point.payload.get("text", ""),
                "metadata": {k: v for k, v in scored_point.payload.items() if k != "text"}
            })
            
        return formatted_results

# Self-test when executing vector_store directly (requires running Qdrant instance)
if __name__ == "__main__":
    import numpy as np
    # Initialize connection
    db = VectorStore()
    # Setup mock collection
    db.init_collection(vector_dim=3, force_recreate=True)
    # Insert dummy vectors
    mock_chunks = [
        {"text": "Text snippet one", "metadata": {"page_number": 0, "document_name": "test1.pdf"}},
        {"text": "Text snippet two", "metadata": {"page_number": 1, "document_name": "test2.pdf"}}
    ]
    mock_vectors = [
        [0.1, 0.2, 0.9],
        [0.8, 0.2, 0.1]
    ]
    db.upsert_chunks(mock_chunks, mock_vectors)
    
    # Query database
    matches = db.search_similarity([0.1, 0.25, 0.85], top_k=1)
    print("Search Result Match:")
    print(matches)
