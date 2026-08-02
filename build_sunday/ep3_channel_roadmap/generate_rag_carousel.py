import os
from PIL import Image, ImageDraw, ImageFont

# Set up output directory
OUTPUT_DIR = "carousel_slides_rag"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Image size (Instagram/LinkedIn standard square format)
WIDTH = 1080
HEIGHT = 1080

# Colors (HSL Tailored / Modern Theme)
COLOR_BG = (13, 14, 21)          # Dark Slate Blue/Black
COLOR_CARD = (22, 24, 35)        # Slightly lighter Card BG
COLOR_BORDER = (46, 50, 70)      # Gray Border
COLOR_TEXT_MAIN = (242, 244, 248) # Off-white text
COLOR_TEXT_MUTED = (150, 155, 175) # Cool gray text
COLOR_HIGHLIGHT_PINK = (255, 60, 140) # Vibrant Pink Accent
COLOR_HIGHLIGHT_BLUE = (90, 80, 255)  # Royal Indigo Accent

def load_font(font_type, size):
    if font_type == "bold":
        paths = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica-Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.dfont"
        ]
    else:
        paths = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.dfont"
        ]
    
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_title = load_font("bold", 48)
font_subtitle = load_font("bold", 26)
font_body = load_font("regular", 28)
font_meta = load_font("bold", 22)
font_small = load_font("regular", 20)

def draw_gradient_line(draw, x0, y0, x1, y1, color_start, color_end, width=8):
    """Draws a horizontal gradient accent line."""
    steps = x1 - x0
    for i in range(steps):
        r = int(color_start[0] + (color_end[0] - color_start[0]) * (i / steps))
        g = int(color_start[1] + (color_end[1] - color_start[1]) * (i / steps))
        b = int(color_start[2] + (color_end[2] - color_start[2]) * (i / steps))
        draw.line([(x0 + i, y0), (x0 + i, y1)], fill=(r, g, b), width=width)

def wrap_text(text, font, max_width):
    """Helper to wrap text into lines fitting within max_width."""
    temp_img = Image.new("RGBA", (100, 100))
    temp_draw = ImageDraw.Draw(temp_img)
    words = text.split()
    lines = []
    curr_line = []
    
    for word in words:
        test_line = " ".join(curr_line + [word])
        bbox = temp_draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            curr_line.append(word)
        else:
            if curr_line:
                lines.append(" ".join(curr_line))
            curr_line = [word]
    if curr_line:
        lines.append(" ".join(curr_line))
    return lines

def create_slide(slide_num, total_slides, title, subtitle, bullets, highlight=None):
    # Create base canvas
    image = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(image)
    
    # 1. Slide header branding
    draw.text((70, 70), "BUILD SUNDAY // EPISODE 2", font=font_meta, fill=COLOR_TEXT_MUTED)
    draw.text((WIDTH - 130, 70), f"{slide_num:02d} / {total_slides:02d}", font=font_meta, fill=COLOR_HIGHLIGHT_PINK)
    
    # 2. Draw card overlay
    card_x0, card_y0 = 70, 140
    card_x1, card_y1 = WIDTH - 70, HEIGHT - 140
    draw.rounded_rectangle([(card_x0, card_y0), (card_x1, card_y1)], radius=16, fill=COLOR_CARD, outline=COLOR_BORDER, width=2)
    
    # 3. Draw gradient line at top of card
    draw_gradient_line(draw, card_x0 + 15, card_y0 + 10, card_x1 - 15, card_y0 + 10, COLOR_HIGHLIGHT_PINK, COLOR_HIGHLIGHT_BLUE, width=5)
    
    # 4. Title Section
    title_y = card_y0 + 50
    title_lines = title.split('\n')
    for line in title_lines:
        draw.text((110, title_y), line, font=font_title, fill=COLOR_TEXT_MAIN)
        title_y += 55
        
    # 5. Content Section
    content_y = title_y + 40
    if subtitle:
        draw.text((110, content_y), subtitle, font=font_subtitle, fill=COLOR_HIGHLIGHT_BLUE)
        content_y += 50
        
    for bullet in bullets:
        wrapped_lines = wrap_text(bullet, font_body, WIDTH - 260)
        first_line = True
        for line in wrapped_lines:
            if first_line:
                # Custom bullet icon (filled square)
                draw.rectangle([(110, content_y + 10), (120, content_y + 20)], fill=COLOR_HIGHLIGHT_PINK)
                draw.text((140, content_y), line, font=font_body, fill=COLOR_TEXT_MAIN)
                first_line = False
            else:
                draw.text((140, content_y), line, font=font_body, fill=COLOR_TEXT_MAIN)
            content_y += 42
        content_y += 15 # spacing between bullets
        
    # 6. Highlight badge
    if highlight:
        badge_y = HEIGHT - 210
        draw.rounded_rectangle([(110, badge_y), (WIDTH - 110, badge_y + 45)], radius=8, fill=COLOR_BG, outline=COLOR_BORDER, width=1)
        draw.text((130, badge_y + 10), highlight, font=font_meta, fill=COLOR_HIGHLIGHT_PINK)
        
    # 7. Slide footer branding
    draw.text((70, HEIGHT - 90), "@IMAGINARY_HUB", font=font_small, fill=COLOR_TEXT_MUTED)
    if slide_num < total_slides:
        draw.text((WIDTH - 210, HEIGHT - 90), "Swipe Left  ➔", font=font_small, fill=COLOR_TEXT_MUTED)
    else:
        draw.text((WIDTH - 240, HEIGHT - 90), "Check Repository 🔗", font=font_small, fill=COLOR_TEXT_MUTED)
        
    # Save image
    file_path = os.path.join(OUTPUT_DIR, f"slide_{slide_num}.png")
    image.save(file_path, "PNG")
    print(f"Generated {file_path}")

