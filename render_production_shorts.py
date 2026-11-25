import os
import sys
import subprocess
import time
import concurrent.futures

BASE_DIR = r"E:\videos\GTA6_YOUTUBE_SHORTS"
FINAL_SHORTS_DIR = os.path.join(BASE_DIR, "FINAL_SHORTS")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "THUMBNAILS")
SUBTITLES_DIR = os.path.join(BASE_DIR, "SUBTITLES")

with open(r"E:\videos\stream_url_360p.txt", "r") as f:
    video_url = f.read().strip()
with open(r"E:\videos\stream_url_audio.txt", "r") as f:
    audio_url = f.read().strip()

from prepare_metadata import SHORTS_DATA

def render_short(item):
    name = item["name"]
    start = item["start"]
    dur = item["duration"]
    mp4_out = os.path.join(FINAL_SHORTS_DIR, f"{name}.mp4")
    thumb_out = os.path.join(THUMBNAILS_DIR, f"Short_{item['id']:03d}.jpg")
    # Use relative path with forward slashes for ffmpeg filter syntax
    rel_ass = os.path.relpath(os.path.join(SUBTITLES_DIR, f"{name}.ass")).replace("\\", "/")
    
    # Check if already rendered
    if os.path.exists(mp4_out) and os.path.getsize(mp4_out) > 1000000 and os.path.exists(thumb_out):
        print(f"[{name}] Already rendered, skipping.")
        return name, True, "Already exists"
        
    print(f"[{name}] Starting render (start: {start}s, duration: {dur}s)...")
    t0 = time.time()
    
    # Filter complex
    filter_complex = (
        "[0:v]split=3[bg_in][game_in][cam_in];"
        "[bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=22:5[bg];"
        "[game_in]crop=in_w*0.85:in_h:in_w*0.075:0,scale=1080:762[game];"
        "[cam_in]crop=168:110:6:160,scale=680:445,drawbox=x=0:y=0:w=680:h=445:color=0x00ffff@1.0:t=6[cam];"
        "[bg][cam]overlay=200:190[bg_cam];"
        "[bg_cam][game]overlay=0:670[bg_game];"
        "[bg_game]drawbox=x=0:y=0:w=1080:h=170:color=black@0.85:t=fill,"
        f"subtitles='{rel_ass}'[outv]"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-t", str(dur),
        "-i", video_url,
        "-ss", str(start), "-t", str(dur),
        "-i", audio_url,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,volume=1.15",
        mp4_out
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[{name}] FFMPEG ERROR: {res.stderr[-300:]}")
        return name, False, res.stderr[-200:]
        
    # Extract thumbnail at 3 seconds in
    thumb_cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:03",
        "-i", mp4_out,
        "-vframes", "1",
        "-update", "1",
        thumb_out
    ]
    subprocess.run(thumb_cmd, capture_output=True)
    
    elapsed = time.time() - t0
    size_mb = os.path.getsize(mp4_out) / (1024 * 1024)
    print(f"[{name}] Rendered successfully in {elapsed:.1f}s ({size_mb:.2f} MB)")
    return name, True, f"{size_mb:.2f} MB"

def main():
    print(f"Starting batch production of {len(SHORTS_DATA)} GTA 6 Shorts...")
    t_start = time.time()
    
    # Run with 3 parallel workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(render_short, item): item for item in SHORTS_DATA}
        for future in concurrent.futures.as_completed(futures):
            item = futures[future]
            try:
                name, success, info = future.result()
            except Exception as e:
                print(f"[{item['name']}] Exception: {e}")
                
    total_elapsed = time.time() - t_start
    print(f"\n==========================================")
    print(f"ALL SHORTS PRODUCTION COMPLETE in {total_elapsed:.1f}s!")
    print(f"==========================================")

if __name__ == "__main__":
    main()
