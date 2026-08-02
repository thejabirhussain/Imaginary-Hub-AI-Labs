# Build Sunday Projects

Welcome to the **Build Sunday** directory. This folder houses the practical, hands-on software builds and codebases developed during our weekly series. We sit down, take real-world problem statements, and build complete applications end-to-end focusing on software architecture, AI engineering, and system resilience.

---

## 🛠️ Projects Index

### [Episode 1: Smart Q&A Chatbot with Local Fallback](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep1_openapi_chat)
A production-grade command-line interface (CLI) chat agent that goes beyond simple wrappers. It integrates:
* **Conversational Memory**: Maintains states across session limits.
* **Token Streaming**: Real-time TYPEWRITER UX using token-level generators.
* **Pre-flight tiktoken Calculation**: Live USD cost counting.
* **Local Fallback**: Automatically intercepting network/credit failures and falling back to a local Llama-3 model via Ollama.

### [Episode 2: Building RAG From Scratch (Local PDF Q&A System)](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep2_rag_pdf)
A secure, local Retrieval-Augmented Generation pipeline using Qdrant vector database and Ollama inference. Features recursive and semantic text chunking, embedding upserts, and citation-grounded response generation.

### [Episode 3: AI Engineering Roadmap & Content Automation Suite](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep3_channel_roadmap)
Our complete 6-Step AI Engineering career roadmap combined with the content automation library—scripts to crop, color-grade, and embed subtitle overlays on lectures, reels, and shorts, plus automated LinkedIn/Instagram slide deck carousel creators.

### [Episode 4: PCA From Scratch Using Eigendecomposition](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep4_pca_from_scratch)
A from-scratch Principal Component Analysis implementation built purely with NumPy — no `scikit-learn` shortcuts. Covers mean centering, the covariance matrix, eigendecomposition, ranking principal components by eigenvalue, and projecting high-dimensional data (64-D handwritten digit images) down to 2-D. Includes a side-by-side validation script against scikit-learn's `PCA()`.

---

## 🚀 Getting Started
Each project folder contains its own self-contained setup instructions, local virtual environments, and `.env.example` configurations. Refer to individual project readmes to run the systems on your machine.