# Slides Content Definitions for PDF Q&A RAG System
slides = [
    {
        "title": "Build RAG from Scratch:\nLocal PDF Q&A System",
        "subtitle": "EPISODE 2: BUILD SUNDAY",
        "bullets": [
            "Stop sending private company documents to third-party APIs.",
            "Learn how to construct a 100% local, hybrid retrieval system.",
            "Leveraging Qdrant Vector DB, Sentence-Transformers, and Ollama.",
            "Swipe to inspect the step-by-step pipeline!"
        ],
        "highlight": "🔗 FULL CODE ON GITHUB: Imaginary-Hub-AI-Labs"
    },
    {
        "title": "The RAG Architecture:\nKeeping Your AI Grounded",
        "subtitle": "RETRIEVAL-AUGMENTED GENERATION",
        "bullets": [
            "LLMs hallucinate because they lack specific domain context.",
            "We extract text from your PDF, chunk it, and index it.",
            "When queries arrive, similarity searches locate matching blocks.",
            "Context is appended directly to the query, anchoring the model."
        ],
        "highlight": "Prevents AI hallucinations on private data"
    },
    {
        "title": "RAG vs. Fine-Tuning:\nWhich One Do You Need?",
        "subtitle": "ARCHITECTURAL TRADE-OFFS",
        "bullets": [
            "RAG: Low compute cost, real-time data updates, exact page citations.",
            "Fine-Tuning: High GPU compute cost, static cutoff date, black-box logic.",
            "RAG is best for database query, facts, and custom knowledge search.",
            "Fine-Tuning is best for modifying style, formatting, or parsing rules."
        ],
        "highlight": "Choose RAG for search, Fine-Tuning for style"
    },
    {
        "title": "Step 1 & 2: Ingestion,\nChunking & Overlaps",
        "subtitle": "PREPARING TEXT DATA",
        "bullets": [
            "We parse PDFs dynamically using PyMuPDF (fitz) extraction.",
            "Text is split into 1000-character logical chunks.",
            "We configure a 50-character boundary overlap.",
            "Overlap prevents sentence splits (e.g. cutting 'on-set') from losing meaning."
        ],
        "highlight": "IMPLEMENTED IN: src/ingestion.py"
    },
    {
        "title": "Step 3 & 4: Embeddings\n& Local Vector Storage",
        "subtitle": "INDEXING WITH QDRANT DB",
        "bullets": [
            "Sentence-Transformers convert text blocks into 384-dimensional vectors.",
            "We spin up a local Qdrant Vector Database container inside Docker.",
            "Vectors are saved and indexed locally for ultra-fast operations.",
            "Queries look up nearest-neighbor context blocks in under 5ms."
        ],
        "highlight": "Secure local indexing with zero cloud database costs"
    },
    {
        "title": "Step 5 & 6: Semantic Retrieval\n& Grounded Prompting",
        "subtitle": "LOCAL INFERENCE GENERATION",
        "bullets": [
            "Ollama serves Llama-3.2 (3B) locally on CPU or local GPU.",
            "We query Qdrant, fetch top chunks, and build a system prompt.",
            "Prompt: 'Answer ONLY using the provided text context...'",
            "Model acts strictly as a synthesizer, citing source page numbers."
        ],
        "highlight": "100% offline reasoning with local failovers"
    },
    {
        "title": "Clean Modular Architecture\nFor RAG Pipelines",
        "subtitle": "PROJECT FILE BREAKDOWN",
        "bullets": [
            "config.py - Setup parameters, model variables, and thresholds.",
            "ingestion.py - Document loaders, chunking rules, and upserts.",
            "retrieval.py - Query embedding, Qdrant search, and Llama generation.",
            "docker-compose.yml - Orchestrates Qdrant container volume states.",
            "main.py - CLI terminal interface boot and chatbot loop."
        ],
        "highlight": "Separated concern layers for high maintainability"
    },
    {
        "title": "Get the Free Codebase\n& Build Today!",
        "subtitle": "GET THE RESOURCES",
        "bullets": [
            "We open-sourced the complete PDF RAG system on GitHub.",
            "Repository: github.com/thejabirhussain/Imaginary-Hub-AI-Labs",
            "Follow setup steps to run Docker and Ollama in under 5 minutes.",
            "What architecture should we tackle next? Share below!"
        ],
        "highlight": "💡 Double tap, share, and save this post!"
    }
]

def main():
    total = len(slides)
    for idx, slide_data in enumerate(slides):
        create_slide(
            slide_num=idx + 1,
            total_slides=total,
            title=slide_data["title"],
            subtitle=slide_data["subtitle"],
            bullets=slide_data["bullets"],
            highlight=slide_data["highlight"]
        )
    print("All RAG carousel slides generated successfully!")

if __name__ == "__main__":
    main()
