import os
import re
import json
import numpy as np
import argparse
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, VideoClip, CompositeVideoClip, afx

# Settings
RESOLUTION = (1920, 1080)  # Horizontal Format (16:9 widescreen)
FPS = 24  # Matches RAG video frame rate
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

# ----------------------------------------------------
# 1. Color Grading LUT (Exposure & Contrast Correction)
# ----------------------------------------------------
LUT = np.zeros(256, dtype=np.uint8)
for i in range(256):
    val = float(i) / 255.0
    val = 0.5 + 1.06 * (val - 0.5)
    val = max(0.0, min(1.0, val))
    val = val ** 0.95
    LUT[i] = int(val * 255.0)

# ----------------------------------------------------
# 2. Header Drawing Overlay Helper
# ----------------------------------------------------
font_hdr = get_font(28)

def draw_header_on_frame(img_pil, header_text):
    draw = ImageDraw.Draw(img_pil)
    x = RESOLUTION[0] // 2
    y = 80
    
    # Calculate pill coordinates
    bbox = draw.textbbox((0, 0), header_text, font=font_hdr, anchor="mm")
    lw = bbox[2] - bbox[0]
    lh = bbox[3] - bbox[1]
    pad_x = 20
    pad_y = 10
    
    # Draw indigo pill background
    draw.rounded_rectangle(
        [(x - lw//2 - pad_x, y - lh//2 - pad_y), (x + lw//2 + pad_x, y + lh//2 + pad_y)],
        radius=10,
        fill=(90, 80, 255, 220)  # Indigo transparent
    )
    # Draw white text
    draw.text((x, y), header_text, font=font_hdr, fill=(255, 255, 255, 255), anchor="mm")

# ----------------------------------------------------
# 3. Main Frame Processing
# ----------------------------------------------------
def process_video_frame(get_frame, t, header_text):
    frame = get_frame(t)  # shape (1080, 1920, 3)
    graded = LUT[frame]
    img_pil = Image.fromarray(graded)
    draw_header_on_frame(img_pil, header_text)
    return np.array(img_pil)

# ----------------------------------------------------
# 4. Dynamic Subtitle Overlay Generator
# ----------------------------------------------------
font_sub = get_font(36)

def get_subtitle_generator(text, duration):
    max_w = 1600  # Wrap boundary
    words = text.split()
    lines = []
    curr_line = []
    
    temp_img = Image.new("RGBA", (100, 100))
    temp_draw = ImageDraw.Draw(temp_img)
    
    for word in words:
        test_line = " ".join(curr_line + [word])
        bbox = temp_draw.textbbox((0, 0), test_line, font=font_sub)
        w = bbox[2] - bbox[0]
        if w <= max_w:
            curr_line.append(word)
        else:
            if curr_line:
                lines.append(" ".join(curr_line))
            curr_line = [word]
    if curr_line:
        lines.append(" ".join(curr_line))
        
    num_lines = len(lines)
    
    def frame_gen(t):
        img = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        line_height = 50
        start_y = 960 - ((num_lines - 1) * line_height) // 2
        
        for idx, line_text in enumerate(lines):
            y = start_y + idx * line_height
            x = RESOLUTION[0] // 2
            
            # Shadow
            shadow_offset = 2
            draw.text((x + shadow_offset, y + shadow_offset), line_text, font=font_sub, fill=(0, 0, 0, 220), anchor="mm")
            # Text
            draw.text((x, y), line_text, font=font_sub, fill=(255, 255, 255, 255), anchor="mm")
            
        np_arr = np.array(img)
        rgb = np_arr[:, :, :3]
        alpha = np_arr[:, :, 3].astype(float) / 255.0
        return rgb, alpha
        
    return frame_gen

# ----------------------------------------------------
# 5. SRT Transcript Parser
# ----------------------------------------------------
def parse_srt(srt_path, clip_start, clip_end):
    """
    Parses standard SRT file and extracts subtitles that overlap
    with [clip_start, clip_end], shifting them relative to clip_start.
    """
    subtitle_entries = []
    if not os.path.exists(srt_path):
        print(f"Warning: SRT path {srt_path} not found.")
        return subtitle_entries

    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split SRT by double newlines or similar block endings
    blocks = re.split(r'\n\s*\n', content.strip())
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            # Lines[0] is index, Lines[1] is timing, rest is subtitle text
            timing = lines[1]
            text = " ".join(lines[2:]).strip()
            
            # Parse timeline timings e.g., 00:01:08,560 --> 00:01:15,440
            m = re.match(r'(\d+):(\d+):(\d+),(\d+)\s+-->\s+(\d+):(\d+):(\d+),(\d+)', timing)
            if m:
                start_sec = int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3)) + int(m.group(4))/1000.0
                end_sec = int(m.group(5))*3600 + int(m.group(6))*60 + int(m.group(7)) + int(m.group(8))/1000.0
                
                # Check overlap
                s = max(start_sec, clip_start)
                e = min(end_sec, clip_end)
                
                if e > s + 0.1:
                    subtitle_entries.append({
                        "start": s - clip_start,
                        "end": e - clip_start,
                        "text": text
                    })
    return subtitle_entries

