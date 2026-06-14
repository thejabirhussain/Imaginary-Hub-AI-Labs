import re
from typing import List, Dict, Any, Callable
from src.utils import time_it

class Chunker:
    """
    Splits document text into optimal sized pieces (chunks) suitable for LLM injection.
    Supports Fixed-size, Recursive Character, and Semantic chunking.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @time_it
    def chunk_documents(self, pages_data: List[Dict[str, Any]], strategy: str = "recursive", embedder: Any = None) -> List[Dict[str, Any]]:
        """
        Main orchestration endpoint for chunking documents.
        
        Args:
            pages_data: List of page objects containing 'text' and 'metadata'.
            strategy: 'fixed', 'recursive', or 'semantic'.
            embedder: An instance of the embedding engine (required for semantic chunking).
        """
        if strategy == "fixed":
            return self.fixed_size_chunk(pages_data)
        elif strategy == "recursive":
            return self.recursive_character_chunk(pages_data)
        elif strategy == "semantic":
            if not embedder:
                raise ValueError("An embedder instance must be provided for semantic chunking.")
            return self.semantic_chunk(pages_data, embedder)
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

    def fixed_size_chunk(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        STRATEGY 1: Fixed-Size Chunking.
        Splits text by absolute character lengths, regardless of punctuation or syntax.
        
        Tradeoffs:
        - Pros: Simple, fast, deterministic.
        - Cons: Rips sentences and thoughts in half, causing high context loss.
        """
        chunks = []
        chunk_counter = 0

        for page in pages_data:
            text = page["text"]
            meta = page["metadata"]
            
            # Slide window across text
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunk_text = text[start:end]
                
                chunk_meta = meta.copy()
                chunk_meta["chunk_index"] = chunk_counter
                chunk_meta["chunk_strategy"] = "fixed"
                
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_meta
                })
                
                chunk_counter += 1
                start += (self.chunk_size - self.chunk_overlap)
                
        return chunks

    def recursive_character_chunk(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        STRATEGY 2: Recursive Character Chunking (Standard Production Default).
        Recursively splits text by a sequence of characters to keep semantic blocks 
        (paragraphs, sentences, words) together as much as possible.
        
        Tradeoffs:
        - Pros: Excellent balance of structure conservation and predictable chunk sizes.
        - Cons: Still doesn't understand semantic concepts (it's purely character-rule based).
        """
        chunks = []
        chunk_counter = 0
        separators = ["\n\n", "\n", " ", ""]

        def _split_text(text: str, seps: List[str]) -> List[str]:
            """Helper to recursively divide text using list of separators."""
            if not seps or len(text) <= self.chunk_size:
                return [text] if text else []
            
            sep = seps[0]
            parts = text.split(sep)
            
            # Recombine splits into blocks smaller than chunk_size
            merged = []
            current_block = ""
            
            for part in parts:
                # If a single unit is bigger than chunk_size, split it with next separator recursively
                if len(part) > self.chunk_size:
                    if current_block:
                        merged.append(current_block)
                        current_block = ""
                    # Delegate remaining separators
                    sub_parts = _split_text(part, seps[1:])
                    merged.extend(sub_parts)
                else:
                    test_block = current_block + (sep if current_block else "") + part
                    if len(test_block) <= self.chunk_size:
                        current_block = test_block
                    else:
                        if current_block:
                            merged.append(current_block)
                        current_block = part
                        
            if current_block:
                merged.append(current_block)
                
            return merged

        for page in pages_data:
            text = page["text"]
            meta = page["metadata"]
            
            # Split the text recursively
            raw_chunks = _split_text(text, separators)
            
            # Now build chunks with overlap
            # For educational simplicity, we construct overlapping blocks from our clean recursive splits
            current_chunk = ""
            for idx, item in enumerate(raw_chunks):
                if not current_chunk:
                    current_chunk = item
                else:
                    test_chunk = current_chunk + " " + item
                    if len(test_chunk) <= self.chunk_size:
                        current_chunk = test_chunk
                    else:
                        chunk_meta = meta.copy()
                        chunk_meta["chunk_index"] = chunk_counter
                        chunk_meta["chunk_strategy"] = "recursive"
                        
                        chunks.append({
                            "text": current_chunk,
                            "metadata": chunk_meta
                        })
                        chunk_counter += 1
                        
                        # Apply simple overlap heuristic by taking the last part of current chunk
                        overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                        current_chunk = current_chunk[overlap_start:] + " " + item
            
            # Append trailing piece
            if current_chunk:
                chunk_meta = meta.copy()
                chunk_meta["chunk_index"] = chunk_counter
                chunk_meta["chunk_strategy"] = "recursive"
                chunks.append({
                    "text": current_chunk,
                    "metadata": chunk_meta
                })
                chunk_counter += 1

        return chunks

    def semantic_chunk(self, pages_data: List[Dict[str, Any]], embedder: Any) -> List[Dict[str, Any]]:
        """
        STRATEGY 3: Semantic Chunking (Advanced).
        Splits text based on embedding similarities between consecutive sentences.
        If the similarity between sentence N and N+1 falls below a dynamic threshold, 
        a boundary is created.
        
        Tradeoffs:
        - Pros: Retains high conceptual integrity. Extremely natural chunks.
        - Cons: Computationally expensive. Requires generating sentence embeddings.
        """
        chunks = []
        chunk_counter = 0

        # Cosine similarity helper
        def cosine_similarity(v1, v2) -> float:
            import numpy as np
            dot = np.dot(v1, v2)
            norm_a = np.linalg.norm(v1)
            norm_b = np.linalg.norm(v2)
            if norm_a == 0 or norm_b == 0:
                return 0.0
            return float(dot / (norm_a * norm_b))

        for page in pages_data:
            text = page["text"]
            meta = page["metadata"]
            
            # 1. Split page into sentences using regex
            sentences = re.split(r'(?<=[.!?])\s+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= 1:
                # Page too small, make it a single chunk
                chunk_meta = meta.copy()
                chunk_meta["chunk_index"] = chunk_counter
                chunk_meta["chunk_strategy"] = "semantic"
                chunks.append({
                    "text": text,
                    "metadata": chunk_meta
                })
                chunk_counter += 1
                continue
                
            # 2. Embed sentences
            # Generating embeddings can take time. We batch-embed for speed.
            sentence_embeddings = embedder.generate_embeddings(sentences)
            
            # 3. Calculate similarity between adjacent sentences
            similarities = []
            for idx in range(len(sentences) - 1):
                sim = cosine_similarity(sentence_embeddings[idx], sentence_embeddings[idx+1])
                similarities.append(sim)
                
            # 4. Determine splitting threshold
            # We look for drops in similarity. A common heuristic is the 20th percentile 
            # of similarity (meaning sentences that are unusually different).
            import numpy as np
            if similarities:
                # Threshold is set to 20% lowest similarities (greatest gaps) or a baseline 0.8
                percentile_threshold = float(np.percentile(similarities, 20))
                # Bound between 0.6 and 0.85 to avoid degenerate thresholds
                threshold = max(0.60, min(0.85, percentile_threshold))
            else:
                threshold = 0.75
                
            # 5. Group sentences into semantic chunks
            current_group = [sentences[0]]
            for idx, sim in enumerate(similarities):
                next_sentence = sentences[idx + 1]
                
                # Check semantic threshold or absolute size boundary
                current_size = sum(len(s) for s in current_group)
                if sim < threshold or (current_size + len(next_sentence) > self.chunk_size * 1.5):
                    # Save current group as chunk
                    chunk_text = " ".join(current_group)
                    chunk_meta = meta.copy()
                    chunk_meta["chunk_index"] = chunk_counter
                    chunk_meta["chunk_strategy"] = "semantic"
                    
                    chunks.append({
                        "text": chunk_text,
                        "metadata": chunk_meta
                    })
                    chunk_counter += 1
                    
                    # Start new group
                    current_group = [next_sentence]
                else:
                    current_group.append(next_sentence)
                    
            # Handle remaining sentences
            if current_group:
                chunk_text = " ".join(current_group)
                chunk_meta = meta.copy()
                chunk_meta["chunk_index"] = chunk_counter
                chunk_meta["chunk_strategy"] = "semantic"
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_meta
                })
                chunk_counter += 1
                
        return chunks

# Self-test code
if __name__ == "__main__":
    test_pages = [{
        "text": "This is paragraph one explaining vector search. Vectors represent semantic space. "
                "In contrast, paragraph two covers databases. Databases organize tables and rows. "
                "SQL allows querying structured data easily.",
        "metadata": {"document_name": "test.pdf", "page_number": 0}
    }]
    
    chunker = Chunker(chunk_size=100, chunk_overlap=10)
    print("Fixed chunks:")
    for c in chunker.fixed_size_chunk(test_pages):
        print(" - ", c["text"])
        
    print("\nRecursive chunks:")
    for c in chunker.recursive_character_chunk(test_pages):
        print(" - ", c["text"])
