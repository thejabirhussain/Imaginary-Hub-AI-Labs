import os
from PIL import Image, ImageDraw, ImageFont

# Set up output directory
OUTPUT_DIR = "carousel_slides"
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
                # If dfont or regular font, try reading it
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

def create_slide(slide_num, total_slides, title, subtitle, bullets, highlight=None, is_cover=False):
    # Create base canvas
    image = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(image)
    
    # 1. Slide header branding
    draw.text((70, 70), "BUILD SUNDAY // EPISODE 1", font=font_meta, fill=COLOR_TEXT_MUTED)
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
                # Custom bullet icon (filled circle/square)
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

# Slides Content Definitions
slides = [
    {
        "title": "How to Build a Smart\nQ&A Chatbot with Fallback",
        "subtitle": "EPISODE 1: BUILD SUNDAY",
        "bullets": [
            "Want to build a production-grade terminal chat agent?",
            "Learn how we integrate Conversational Memory, Chunk-based Streaming, Tiktoken calculations, and error fallback.",
            "We'll failover seamlessly from OpenAI API to a local Llama model running on your computer.",
            "Swipe to inspect the architecture and modules!"
        ],
        "highlight": "🔗 FULL CODE ON GITHUB: Build_Sunday"
    },
    {
        "title": "LLMs are State-Less!\nSolving the Memory Problem",
        "subtitle": "THE STATELESS CHALLENGE",
        "bullets": [
            "By default, large language model APIs are completely stateless.",
            "If you say 'My name is Jabir', and then ask 'What is my name?', the model has already forgotten the context.",
            "Solution: We maintain a structured conversation history list in a JSON-like format.",
            "Every user query is wrapped together with historical memory and sent back as a cumulative payload."
        ],
        "highlight": "IMPLEMENTED IN: src/conversation.py"
    },
    {
        "title": "Pillar 1: Memory Loop &\nContext Windows",
        "subtitle": "DYNAMIC MESSAGE MANAGEMENT",
        "bullets": [
            "We store message structures with 'role' (user/assistant) and 'content' fields.",
            "But message payloads cannot grow forever. Context window sizes are finite.",
            "Our client enforces a sliding window configuration: automatically summarizing or removing old logs.",
            "This guarantees that token usage and cost remain predictable."
        ],
        "highlight": "Saves API usage and respects model limits"
    },
    {
        "title": "Pillar 2: Instant Responsiveness\nVia Token Streaming",
        "subtitle": "IMPROVING THE USER EXPERIENCE",
        "bullets": [
            "Normal API requests block execution and make the user wait for the entire response to load.",
            "We integrate stream=True in the OpenAI client to stream token chunks in real-time.",
            "As the model computes, we print chunks to the terminal instantly.",
            "Zero loading spinners. Fluid, human-like typewriter output."
        ],
        "highlight": "Provides premium, low-latency responsiveness"
    },
    {
        "title": "Pillar 3: Tiktoken &\nDynamic Cost Calculation",
        "subtitle": "REAL-TIME BILL TRACKING",
        "bullets": [
            "Keep an eye on API expenses. We track prompt and completion token sizes dynamically.",
            "We use tiktoken (cl100k_base encoder) to count query tokens locally before sending.",
            "Response tokens are counted chunk-by-chunk during the stream loop.",
            "Computes exact cost in USD based on rates ($0.15/1M input for gpt-4o-mini)."
        ],
        "highlight": "IMPLEMENTED IN: src/token_counter.py"
    },
    {
        "title": "Pillar 4: Zero-Downtime\nLocal Fallback",
        "subtitle": "HYBRID CLOUD & LOCAL MODEL DESIGN",
        "bullets": [
            "What if OpenAI API is down, rate-limited, or you run out of credits?",
            "Our code intercepts connection and API credit errors gracefully.",
            "Fallback Action: Instantly boots a local Llama-3 model using Ollama on your computer.",
            "Seamless CLI failover without crashing the active chat session!"
        ],
        "highlight": "IMPLEMENTED IN: src/api_client.py"
    },
    {
        "title": "Clean Modular Architecture\nFor Code Maintainability",
        "subtitle": "PROJECT STRUCTURE",
        "bullets": [
            "config.py - Loads env parameters, default limits, temperatures.",
            "api_client.py - Deals with OpenAI & Ollama client fallbacks.",
            "conversation.py - Formats history and updates message lists.",
            "token_counter.py - Tiktoken calculator & cost trackers.",
            "main.py - Boots terminal CLI and manages the chat loop."
        ],
        "highlight": "Elegantly separated layers of concern"
    },
    {
        "title": "Clone, Configure, and\nBuild This Sunday!",
        "subtitle": "GET THE COMPLETE CODE",
        "bullets": [
            "We have open-sourced the complete codebase on GitHub.",
            "Go to: github.com/thejabirhussain/Build_Sunday",
            "Copy .env.example to .env, insert your API keys, and run 'python src/main.py' to start chatting.",
            "What features should we add next? Tell me in the comment section below!"
        ],
        "highlight": "💡 Double tap, share, and subscribe to Imaginary Hub!"
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
    print("All carousel slides generated successfully!")

if __name__ == "__main__":
    main()
