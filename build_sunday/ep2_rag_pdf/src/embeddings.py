import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from src.utils import time_it

class EmbeddingEngine:
    """
    Handles local generation of vector embeddings from textual content using Sentence-Transformers.
    
    EDUCATIONAL INSIGHT: What are Embeddings & Semantic Similarity?
    - An embedding is a vector (a list of numbers) that represents the semantic meaning of a piece of text.
    - Traditional search looks for exact keywords. Vector search evaluates the geometric distance (angle/closeness) 
      between vectors, capturing concepts. (e.g., "puppy" and "dog" will sit close together in vector space).
      
    DIMENSIONALITY CONCEPTS:
    - `all-MiniLM-L6-v2` outputs 384-dimensional vectors. Each dimension is a learned feature representing 
      an abstract concept.
    - More dimensions (e.g., 1536 in OpenAI, or 1024 in bge-large-en-v1.5) capture more fine-grained semantics 
      but require significantly more CPU/GPU calculation, memory storage, and slower database query speeds.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        print(f"📥 Loading embedding model '{self.model_name}' locally...")
        # Load the model. It automatically downloads to local HuggingFace cache directory if not present.
        self.model = SentenceTransformer(self.model_name)
        print(f"✅ Embedding model loaded. Vector Dimensions: {self.get_dimension()}")

    def get_dimension(self) -> int:
        """Returns the embedding vector size."""
        return self.model.get_embedding_dimension()

    @time_it
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates dense embeddings for a list of text strings in batch.
        
        Args:
            texts: List of strings to encode.
        Returns:
            List of embedding vectors (float lists).
        """
        if not texts:
            return []
        
        # sentence-transformers expects a list of strings
        # we call model.encode with batching and return list of list of floats
        embeddings = self.model.encode(
            texts, 
            show_progress_bar=False, 
            convert_to_numpy=True
        )
        return embeddings.tolist()

    @time_it
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generates an embedding vector for a single query.
        """
        if not query:
            raise ValueError("Query string cannot be empty.")
            
        embedding = self.model.encode(
            query,
            show_progress_bar=False,
            convert_to_numpy=True
        )
        return embedding.tolist()

# Self-test when executing embeddings directly
if __name__ == "__main__":
    engine = EmbeddingEngine()
    test_texts = ["Sentence search", "Machine learning systems are cool."]
    vectors = engine.generate_embeddings(test_texts)
    print(f"Generated {len(vectors)} embeddings.")
    print(f"Vector 1 length: {len(vectors[0])}")
    print(f"Vector 1 start snippet: {vectors[0][:5]}...")
