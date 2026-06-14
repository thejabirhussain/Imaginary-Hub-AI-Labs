# Build Sunday EP 2: Building RAG From Scratch (Local PDF Q&A System)

A modular, production-minded Retrieval-Augmented Generation (RAG) system running **100% locally** using **Qdrant** as the vector database, **Sentence-Transformers** for embedding generation, and **Ollama (llama3.2)** as the LLM.

No third-party API keys required. No cloud subscriptions. Full data privacy.

---

## 🌟 System Architecture & Ingestion Flow

```
                ┌────────────────────────────────────────┐
                │             PDF Documents              │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼ (PyMuPDF fitz)
                ┌────────────────────────────────────────┐
                │          Document Processor            │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │    Chunking: Fixed, Recurse, Semantic  │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │     Embedding: all-MiniLM-L6-v2        │
                └───────────────────┬────────────────────┘
                                    │
                                    ▼
                ┌────────────────────────────────────────┐
                │         Qdrant Vector Database         │
                │        (http://localhost:6333)         │
                └───────────────────┬────────────────────┘
                                    │
        ┌───────────────────────────┴───────────────────────────┐
        │                                                       │
        ▼ (Query Embedding & Cosine Search)                     ▼ (Top-K Context)
┌───────────────┐                                       ┌───────────────┐
│  User Query   │                                       │   Retriever   │
└───────────────┘                                       └───────┬───────┘
                                                                │
                                                                ▼
                                                        ┌───────────────┐
                                                        │ Prompt Ground │
                                                        └───────┬───────┘
                                                                │
                                                                ▼ (Inference API)
                                                        ┌───────────────┐
                                                        │ Local Ollama  │
                                                        └───────┬───────┘
                                                                │
                                                                ▼ (Stream Callback)
                                                        ┌───────────────┐
                                                        │ Answer + Cite │
                                                        └───────────────┘
```

---

## 🚀 Setup Instructions

### Prerequisites
1. **Python 3.9+**
2. **Qdrant**: Running locally on port `6333` (e.g. inside Docker or via binary).
   - Docker quickstart:
     ```bash
     docker run -p 6333:6333 -p 6334:6334 \
       -v $(pwd)/qdrant_storage:/qdrant/storage:z \
       qdrant/qdrant
     ```
   - Dashboard URL: [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
3. **Ollama**: Download and install Ollama from [ollama.com](https://ollama.com).
   - Once running, download the default 3B parameters LLM:
     ```bash
     ollama pull llama3.2
     ```

### 1. Installation
Clone/copy the project files, navigate into the project root, and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
A `.env` file is generated automatically in your workspace with standard local coordinates:
```env
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=pdf_rag_collection
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K=4
```

---

## 🛠️ Usage Guide

### Step 1: Upload Documents
Drop one or more PDF files into the `data/uploads/` directory. (e.g. papers, textbooks, resumes).

### Step 2: Build the Vector Knowledge Base
Process your files and upload them to Qdrant. You can choose from three chunking strategies:
- **`recursive`** (Recommended default: split by paragraphs/sentences)
- **`fixed`** (Split by character count)
- **`semantic`** (Split by topic change using sentence similarities)

```bash
# Build using recursive chunking
python src/main.py --mode build --strategy recursive

# Build using advanced semantic chunking
python src/main.py --mode build --strategy semantic
```

### Step 3: Start interactive Q&A Retrieval Session
Query your knowledge base with real-time answer streaming:
```bash
python src/main.py --mode qa
```

*Example console loop:*
```text
🔎 Question: What is the main thesis of the document?
🔄 Running semantic lookup...
🎯 Retrieved 3 matching chunks from database.
📚 Source Contexts:
   [1] sample.pdf (Page 1) - Similarity Score: 0.8423
   [2] sample.pdf (Page 2) - Similarity Score: 0.7911

🤖 Answer: The main thesis argues that... [sample.pdf, Page 1]. Additionally, ... [sample.pdf, Page 2].
```

---

## 🎓 Learning Objectives

This codebase is specifically constructed to teach:
* **RAG Flow**: The relationship between raw files, vector search, context prompt formulation, and generator execution.
* **Vector Mechanics**: How cosine similarities map semantic vectors to find matching passages.
* **Chunking trade-offs**:
  - **Fixed-size**: Fast but rips sentences in half.
  - **Recursive**: Respects punctuation structural syntax (default).
  - **Semantic**: Slow but preserves continuous context unit integrity.
* **Citation & Grounding**: Writing prompts that constraint hallucination by relying strictly on source tokens.

---

## 🔮 Future Production Improvements
To transition this prototype into a production service:
1. **Hybrid Retrieval**: Combine vector search (Qdrant) with sparse keyword indexing (BM25) to catch both semantic intents and exact keyword IDs.
2. **Re-ranking**: Introduce a cross-encoder model (e.g., `bge-reranker-large`) to re-score the top 25 retrieved candidates, narrowing them down to the best 5 for the LLM.
3. **Chunk Quantization**: Compress embedding dimensions to save memory when storing millions of documents in production Qdrant clusters.
4. **OCR Pipeline**: Integrate libraries like PyMuPDF's OCR support (via Tesseract) to extract scanned text from PDFs.
