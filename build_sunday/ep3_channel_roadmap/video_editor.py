import os
import json
import numpy as np
import argparse
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, VideoClip, CompositeVideoClip, concatenate_videoclips, afx

# Global settings
RESOLUTION = (1620, 1080)
FPS = 30
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def get_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

# ----------------------------------------------------
# 1. Subtle Color Correction (Brightness/Contrast)
# ----------------------------------------------------
# Precompute Look-Up Table (LUT) for fast element-wise mapping
LUT = np.zeros(256, dtype=np.uint8)
for i in range(256):
    val = float(i) / 255.0
    val = 0.5 + 1.06 * (val - 0.5)
    val = max(0.0, min(1.0, val))
    val = val ** 0.95
    LUT[i] = int(val * 255.0)

def grade_frame(frame):
    """
    Applies a natural, clean exposure and contrast correction.
    Uses precomputed LUT for maximum performance.
    """
    return LUT[frame]

def fl_grade_filter(get_frame, t):
    frame = get_frame(t)
    return grade_frame(frame)

# ----------------------------------------------------
# 2. Time Mapping (Raw to Output Timeline)
# ----------------------------------------------------
class TimeMapper:
    def __init__(self, speech_segments):
        self.segments = speech_segments
        self.out_segments = []
        
        curr_out = 0.0
        for seg in self.segments:
            s_raw, e_raw = seg[0], seg[1]
            dur = e_raw - s_raw
            self.out_segments.append({
                "raw_start": s_raw,
                "raw_end": e_raw,
                "out_start": curr_out,
                "out_end": curr_out + dur,
                "duration": dur
            })
            curr_out += dur
            
    def raw_to_out(self, t_raw):
        for o_seg in self.out_segments:
            if o_seg["raw_start"] <= t_raw <= o_seg["raw_end"]:
                return o_seg["out_start"] + (t_raw - o_seg["raw_start"])
        return None
        
    def raw_range_to_out(self, start_raw, end_raw):
        """Maps a raw time range to one or more output time ranges."""
        mapped = []
        for o_seg in self.out_segments:
            # Overlap intersection
            s = max(start_raw, o_seg["raw_start"])
            e = min(end_raw, o_seg["raw_end"])
            if e > s + 0.05:
                o_s = o_seg["out_start"] + (s - o_seg["raw_start"])
                o_e = o_seg["out_start"] + (e - o_seg["raw_start"])
                mapped.append((o_s, o_e))
        return mapped

# ----------------------------------------------------
# 3. Pillow Clean, Minimal Subtitle Overlay
# ----------------------------------------------------
def get_subtitle_generator(text, duration):
    font = get_font(48)
    
    # Word wrap logic: wrap text to fit max width of 1300px
    max_w = 1300
    words = text.split()
    lines = []
    curr_line = []
    
    # Create temporary drawing canvas for text measurement
    temp_img = Image.new("RGBA", (100, 100))
    temp_draw = ImageDraw.Draw(temp_img)
    
    for word in words:
        test_line = " ".join(curr_line + [word])
        bbox = temp_draw.textbbox((0, 0), test_line, font=font)
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
        
        # Centered position in the lower third
        line_height = 65
        start_y = 850 - ((num_lines - 1) * line_height) // 2
        
        for idx, line_text in enumerate(lines):
            y = start_y + idx * line_height
            x = RESOLUTION[0] // 2
            
            # Subtle dark drop shadow for legibility
            shadow_offset = 2
            draw.text((x + shadow_offset, y + shadow_offset), line_text, font=font, fill=(0, 0, 0, 200), anchor="mm")
            # Clean white text
            draw.text((x, y), line_text, font=font, fill=(255, 255, 255, 255), anchor="mm")
            
        np_arr = np.array(img)
        rgb = np_arr[:, :, :3]
        alpha = np_arr[:, :, 3].astype(float) / 255.0
        return rgb, alpha
        
    return frame_gen

def make_subtitle_clip(text, duration):
    gen = get_subtitle_generator(text, duration)
    # Precompute the static subtitle frames to avoid drawing on every single frame iteration
    rgb, alpha = gen(0.0)
    color_clip = VideoClip(lambda t: rgb, duration=duration)
    mask_clip = VideoClip(lambda t: alpha, duration=duration, is_mask=True)
    return color_clip.with_mask(mask_clip)

