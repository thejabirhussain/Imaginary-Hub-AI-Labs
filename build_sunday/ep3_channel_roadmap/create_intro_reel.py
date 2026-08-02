import os
import json
import numpy as np
import argparse
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, VideoClip, CompositeVideoClip, afx

# Settings
RESOLUTION = (1080, 1920) # Vertical Reel Format
FPS = 24 # Matches original video frame rate
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

# ----------------------------------------------------
# 1. Color Grading LUT
# ----------------------------------------------------
# A color grade profile maps raw pixel colors using lookup tables.
# This curve adjusts exposure, boosting highlights and mapping curves.
LUT = np.zeros(256, dtype=np.uint8)
for i in range(256):
    val = float(i) / 255.0
    val = 0.5 + 1.06 * (val - 0.5)
    val = max(0.0, min(1.0, val))
    val = val ** 0.95
    LUT[i] = int(val * 255.0)

# ----------------------------------------------------
# 2. Pillow Clean Header Overlay Helper
# ----------------------------------------------------
font_hdr = get_font(36)
def draw_header_on_frame(img_pil):
    draw = ImageDraw.Draw(img_pil)
    text = "BUILD SUNDAY // EPISODE 1"
    x = RESOLUTION[0] // 2
    y = 150
    
    # Calculate pill coordinates
    bbox = draw.textbbox((0, 0), text, font=font_hdr, anchor="mm")
    lw = bbox[2] - bbox[0]
    lh = bbox[3] - bbox[1]
    pad_x = 25
    pad_y = 15
    
    # Draw indigo pill background
    draw.rounded_rectangle(
        [(x - lw//2 - pad_x, y - lh//2 - pad_y), (x + lw//2 + pad_x, y + lh//2 + pad_y)],
        radius=12,
        fill=(90, 80, 255, 220) # Indigo transparent
    )
    # Draw white text
    draw.text((x, y), text, font=font_hdr, fill=(255, 255, 255, 255), anchor="mm")

# ----------------------------------------------------
# 3. Main Frame Processing (Crop, Grade, Resize, Header)
# ----------------------------------------------------
def process_video_frame(get_frame, t):
    frame = get_frame(t) # shape (1080, 1920, 3)
    
    # A. Color Grade
    graded = LUT[frame]
    
    # B. Crop Center 9:16 (x: 657 to 1264)
    cropped = graded[:, 657:1264]
    
    # C. Resize to 1080x1920
    img_pil = Image.fromarray(cropped)
    resized = img_pil.resize(RESOLUTION, Image.Resampling.LANCZOS)
    
    # D. Draw Static Header Overlay
    draw_header_on_frame(resized)
    
    return np.array(resized)

# ----------------------------------------------------
# 4. Dynamic Subtitle Overlay Generator
# ----------------------------------------------------
font_sub = get_font(55)

def get_subtitle_generator(text, duration):
    max_w = 900
    words = text.split()
    lines = []
    curr_line = []
    
    # Measure line wraps
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
        # Transparent canvas
        img = Image.new("RGBA", RESOLUTION, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        line_height = 80
        # Position in lower third
        start_y = 1450 - ((num_lines - 1) * line_height) // 2
        
        for idx, line_text in enumerate(lines):
            y = start_y + idx * line_height
            x = RESOLUTION[0] // 2
            
            # Pill capsule background for subtitle readability
            bbox = draw.textbbox((0, 0), line_text, font=font_sub, anchor="mm")
            lw = bbox[2] - bbox[0]
            lh = bbox[3] - bbox[1]
            pad_x = 25
            pad_y = 15
            
            draw.rounded_rectangle(
                [(x - lw//2 - pad_x, y - lh//2 - pad_y), (x + lw//2 + pad_x, y + lh//2 + pad_y)],
                radius=12,
                fill=(0, 0, 0, 160)
            )
            # White text
            draw.text((x, y), line_text, font=font_sub, fill=(255, 255, 255, 255), anchor="mm")
            
        np_arr = np.array(img)
        rgb = np_arr[:, :, :3]
        alpha = np_arr[:, :, 3].astype(float) / 255.0
        return rgb, alpha
        
    return frame_gen

def main():
    parser = argparse.ArgumentParser(description="Create Intro Reel showing Speaker Face")
    parser.add_argument("--preview", action="store_true", help="Render a 5-second preview instead of full 90s")
    args = parser.parse_args()
    
    video_path = "OPEN API CRASH COURSE SMART QA.mov"
    segments_path = "qa_segments.json"
    
    print("Loading original video...")
    raw_clip = VideoFileClip(video_path)
    
    # 90-second duration for full reel
    target_duration = 5.0 if args.preview else 90.0
    print(f"Creating a {target_duration}s clip from start...")
    
    # Cut talking head introduction (0:00 to 1:30)
    intro_clip = raw_clip.subclipped(0, target_duration)
    
    # Smooth audio transitions (micro fades to remove microphone clicks)
    intro_clip = intro_clip.with_effects([afx.AudioFadeIn(0.05), afx.AudioFadeOut(0.05)])
    
    # Apply transformation to center-crop, color-grade and add header
    print("Processing video frames (crop & color grade)...")
    processed_clip = intro_clip.transform(lambda get_frame, t: process_video_frame(get_frame, t))
    
    # Prepare subtitles from JSON
    print("Adding subtitles track...")
    with open(segments_path) as f:
        segments_data = json.load(f)
        
    subtitle_clips = []
    for seg in segments_data["segments"]:
        s, e, text = seg["start"], seg["end"], seg["text"]
        if s >= target_duration:
            continue
        
        clip_end = min(target_duration, e)
        dur = clip_end - s
        if dur > 0.2:
            # Create a subtitle generator clip for this timing block
            gen = get_subtitle_generator(text.strip(), dur)
            
            # Static frames pre-generation for speed
            rgb, alpha = gen(0.0)
            color_clip = VideoClip(lambda t: rgb, duration=dur)
            mask_clip = VideoClip(lambda t: alpha, duration=dur, is_mask=True)
            sub_clip = color_clip.with_mask(mask_clip).with_start(s)
            
            subtitle_clips.append(sub_clip)
            
    # Combine processed video with all subtitle clips
    final_video = CompositeVideoClip([processed_clip] + subtitle_clips, size=RESOLUTION)
    final_video = final_video.with_duration(target_duration)
    
    output_filename = "qa_intro_reel_preview.mp4" if args.preview else "qa_intro_reel.mp4"
    print(f"Exporting to {output_filename}...")
    
    final_video.write_videofile(
        output_filename,
        fps=FPS,
        codec="h264_videotoolbox", # Fast hardware encoding on Apple Silicon
        audio_codec="aac",
        temp_audiofile="temp-audio-intro.m4a",
        remove_temp=True,
        write_logfile=False,
        threads=8,
        bitrate="8000k"
    )
    print(f"Reel exported successfully: {output_filename}")

if __name__ == "__main__":
    main()
