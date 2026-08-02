import os
from PIL import Image, ImageDraw, ImageFont

# Set up output directory
OUTPUT_DIR = "carousel_slides_la"
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

font_title = load_font("bold", 44)
font_subtitle = load_font("bold", 24)
font_body = load_font("regular", 26)
font_meta = load_font("bold", 20)
font_small = load_font("regular", 18)

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
    draw.text((70, 70), "FOUNDATIONS OF AI // LINEAR ALGEBRA", font=font_meta, fill=COLOR_TEXT_MUTED)
    draw.text((WIDTH - 130, 70), f"{slide_num:02d} / {total_slides:02d}", font=font_meta, fill=COLOR_HIGHLIGHT_PINK)
    
    # 2. Draw card overlay
    card_x0, card_y0 = 70, 140
    card_x1, card_y1 = WIDTH - 70, HEIGHT - 140
    draw.rounded_rectangle([(card_x0, card_y0), (card_x1, card_y1)], radius=16, fill=COLOR_CARD, outline=COLOR_BORDER, width=2)
    
    # 3. Draw gradient line at top of card
    draw_gradient_line(draw, card_x0 + 15, card_y0 + 10, card_x1 - 15, card_y0 + 10, COLOR_HIGHLIGHT_PINK, COLOR_HIGHLIGHT_BLUE, width=5)
    
    # 4. Title Section
    title_y = card_y0 + 45
    title_lines = title.split('\n')
    for line in title_lines:
        draw.text((110, title_y), line, font=font_title, fill=COLOR_TEXT_MAIN)
        title_y += 50
        
    # 5. Content Section
    content_y = title_y + 35
    if subtitle:
        draw.text((110, content_y), subtitle, font=font_subtitle, fill=COLOR_HIGHLIGHT_BLUE)
        content_y += 45
        
    for bullet in bullets:
        wrapped_lines = wrap_text(bullet, font_body, WIDTH - 260)
        first_line = True
        for line in wrapped_lines:
            if first_line:
                # Custom bullet icon (filled circle/square)
                draw.rectangle([(110, content_y + 8), (120, content_y + 18)], fill=COLOR_HIGHLIGHT_PINK)
                draw.text((140, content_y), line, font=font_body, fill=COLOR_TEXT_MAIN)
                first_line = False
            else:
                draw.text((140, content_y), line, font=font_body, fill=COLOR_TEXT_MAIN)
            content_y += 38
        content_y += 12 # spacing between bullets
        
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
        draw.text((WIDTH - 240, HEIGHT - 90), "Watch Full Lecture 🔗", font=font_small, fill=COLOR_TEXT_MUTED)
        
    # Save image
    file_path = os.path.join(OUTPUT_DIR, f"slide_{slide_num}.png")
    image.save(file_path, "PNG")
    print(f"Generated {file_path}")