# ----------------------------------------------------
# Main Editing Pipeline
# ----------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Imaginary Hub Clean & Minimal Updates Video Editor")
    parser.add_argument("--preview", action="store_true", help="Render a 60-second preview clip instead of full video")
    args = parser.parse_args()
    
    print("Initializing editor (minimal updates mode)...")
    raw_video_path = "Imaginary_Hub.MOV"
    
    # Load data
    with open("intervals.json") as f:
        intervals_data = json.load(f)
    with open("subtitles.json") as f:
        subtitles_data = json.load(f)
        
    speech_segments = intervals_data["speech"]
    time_mapper = TimeMapper(speech_segments)
    
    raw_clip = VideoFileClip(raw_video_path)
    
    # ----------------------------------------------------
    # Step A: Assemble Jump Cut Clips (1.0x Scale, Natural flow)
    # ----------------------------------------------------
    print("Stitching talking-head segments with natural cuts...")
    cut_clips = []
    
    for idx, seg in enumerate(speech_segments):
        start_raw, end_raw = seg[0], seg[1]
        
        # Check for preview limit
        if args.preview:
            out_start = time_mapper.raw_to_out(start_raw)
            if out_start is not None and out_start >= 60.0:
                print(f"Preview limit reached. Stopping clip assembly at segment {idx}.")
                break
                
        seg_clip = raw_clip.subclipped(start_raw, end_raw)
        
        # Apply subtle color grading filter
        seg_clip = seg_clip.transform(lambda get_frame, t: fl_grade_filter(get_frame, t))
        
        # Smooth audio transition (micro-fade of 50ms) to avoid pops at jump cuts
        seg_clip = seg_clip.with_effects([afx.AudioFadeIn(0.05), afx.AudioFadeOut(0.05)])
        
        # Keep scale strictly at 1.0x (no zooms, no jumps)
        cut_clips.append(seg_clip)
        
    concat_talking = concatenate_videoclips(cut_clips, method="chain")
    print(f"Stitched talking-head duration: {concat_talking.duration:.2f}s")
    
    # Determine target duration
    target_duration = concat_talking.duration
    if args.preview:
        target_duration = min(60.0, target_duration)
        concat_talking = concat_talking.subclipped(0, target_duration)
        
    # ----------------------------------------------------
    # Step B: Prepare Subtitles with Memory-Efficient Cache
    # ----------------------------------------------------
    print("Preparing subtitle entries...")
    subtitle_entries = []
    for sub in subtitles_data:
        s_raw, e_raw, text = sub["start"], sub["end"], sub["text"]
        
        mapped_ranges = time_mapper.raw_range_to_out(s_raw, e_raw)
        for s_out, e_out in mapped_ranges:
            if s_out >= target_duration:
                continue
            clip_end = min(target_duration, e_out)
            clip_dur = clip_end - s_out
            if clip_dur > 0.2:
                subtitle_entries.append({
                    "start": s_out,
                    "end": clip_end,
                    "text": text,
                    "duration": clip_dur
                })
                
    # Cache variables for the active subtitle frame
    cache = {
        "active_entry": None,
        "rgb": None,
        "alpha": None
    }
    
    BLANK_RGB = np.zeros((RESOLUTION[1], RESOLUTION[0], 3), dtype=np.uint8)
    BLANK_ALPHA = np.zeros((RESOLUTION[1], RESOLUTION[0]), dtype=float)
    
    last_found_idx = [0]
    
    def get_frame_cached(t):
        # 1. Quick check: is the current time still in the active cached entry?
        active = cache["active_entry"]
        if active and active["start"] <= t < active["end"]:
            return cache["rgb"], cache["alpha"]
            
        # 2. Lookup entry at time t starting from the last found index (O(1) sequential lookup)
        n = len(subtitle_entries)
        found_entry = None
        start_idx = last_found_idx[0]
        for i in range(n):
            idx = (start_idx + i) % n
            item = subtitle_entries[idx]
            if item["start"] <= t < item["end"]:
                last_found_idx[0] = idx
                found_entry = item
                break
                
        if not found_entry:
            # Silent interval - no active subtitle
            cache["active_entry"] = None
            cache["rgb"] = BLANK_RGB
            cache["alpha"] = BLANK_ALPHA
            return BLANK_RGB, BLANK_ALPHA
            
        # 3. Draw text and cache the results
        gen = get_subtitle_generator(found_entry["text"], found_entry["duration"])
        rgb, alpha = gen(0.0)
        
        # Update cache
        cache["active_entry"] = found_entry
        cache["rgb"] = rgb
        cache["alpha"] = alpha
        
        return rgb, alpha

    def sub_color_frame(t):
        return get_frame_cached(t)[0]

    def sub_mask_frame(t):
        return get_frame_cached(t)[1]

    print("Creating unified subtitle track...")
    sub_color_clip = VideoClip(sub_color_frame, duration=target_duration)
    sub_mask_clip = VideoClip(sub_mask_frame, duration=target_duration, is_mask=True)
    subtitle_track = sub_color_clip.with_mask(sub_mask_clip)
    
    # ----------------------------------------------------
    # Step C: Assemble Timeline Composites (Just 2 layers)
    # ----------------------------------------------------
    print("Assembling video composites (2 layers)...")
    final_video = CompositeVideoClip([concat_talking, subtitle_track], size=RESOLUTION)
    
    # ----------------------------------------------------
    # Step D: Render Export
    # ----------------------------------------------------
    output_filename = "Imaginary_Hub_Preview.mp4" if args.preview else "Imaginary_Hub_Edited.mp4"
    print(f"Starting export to {output_filename} ({target_duration:.2f}s)...")
    
    # Render with Apple Silicon hardware acceleration for speed
    final_video.write_videofile(
        output_filename,
        fps=FPS,
        codec="h264_videotoolbox",
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True,
        write_logfile=False,
        threads=8,
        bitrate="8000k"
    )
    print(f"Export completed successfully: {output_filename}")

if __name__ == "__main__":
    main()
