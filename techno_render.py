import os
import subprocess
import time
import concurrent.futures

BASE_DIR = r"E:\videos\TECHNO_GAMERZ_REELS"
FINAL_REELS_DIR = os.path.join(BASE_DIR, "FINAL_REELS")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "THUMBNAILS")
SUBTITLES_DIR = os.path.join(BASE_DIR, "SUBTITLES")

with open(r"E:\videos\techno_work\stream_url_1080p.txt", "r") as f:
    video_url = f.read().strip()
with open(r"E:\videos\techno_work\stream_url_audio.txt", "r") as f:
    audio_url = f.read().strip()

from techno_prepare import REELS_DATA

def render_reel(item):
    name = item["name"]
    start = item["start"]
    dur = item["duration"]
    mp4_out = os.path.join(FINAL_REELS_DIR, f"{name}.mp4")
    thumb_out = os.path.join(THUMBNAILS_DIR, f"Reel_{item['id']:03d}.jpg")
    rel_ass = os.path.relpath(os.path.join(SUBTITLES_DIR, f"{name}.ass")).replace("\\", "/")

    if os.path.exists(mp4_out) and os.path.getsize(mp4_out) > 2000000 and os.path.exists(thumb_out):
        print(f"[{name}] Already rendered, skipping.", flush=True)
        return name, True, "Already exists"

    print(f"[{name}] Rendering 1080p60 HD Reel (start={start}s, dur={dur}s)...", flush=True)
    t0 = time.time()

    # High-quality 1080p60 lanczos pipeline:
    # 1. Background: blurred full canvas 1080x1920
    # 2. Webcam: tight crop from top-right of 1920x1070 (x=1539, y=121, w=318, h=226) -> scaled to 640x455 with gold border
    # 3. Gameplay: crisp center 1620x1070 -> scaled to 1080x714
    filter_complex = (
        "[0:v]split=3[bg_in][game_in][cam_in];"
        "[bg_in]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,boxblur=25:5[bg];"
        "[game_in]crop=1620:1070:150:0,scale=1080:714:flags=lanczos[game];"
        "[cam_in]crop=318:226:1539:121,scale=640:455:flags=lanczos,drawbox=x=0:y=0:w=640:h=455:color=0xffe600@1.0:t=6[cam];"
        "[bg][cam]overlay=220:180[bg_cam];"
        "[bg_cam][game]overlay=0:675[bg_game];"
        "[bg_game]drawbox=x=0:y=0:w=1080:h=155:color=black@0.85:t=fill,"
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
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "60", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,volume=1.15",
        mp4_out
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[{name}] FFMPEG ERROR: {res.stderr[-300:]}", flush=True)
        return name, False, res.stderr[-200:]

    thumb_cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:03",
        "-i", mp4_out,
        "-vframes", "1", "-q:v", "2", "-update", "1",
        thumb_out
    ]
    subprocess.run(thumb_cmd, capture_output=True)

    elapsed = time.time() - t0
    size_mb = os.path.getsize(mp4_out) / (1024 * 1024)
    print(f"[{name}] Done in {elapsed:.1f}s ({size_mb:.2f} MB)", flush=True)
    return name, True, f"{size_mb:.2f} MB"

def main():
    t_start = time.time()
    print(f"Starting 1080p60 HD batch render of {len(REELS_DATA)} Reels...", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(render_reel, item): item for item in REELS_DATA}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Exception: {e}", flush=True)
    print(f"\nALL 16 HD REELS RENDERED in {time.time() - t_start:.1f}s!", flush=True)

if __name__ == "__main__":
    main()
