# Build Sunday EP 3: AI Engineering Roadmap & Content Automation

This directory contains the presentations, reference curriculum, and code automation scripts developed for **Episode 3 of Build Sunday**. In this episode, we lay out the complete **6-Step AI Engineer Roadmap** to land jobs in the current intelligent market and release the official **Imaginary Hub Content Automation Suite**—a set of production-ready tools to automate video editing, reels extraction, and LinkedIn/Instagram carousel generation.

---

## 🗺️ The 6-Step AI Engineer Roadmap

AI Engineering bridges the gap between raw research and shipping production systems. Here is the structured path outlined in the presentation:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 1: Programming & LeetCode                      │
│        Pick Python or Java. Master syntax. Solve 200-300 problems       │
│                to build logical breaking-down mindsets.                 │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 2: Core Web Technologies                       │
│        Learn full-stack web development (MERN, .NET, or FastAPI).        │
│          Understand APIs, requests, data flows, and deployments.        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     STEP 3: Math for Machine Learning                   │
│          Master the pillars: Linear Algebra (Ax=b, E, P, Inverses),     │
│             Multivariate Calculus, and Probability Theory.              │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                STEP 4: Machine Learning Core Algorithms                 │
│         Learn Supervised & Unsupervised (Regressions, SVMs, Trees,       │
│             K-Means). Build algorithms on real datasets.                │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│               STEP 5: Deep Learning, NLP & Transformers                 │
│        Study neural networks (propagation), NLP (tokenization), and      │
│      Transformer architectures. Practice fine-tuning open-source models.│
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                STEP 6: Production Software Architecture                 │
│        Apply Clean Architecture, select vector databases (Qdrant),      │
│         design reliable RAG systems, and optimize system layers.        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1. Programming & Problem Solving
* **Goal**: Pick a foundational language (Python is highly recommended for ML/AI; Java is also solid) and master it.
* **Practice**: Solve 200 to 300 problems on platforms like LeetCode. This is not about beating AI; it is about building the engineering mindset required to decompose complex problems.

### 2. Full-Stack Web Development
* **Goal**: AI cannot live in isolation. You must know how to build a web interface to host and consume your models.
* **Stack**: Learn MERN (MongoDB, Express, React, Node.js) or Python backends (FastAPI/Flask) to integrate model endpoints.

### 3. Mathematics for ML
* **Goal**: Avoid using algorithms as black boxes. Understand why models work.
* **Pillars**: 
  - **Linear Algebra**: Matrix multiplications, systems of equations ($Ax=b$), Gaussian elimination, pivots, and matrices inverses.
  - **Calculus**: Derivatives, gradients, and optimization loops.
  - **Probability & Statistics**: Densities, distributions, and likelihood estimations.

### 4. Machine Learning Algorithms
* **Goal**: Build models on real-world datasets.
* **Pillars**: Supervised learning (linear/logistic regression, SVMs, decision trees, random forests) and unsupervised clustering (K-Means).

### 5. DL, NLP & Transformers
* **Goal**: Master modern natural language processing and deep neural networks.
* **Pillars**: Tokenization, backpropagation, and transformer architectures (self-attention). Practice fine-tuning base LLMs (like Llama-3 or GPT-2) on custom downstream tasks.

### 6. Production Software Architecture
* **Goal**: Architect enterprise-grade, resilient AI applications.
* **Pillars**: Implement **Clean Architecture** patterns, write decoupling layers, manage context window sizes, select appropriate vector databases (e.g. Qdrant), and establish reliable RAG pipelines.

---

## 🛠️ Content Automation Suite

To support creators, developers, and educators, we have bundled **8 automated script tools** that handle image generation and video compositing locally using `Pillow`, `MoviePy`, and `FFmpeg`.

### Video Editing & Clip Extraction

#### 1. [video_editor.py](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep3_channel_roadmap/video_editor.py)
* **Description**: A performance-optimized jump-cut talking-head editor. It loads speech intervals from `intervals.json` and subtitles from `subtitles.json`, merges active voice frames while eliminating dead air, applies exposure/contrast LUT color grading, and embeds word-wrapped subtitles using a custom cache to bypass frame-by-frame rendering loops.
* **Usage**:
  ```bash
  # Render full edited video
  python video_editor.py
  # Render a 60-second preview
  python video_editor.py --preview
  ```

