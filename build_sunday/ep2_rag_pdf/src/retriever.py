from typing import List, Dict, Any
from src.embeddings import EmbeddingEngine
from src.vector_store import VectorStore
from src.prompts import CONTEXT_BLOCK_TEMPLATE
from src.utils import time_it, format_citation

class Retriever:
    """
    Coordinates semantic search and raw source tracking.
    Converts query text to embeddings, requests matching documents, and structures prompt contexts.
    
    EDUCATIONAL INSIGHT: Why Retrieval Quality Matters
    - The "Garbage In, Garbage Out" rule rules LLM pipelines. If the retriever fetches irrelevant text, 
      the LLM will generate hallucinated or useless answers.
    - Cosine Similarity measures the angle between the query vector and the document vector.
      Formula: cos(theta) = (A . B) / (||A|| ||B||)
      Value ranges from -1 to 1. Closer to 1 means the vectors point in nearly the same direction, 
      indicating strong semantic alignment.
    """

    def __init__(self, embedder: EmbeddingEngine, vector_store: VectorStore, top_k: int = 4):
        self.embedder = embedder
        self.vector_store = vector_store
        self.top_k = top_k

    @time_it
    def retrieve(self, query: str) -> Dict[str, Any]:
        """
        Executes a similarity search for a query and compiles context data.
        
        Args:
            query: User's search query.
        Returns:
            Dict containing:
            - "context_string": Formatted text block containing retrieved sources & contents
            - "raw_results": List of points returned from Qdrant with scores and payloads
            - "citations": List of formatted unique citations (e.g. "[file.pdf, Page 1]")
        """
        # 1. Embed query
        query_vector = self.embedder.generate_query_embedding(query)
        
        # 2. Search Vector Database
        matches = self.vector_store.search_similarity(query_vector, top_k=self.top_k)
        
        # 3. Format context blocks and track citations
        context_parts = []
        citations = []
        
        for doc in matches:
            text = doc["text"]
            meta = doc["metadata"]
            score = doc["score"]
            
            # Create a readable source identifier (e.g., "paper.pdf, Page 3")
            source_tag = format_citation(meta)
            citations.append(source_tag)
            
            # Format using the CONTEXT_BLOCK_TEMPLATE
            context_block = CONTEXT_BLOCK_TEMPLATE.format(
                source_id=f"{source_tag} (Similarity Score: {score:.4f})",
                chunk_text=text
            )
            context_parts.append(context_block)
            
        # Combine all parts
        context_string = "\n".join(context_parts)
        
        # Unique citations list
        unique_citations = list(dict.fromkeys(citations))
        
        return {
            "context_string": context_string,
            "raw_results": matches,
            "citations": unique_citations
        }

# Self-test code
if __name__ == "__main__":
    # If imports are relative, running direct execution requires PYTHONPATH setup.
    print("Retriever class loaded successfully.")