# ----------------------------------------------------
# 6. Clip Processing Pipeline
# ----------------------------------------------------
def create_reel(config, is_preview, no_subtitles=False):
    print("\n" + "="*50)
    print(f"Generating Reel: {config['name']}")
    print("="*50)
    
    # Check source video path
    if not os.path.exists(config["video_path"]):
        print(f"Error: Source video file not found at {config['video_path']}")
        return
        
    start = config["start_time"]
    duration = config["end_time"] - start
    if is_preview:
        duration = min(10.0, duration)
    
    print(f"Loading source: {config['video_path']}")
    raw_clip = VideoFileClip(config["video_path"])
    
    print(f"Slicing clip from {start}s to {start + duration}s...")
    sub_clip = raw_clip.subclipped(start, start + duration)
    sub_clip = sub_clip.with_effects([afx.AudioFadeIn(0.05), afx.AudioFadeOut(0.05)])
    
    print("Processing video frames (grade & header)...")
    processed_clip = sub_clip.transform(lambda get_frame, t: process_video_frame(get_frame, t, config["header"]))
    
    # Add subtitles
    subtitle_clips = []
    if not no_subtitles:
        print("Parsing SRT transcript and building subtitle track...")
        subtitles = parse_srt(config["transcript_path"], start, start + duration)
        
        for sub in subtitles:
            s, e, text = sub["start"], sub["end"], sub["text"]
            dur = e - s
            if dur > 0.2:
                gen = get_subtitle_generator(text, dur)
                rgb, alpha = gen(0.0)
                
                color_clip = VideoClip(lambda t: rgb, duration=dur)
                mask_clip = VideoClip(lambda t: alpha, duration=dur, is_mask=True)
                sub_clip_layer = color_clip.with_mask(mask_clip).with_start(s)
                subtitle_clips.append(sub_clip_layer)
            
    print(f"Compositing final clip with {len(subtitle_clips)} subtitle blocks...")
    final_video = CompositeVideoClip([processed_clip] + subtitle_clips, size=RESOLUTION)
    final_video = final_video.with_duration(duration)
    
    output_path = config["output_preview"] if is_preview else config["output"]
    print(f"Exporting video to {output_path}...")
    
    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec="h264_videotoolbox",  # Apple Silicon acceleration
        audio_codec="aac",
        temp_audiofile=f"temp-audio-{config['name'].lower().replace(' ', '_')}.m4a",
        remove_temp=True,
        write_logfile=False,
        threads=8,
        bitrate="8000k"
    )
    print(f"Success! Export completed: {output_path}")

# ----------------------------------------------------
# Main Entry Point
# ----------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate Widescreen Educational Reels from RAG Sunday Episode 2")
    parser.add_argument("--preview", action="store_true", help="Render a 10-second preview of each selected reel")
    parser.add_argument("--clip", choices=["1", "2", "3", "4", "all"], default="all", 
                        help="Select a specific clip (1: LLM Types, 2: RAG Whiteboard, 3: RAG vs Fine-Tuning, 4: Chunk Overlap, all)")
    parser.add_argument("--no-subtitles", action="store_true", help="Disable subtitles entirely on the exported video")
    args = parser.parse_args()
    
    configs = {
        "1": {
            "name": "LLM Types Explained",
            "video_path": "Building RAG from Scratch - PDF Q&A System (Build Sunday Ep 2).mov",
            "transcript_path": "rag_audio.srt",
            "start_time": 68.0,    # ~1:08
            "end_time": 270.0,     # ~4:30
            "header": "BUILD SUNDAY // EPISODE 2",
            "output": "rag_llm_classification.mp4",
            "output_preview": "rag_llm_classification_preview.mp4"
        },
        "2": {
            "name": "RAG Whiteboard Architecture",
            "video_path": "Building RAG from Scratch - PDF Q&A System (Build Sunday Ep 2).mov",
            "transcript_path": "rag_audio.srt",
            "start_time": 350.0,   # ~5:50
            "end_time": 530.0,     # ~8:50
            "header": "RAG SYSTEM ARCHITECTURE",
            "output": "rag_whiteboard_architecture.mp4",
            "output_preview": "rag_whiteboard_architecture_preview.mp4"
        },
        "3": {
            "name": "RAG vs Fine-Tuning",
            "video_path": "Building RAG from Scratch - PDF Q&A System (Build Sunday Ep 2).mov",
            "transcript_path": "rag_audio.srt",
            "start_time": 810.0,   # ~13:30
            "end_time": 1120.0,    # ~18:40
            "header": "RAG VS FINE-TUNING // TECH DECISIONS",
            "output": "rag_vs_finetuning.mp4",
            "output_preview": "rag_vs_finetuning_preview.mp4"
        },
        "4": {
            "name": "Chunk Overlapping",
            "video_path": "Building RAG from Scratch - PDF Q&A System (Build Sunday Ep 2).mov",
            "transcript_path": "rag_audio.srt",
            "start_time": 2220.0,  # ~37:00
            "end_time": 2355.0,    # ~39:15
            "header": "INGESTION // CHUNKING & OVERLAP",
            "output": "rag_chunk_overlapping.mp4",
            "output_preview": "rag_chunk_overlapping_preview.mp4"
        }
    }
    
    selected_keys = ["1", "2", "3", "4"] if args.clip == "all" else [args.clip]
    
    for key in selected_keys:
        create_reel(configs[key], args.preview, args.no_subtitles)

if __name__ == "__main__":
    main()