# Slides Content Definitions
slides = [
    {
        "title": "Linear Algebra for AI:\nThe Matrix Picture & Elimination",
        "subtitle": "LECTURE 02: MATH FOUNDATIONS",
        "bullets": [
            "In Lecture 01, we explored the Row and Column pictures. Now, it's time for the ultimate tool: The Matrix Picture.",
            "Are you coding ML algorithms blind? Behind every neural network layer and weights tensor is pure, visual mathematics.",
            "Swipe to learn the computational engine that solves complex systems of equations! 👉"
        ],
        "highlight": "🔗 FULL 56-MIN LECTURE ON YOUTUBE: IMAGINARY HUB"
    },
    {
        "title": "The Matrix Picture:\nAx = b Formulation",
        "subtitle": "SYSTEMS AT SCALE",
        "bullets": [
            "To solve systems of equations at scale, we must write them in Matrix form: Ax = b.",
            "Instead of visualizing high-dimensional plane intersections, we rely on systematic matrix operations.",
            "By taking a coefficient matrix A and an unknown vector x, we can transform equations into highly optimized data structures."
        ],
        "highlight": "The foundation of deep learning weight matrices"
    },
    {
        "title": "Gaussian Elimination:\nFinding the Upper Triangular",
        "subtitle": "THE ALGORITHM",
        "bullets": [
            "How do we actually solve Ax = b? We use Gaussian Elimination.",
            "We systematically subtract multiples of rows from the rows below them to eliminate variables.",
            "The goal is to turn all numbers below the diagonal into zeros, forming an Upper Triangular matrix (U).",
            "Once U is found, we can quickly solve for x, y, and z using Back Substitution."
        ],
        "highlight": "Transforms complex systems into easy-to-solve triangles"
    },
    {
        "title": "What Makes a 'Bad' Equation?",
        "subtitle": "PARALLEL PLANES & VECTORS",
        "bullets": [
            "Not all systems of equations have a unique solution. Some are mathematically 'bad'.",
            "In the Row Picture, a bad equation means two planes are completely parallel—they never intersect!",
            "In the Column Picture, it means vectors are parallel and cannot combine to form the target space.",
            "When this happens, the system crashes. There is no unique point of intersection."
        ],
        "highlight": "Identifying when your ML model will fail to converge"
    },
    {
        "title": "Zero Pivots:\nTemporary vs. Permanent Failure",
        "subtitle": "MATRICES WITH ZERO DIAGONALS",
        "bullets": [
            "During elimination, the diagonal numbers are called 'Pivots'. A pivot can NEVER be zero.",
            "Temporary Failure: You hit a zero pivot, but there is a non-zero number below it. Fix: Swap the rows and continue!",
            "Permanent Failure: You hit a zero pivot at the very bottom. You cannot swap. The matrix is Singular."
        ],
        "highlight": "Singular matrices crash neural network training loops 🚨"
    },
    {
        "title": "The Augmented Matrix:\nKeeping Things Balanced",
        "subtitle": "[ A | b ]",
        "bullets": [
            "When doing elimination on A, we must also apply the exact same operations to the target vector b.",
            "We stick them together into an 'Augmented Matrix' [ A | b ].",
            "Whatever row operation you perform on the left side, you carry it over to the right side seamlessly."
        ],
        "highlight": "Maintaining equation parity"
    },
    {
        "title": "Elimination Matrices:\nMath Meets Code",
        "subtitle": "ALGEBRAIC TRANSFORMATIONS",
        "bullets": [
            "We don't just subtract rows manually like in high school. We write row operations as Matrix Multiplications!",
            "An Elimination Matrix (e.g., E21) subtracts a multiple of row 1 from row 2.",
            "Multiplying E21 * A mathematically executes the row operation.",
            "This unified algebraic form lets GPUs execute row operations in parallel!"
        ],
        "highlight": "Why GPUs are built for matrix math 💻"
    },
    {
        "title": "Permutation Matrices:\nSwapping Rows",
        "subtitle": "FIXING TEMPORARY FAILURES",
        "bullets": [
            "Remember Temporary Failures? We fix them by swapping rows.",
            "A Permutation Matrix (P) is just the Identity matrix with its rows swapped.",
            "Multiplying P * A instantly executes a row swap operation on your dataset.",
            "This elegant math avoids writing messy procedural swap code!"
        ],
        "highlight": "Row swaps executed via pure matrix multiplication"
    },
    {
        "title": "Fundamental Laws:\nMatrix Rules",
        "subtitle": "MATHEMATICAL PROPERTIES",
        "bullets": [
            "Matrix Math has strict rules you must obey:",
            "Non-Commutative: Order matters! AB is NOT equal to BA. (Applying elimination steps in reverse changes the result).",
            "Associative: Grouping does not matter! A(BC) = (AB)C.",
            "We can safely group elimination matrices together without breaking the logic."
        ],
        "highlight": "Order matters when transforming dimensions"
    },
    {
        "title": "Finding the Inverse:\nThe Gauss-Jordan Method",
        "subtitle": "WHEN E * A = I",
        "bullets": [
            "How do we calculate the Inverse matrix? We use Gauss-Jordan Elimination.",
            "Set up an Augmented Matrix with the Identity Matrix: [A | I].",
            "Perform row operations until the left side becomes Identity [I]. The right side will magically transform into the Inverse [A_inv]!",
            "Mathematically, we are tracking all our elimination matrices (E) applied to A, so E * A = I."
        ],
        "highlight": "The ultimate tool for solving complex linear equations!"
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
    print("All lecture slides generated successfully!")

if __name__ == "__main__":
    main()
