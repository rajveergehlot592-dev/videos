import os
import subprocess
import json

BASE_DIR = r"E:\videos\GTA6_YOUTUBE_SHORTS"
FINAL_SHORTS_DIR = os.path.join(BASE_DIR, "FINAL_SHORTS")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "THUMBNAILS")
SUBTITLES_DIR = os.path.join(BASE_DIR, "SUBTITLES")

from prepare_metadata import SHORTS_DATA

ANALYSIS_DIR = os.path.join(BASE_DIR, "ANALYSIS")
results = []

print("Running Automated Quality Control Verification on all 20 Shorts...\n")

for item in SHORTS_DATA:
    name = item["name"]
    mp4_path = os.path.join(FINAL_SHORTS_DIR, f"{name}.mp4")
    thumb_path = os.path.join(THUMBNAILS_DIR, f"Short_{item['id']:03d}.jpg")
    srt_path = os.path.join(SUBTITLES_DIR, f"{name}.srt")
    
    qc = {
        "id": item["id"],
        "name": name,
        "title": item["title"],
        "category": item["category"],
        "score": item["score"],
        "mp4_exists": os.path.exists(mp4_path),
        "size_mb": 0.0,
        "resolution": "Unknown",
        "video_codec": "Unknown",
        "fps": 0.0,
        "duration": 0.0,
        "audio_present": False,
        "audio_codec": "Unknown",
        "black_frames": 0,
        "thumbnail_exists": os.path.exists(thumb_path),
        "srt_exists": os.path.exists(srt_path),
        "status": "PASS"
    }
    
    if qc["mp4_exists"]:
        qc["size_mb"] = round(os.path.getsize(mp4_path) / (1024 * 1024), 2)
        
        # Probe video using ffmpeg
        cmd = ["ffmpeg", "-i", mp4_path]
        res = subprocess.run(cmd, capture_output=True, text=True)
        out = res.stderr
        
        for line in out.split("\n"):
            line = line.strip()
            if "Stream #" in line and "Video:" in line:
                if "1080x1920" in line:
                    qc["resolution"] = "1080x1920"
                if "h264" in line:
                    qc["video_codec"] = "h264"
                if "30 fps" in line or "30 tbr" in line:
                    qc["fps"] = 30.0
            if "Stream #" in line and "Audio:" in line:
                qc["audio_present"] = True
                if "aac" in line:
                    qc["audio_codec"] = "aac"
            if "Duration:" in line:
                parts = line.split(",")[0].replace("Duration:", "").strip()
                # e.g. 00:00:25.00
                h, m, s = parts.split(":")
                qc["duration"] = round(float(h)*3600 + float(m)*60 + float(s), 1)
                
        # Run blackdetect
        b_cmd = [
            "ffmpeg", "-i", mp4_path,
            "-vf", "blackdetect=d=1.0:pic_th=0.98",
            "-an", "-f", "null", "-"
        ]
        b_res = subprocess.run(b_cmd, capture_output=True, text=True)
        if "black_start" in b_res.stderr:
            qc["black_frames"] = b_res.stderr.count("black_start")
            
        # Verify criteria
        if qc["resolution"] != "1080x1920" or not qc["audio_present"] or qc["size_mb"] < 1.0 or qc["black_frames"] > 0:
            qc["status"] = "FAIL"
            
    print(f"[{name}] Status: {qc['status']} | Size: {qc['size_mb']}MB | Res: {qc['resolution']} | Dur: {qc['duration']}s | Audio: {qc['audio_present']} | Thumb: {qc['thumbnail_exists']} | SRT: {qc['srt_exists']}")
    results.append(qc)

passed_count = sum(1 for r in results if r["status"] == "PASS")
print(f"\n==========================================")
print(f"QUALITY CONTROL SUMMARY: {passed_count}/{len(results)} PASSED")
print(f"==========================================")

with open(os.path.join(ANALYSIS_DIR, "quality_control_report.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