#### 2. [create_intro_reel.py](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep3_channel_roadmap/create_intro_reel.py)
* **Description**: Extracts a 90-second vertical 9:16 Short/Reel from a raw widescreen talking-head video. It automatically crops the center coordinates ($657 \rightarrow 1264$), resizes, color grades, draws a top pill banner, and streams colored background subtitles below.
* **Usage**:
  ```bash
  python create_intro_reel.py --preview
  ```

#### 3. [create_lecture_02_reels.py](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep3_channel_roadmap/create_lecture_02_reels.py)
* **Description**: Extracts widescreen educational clips from Linear Algebra Lecture 02 (e.g. Bad Equations, Zero Pivots, Elimination Matrices, Inverses), applies color LUT grading, parses timestamps from the transcription text file, and renders drop-shadowed subtitles.
* **Usage**:
  ```bash
  # Render all four clips
  python create_lecture_02_reels.py --clip all
  # Render a specific clip with 10s preview limit
  python create_lecture_02_reels.py --clip A --preview
  ```

#### 4. [create_lecture_reels.py](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep3_channel_roadmap/create_lecture_reels.py)
* **Description**: Widescreen clips generator for Linear Algebra Lecture 01 & Lecture 02, adding drop-shadowed subtitles and top pill banners.
* **Usage**:
  ```bash
  python create_lecture_reels.py --clip all
  ```

#### 5. [create_rag_reels.py](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep3_channel_roadmap/create_rag_reels.py)
* **Description**: Generates educational reels from RAG Sunday Episode 2, extracting components like LLM classification, RAG architecture whiteboard, RAG vs Fine-tuning, and chunk overlaps.
* **Usage**:
  ```bash
  python create_rag_reels.py --clip 3
  ```

---

### Carousel Slide Deck Generators

#### 6. [generate_carousel.py](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep3_channel_roadmap/generate_carousel.py)
* **Description**: Automated generator for Instagram/LinkedIn square carousels ($1080 \times 1080$) for Episode 1 (Memory, Streaming, Cost counting, Fallback). Generates slides with high-fidelity gradients, rounded borders, card structures, and text-wrapping configurations.
* **Usage**:
  ```bash
  python generate_carousel.py
  ```

#### 7. [generate_lecture_carousel.py](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep3_channel_roadmap/generate_lecture_carousel.py)
* **Description**: Slide deck generator for Linear Algebra Lecture 02 visual notes (Ax=b, elimination, zero pivots, augmented matrices, Gauss-Jordan method).
* **Usage**:
  ```bash
  python generate_lecture_carousel.py
  ```

#### 8. [generate_rag_carousel.py](file:///Users/shaikmohammedjabirhussain/Desktop/Imaginary_Hub_content/Imaginary-Hub-AI-Labs/build_sunday/ep3_channel_roadmap/generate_rag_carousel.py)
* **Description**: Slide deck generator for Episode 2 RAG architecture (chunking, Qdrant vectors, Ollama offline inference).
* **Usage**:
  ```bash
  python generate_rag_carousel.py
  ```

---

## 🚀 Setup & Installation

### Prerequisites
1. **Python 3.8+**
2. **System Fonts**: The scripts default to macOS supplemental fonts:
   - `/System/Library/Fonts/Supplemental/Arial Bold.ttf`
   - `/System/Library/Fonts/Supplemental/Arial.ttf`
   If you are on Windows/Linux, the scripts fall back to Pillow's default font. Modify the `FONT_PATH` variables if customized styles are needed.
3. **FFmpeg**: Required on your system path for video manipulation.

### Setup
1. Install project dependencies:
   ```bash
   pip install pillow moviepy numpy
   ```
2. Place your raw video footages in the root directory matching the filenames mapped in the scripts (`OPEN API CRASH COURSE SMART QA.mov`, `Linear Algebra 01.mov`, `Linear Algebra 02.mov`, `Building RAG from Scratch - PDF Q&A System (Build Sunday Ep 2).mov`, `Imaginary_Hub.MOV`).
3. Run the scripts of your choice to output carousels into folders or exported video clips into MP4 formats.
