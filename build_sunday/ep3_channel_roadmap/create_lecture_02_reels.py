import os
import re
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, VideoClip, CompositeVideoClip, afx

# Settings
RESOLUTION = (1920, 1080)  # Horizontal Format (16:9 widescreen)
FPS = 24  # Matches lecture video frame rate
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

# 1. Color Grading LUT
LUT = np.zeros(256, dtype=np.uint8)
for i in range(256):
    val = float(i) / 255.0
    val = 0.5 + 1.06 * (val - 0.5)
    val = max(0.0, min(1.0, val))
    val = val ** 0.95
    LUT[i] = int(val * 255.0)

# 2. Header Drawing Overlay Helper
font_hdr = get_font(28)

def draw_header_on_frame(img_pil, header_text):
    draw = ImageDraw.Draw(img_pil)
    x = RESOLUTION[0] // 2
    y = 80
    
    bbox = draw.textbbox((0, 0), header_text, font=font_hdr, anchor="mm")
    lw = bbox[2] - bbox[0]
    lh = bbox[3] - bbox[1]
    pad_x = 20
    pad_y = 10
    
    draw.rounded_rectangle(
        [(x - lw//2 - pad_x, y - lh//2 - pad_y), (x + lw//2 + pad_x, y + lh//2 + pad_y)],
        radius=10,
        fill=(90, 80, 255, 220)
    )
    draw.text((x, y), header_text, font=font_hdr, fill=(255, 255, 255, 255), anchor="mm")

# 3. Main Frame Processing
def process_video_frame(get_frame, t, header_text):
    frame = get_frame(t)
    graded = LUT[frame]
    img_pil = Image.fromarray(graded)
    draw_header_on_frame(img_pil, header_text)
    return np.array(img_pil)

# 4. Dynamic Subtitle Overlay Generator
font_sub = get_font(36)

def get_subtitle_generator(text, duration):
    max_w = 1600
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
            shadow_offset = 2
            draw.text((x + shadow_offset, y + shadow_offset), line_text, font=font_sub, fill=(0, 0, 0, 220), anchor="mm")
            draw.text((x, y), line_text, font=font_sub, fill=(255, 255, 255, 255), anchor="mm")
            
        np_arr = np.array(img)
        return np_arr[:, :, :3], np_arr[:, :, 3].astype(float) / 255.0
        
    return frame_gen

# 5. Transcript Parser
def parse_transcript(transcript_path, clip_start, clip_end, transcript_offset=0.0):
    pattern = re.compile(r'\[(?:(\d+):)?(\d+):(\d+)\s+-->\s+(?:(\d+):)?(\d+):(\d+)\]\s*(.*)')
    subtitle_entries = []
    
    if not os.path.exists(transcript_path):
        print(f"Warning: Transcript path {transcript_path} not found.")
        return subtitle_entries
        
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            m = pattern.match(line.strip())
            if m:
                sh_h, sh_m, sh_s = m.group(1), m.group(2), m.group(3)
                start_sec = (int(sh_h) * 3600 if sh_h else 0) + int(sh_m) * 60 + int(sh_s) + transcript_offset
                
                eh_h, eh_m, eh_s = m.group(4), m.group(5), m.group(6)
                end_sec = (int(eh_h) * 3600 if eh_h else 0) + int(eh_m) * 60 + int(eh_s) + transcript_offset
                
                text = m.group(7).strip()
                s = max(start_sec, clip_start)
                e = min(end_sec, clip_end)
                
                if e > s + 0.1:
                    subtitle_entries.append({
                        "start": s - clip_start,
                        "end": e - clip_start,
                        "text": text
                    })
    return subtitle_entries

# 6. Clip Processing Pipeline
def create_reel(config, is_preview, no_subtitles=False):
    print("\n" + "="*50)
    print(f"Generating Reel (Horizontal): {config['name']}")
    print("="*50)
    
    if not os.path.exists(config["video_path"]):
        print(f"Error: Source video file not found at {config['video_path']}")
        return
        
    start = config["start_time"]
    duration = config["end_time"] - start
    if is_preview:
        duration = min(10.0, duration)
    
    raw_clip = VideoFileClip(config["video_path"])
    sub_clip = raw_clip.subclipped(start, start + duration)
    sub_clip = sub_clip.with_effects([afx.AudioFadeIn(0.05), afx.AudioFadeOut(0.05)])
    
    processed_clip = sub_clip.transform(lambda get_frame, t: process_video_frame(get_frame, t, config["header"]))
    
    subtitle_clips = []
    if not no_subtitles:
        subtitles = parse_transcript(config["transcript_path"], start, start + duration, config.get("transcript_offset", 0.0))
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
            
    final_video = CompositeVideoClip([processed_clip] + subtitle_clips, size=RESOLUTION)
    final_video = final_video.with_duration(duration)
    
    output_path = config["output_preview"] if is_preview else config["output"]
    print(f"Exporting video to {output_path}...")
    
    final_video.write_videofile(
        output_path,
        fps=FPS,
        codec="h264_videotoolbox",
        audio_codec="aac",
        temp_audiofile=f"temp-audio-{config['name'].lower().replace(' ', '_')}.m4a",
        remove_temp=True,
        write_logfile=False,
        threads=8,
        bitrate="8000k"
    )
    print(f"Success! Export completed: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate Widescreen Educational Reels from Linear Algebra Lectures")
    parser.add_argument("--preview", action="store_true", help="Render a 10-second preview of each selected reel")
    parser.add_argument("--clip", choices=["A", "B", "C", "all"], default="all", help="Select a specific clip")
    parser.add_argument("--no-subtitles", action="store_true", help="Disable subtitles entirely")
    args = parser.parse_args()
    
    configs = {
        "A": {
            "name": "Bad Equations",
            "video_path": "Linear Algebra 02.mov",
            "transcript_path": "lecture_02_transcript.txt",
            "start_time": 1055,  # 17:35
            "end_time": 1176,    # 19:36
            "transcript_offset": 0.0,
            "header": "LINEAR ALGEBRA // BAD EQUATIONS",
            "output": "reel_bad_equations.mp4",
            "output_preview": "reel_bad_equations_preview.mp4"
        },
        "B": {
            "name": "Zero Pivots",
            "video_path": "Linear Algebra 02.mov",
            "transcript_path": "lecture_02_transcript.txt",
            "start_time": 1274,  # 21:14
            "end_time": 1394,    # 23:14
            "transcript_offset": 0.0,
            "header": "LINEAR ALGEBRA // PIVOTS",
            "output": "reel_zero_pivots.mp4",
            "output_preview": "reel_zero_pivots_preview.mp4"
        },
        "C": {
            "name": "Elimination Matrices",
            "video_path": "Linear Algebra 02.mov",
            "transcript_path": "lecture_02_transcript.txt",
            "start_time": 2119,  # 35:19
            "end_time": 2229,    # 37:09
            "transcript_offset": 0.0,
            "header": "MATRIX ALGEBRA // ELIMINATION",
            "output": "reel_elimination_matrices.mp4",
            "output_preview": "reel_elimination_matrices_preview.mp4"
        },
        "D": {
            "name": "Inverse Matrices",
            "video_path": "Linear Algebra 02.mov",
            "transcript_path": "lecture_02_audio.vtt",
            "start_time": 3070,  # 51:10
            "end_time": 3131,    # 52:11
            "transcript_offset": 0.0,
            "header": "MATRIX ALGEBRA // INVERSE",
            "output": "reel_inverse_matrices.mp4",
            "output_preview": "reel_inverse_matrices_preview.mp4"
        }
    }
    
    selected_keys = ["A", "B", "C", "D"] if args.clip == "all" else [args.clip]
    for key in selected_keys:
        create_reel(configs[key], args.preview, args.no_subtitles)

if __name__ == "__main__":
    main()
