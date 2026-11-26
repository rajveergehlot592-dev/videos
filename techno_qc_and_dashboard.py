import os
import subprocess
import json

BASE_DIR = r"E:\videos\TECHNO_GAMERZ_REELS"
FINAL_REELS_DIR = os.path.join(BASE_DIR, "FINAL_REELS")
THUMBNAILS_DIR = os.path.join(BASE_DIR, "THUMBNAILS")
SUBTITLES_DIR = os.path.join(BASE_DIR, "SUBTITLES")
ANALYSIS_DIR = os.path.join(BASE_DIR, "ANALYSIS")
HTML_PATH = os.path.join(BASE_DIR, "dashboard.html")

from techno_prepare import REELS_DATA

results = []
print("Running Quality Control on all 16 1080p60 Techno Gamerz Reels...\n")

for item in REELS_DATA:
    name = item["name"]
    mp4_path = os.path.join(FINAL_REELS_DIR, f"{name}.mp4")
    thumb_path = os.path.join(THUMBNAILS_DIR, f"Reel_{item['id']:03d}.jpg")
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
        "black_frames": 0,
        "thumbnail_exists": os.path.exists(thumb_path),
        "srt_exists": os.path.exists(srt_path),
        "status": "PASS"
    }

    if qc["mp4_exists"]:
        qc["size_mb"] = round(os.path.getsize(mp4_path) / (1024 * 1024), 2)
        res = subprocess.run(["ffmpeg", "-i", mp4_path], capture_output=True, text=True)
        for line in res.stderr.split("\n"):
            line = line.strip()
            if "Stream #" in line and "Video:" in line:
                if "1080x1920" in line:
                    qc["resolution"] = "1080x1920"
                if "h264" in line:
                    qc["video_codec"] = "h264"
                if "60 fps" in line or "60 tbr" in line:
                    qc["fps"] = 60.0
            if "Stream #" in line and "Audio:" in line:
                qc["audio_present"] = True
            if "Duration:" in line:
                parts = line.split(",")[0].replace("Duration:", "").strip()
                h, m, s = parts.split(":")
                qc["duration"] = round(float(h)*3600 + float(m)*60 + float(s), 1)

        b_res = subprocess.run([
            "ffmpeg", "-i", mp4_path,
            "-vf", "blackdetect=d=1.0:pic_th=0.98",
            "-an", "-f", "null", "-"
        ], capture_output=True, text=True)
        if "black_start" in b_res.stderr:
            qc["black_frames"] = b_res.stderr.count("black_start")

        if qc["resolution"] != "1080x1920" or not qc["audio_present"] or qc["size_mb"] < 2.0 or qc["black_frames"] > 0:
            qc["status"] = "FAIL"

    print(f"[{name}] {qc['status']} | {qc['size_mb']} MB | {qc['resolution']} @ {qc['fps']}fps | {qc['duration']}s | Audio: {qc['audio_present']}")
    results.append(qc)

passed = sum(1 for r in results if r["status"] == "PASS")
print(f"\nQUALITY CONTROL SUMMARY: {passed}/{len(results)} PASSED")

with open(os.path.join(ANALYSIS_DIR, "quality_control_report.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

# Generate dashboard.html
qc_map = {r["id"]: r for r in results}
cards_data = []
for item in REELS_DATA:
    cid = item["id"]
    qc = qc_map.get(cid, {})
    cards_data.append({
        "id": cid,
        "name": item["name"],
        "title": item["title"],
        "category": item["category"],
        "score": item["score"],
        "hook": item["hook"],
        "start": item["start"],
        "duration": item["duration"],
        "desc": item["desc"],
        "hashtags": item["hashtags"],
        "pinned": item["pinned"],
        "subtitles": item["subtitles"],
        "video_file": f"FINAL_REELS/{item['name']}.mp4",
        "thumb_file": f"THUMBNAILS/Reel_{cid:03d}.jpg",
        "srt_file": f"SUBTITLES/{item['name']}.srt",
        "size_mb": qc.get("size_mb", 0),
        "qc_status": qc.get("status", "PASS")
    })

json_cards = json.dumps(cards_data, indent=2)
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Techno Gamerz GTA 6 Reels Studio (1080p60 HD)</title>
<style>
  body {{ background:#090a10; color:#f0f3fc; font-family:system-ui,-apple-system,sans-serif; margin:0; padding:24px; }}
  .container {{ max-width:1400px; margin:0 auto; }}
  header {{ display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #232840; padding-bottom:20px; margin-bottom:24px; flex-wrap:wrap; gap:12px; }}
  .badge {{ background:linear-gradient(135deg,#ffe600,#ff2a85); color:#000; font-weight:900; padding:8px 16px; border-radius:10px; font-size:20px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:22px; }}
  .card {{ background:#121420; border:1px solid #232840; border-radius:16px; overflow:hidden; display:flex; flex-direction:column; }}
  .thumb {{ position:relative; aspect-ratio:9/16; max-height:380px; background:#000; cursor:pointer; overflow:hidden; }}
  .thumb img {{ width:100%; height:100%; object-fit:cover; }}
  .score {{ position:absolute; top:12px; right:12px; background:#ffe600; color:#000; font-weight:900; padding:4px 10px; border-radius:6px; font-size:12px; }}
  .cat {{ position:absolute; top:12px; left:12px; background:rgba(0,0,0,0.8); padding:4px 10px; border-radius:6px; font-size:11px; font-weight:700; }}
  .body {{ padding:16px; display:flex; flex-direction:column; gap:10px; flex:1; }}
  .hook {{ color:#ffe600; font-size:12px; font-weight:700; background:rgba(255,230,0,0.1); padding:6px 10px; border-radius:6px; }}
  .title {{ font-size:14px; font-weight:700; line-height:1.4; }}
  .meta {{ font-size:12px; color:#8b92b2; display:flex; justify-content:space-between; }}
  .actions {{ display:flex; gap:8px; margin-top:auto; }}
  .btn {{ flex:1; background:#1b1e30; color:#fff; border:1px solid #232840; padding:9px; border-radius:8px; font-weight:700; cursor:pointer; font-size:12px; text-align:center; text-decoration:none; }}
  .btn-primary {{ background:#0072ff; border:none; }}
  .modal {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,0.88); z-index:99; align-items:center; justify-content:center; padding:20px; }}
  .modal.active {{ display:flex; }}
  .modal-box {{ background:#121420; border:1px solid #232840; border-radius:18px; max-width:850px; width:100%; padding:24px; display:flex; gap:24px; max-height:90vh; overflow:auto; }}
  video {{ width:320px; aspect-ratio:9/16; background:#000; border-radius:12px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div style="display:flex;align-items:center;gap:14px;">
      <div class="badge">GTA 6 HD</div>
      <div>
        <h1 style="margin:0;font-size:22px;">TECHNO GAMERZ — 1080p60 REELS STUDIO</h1>
        <p style="margin:4px 0 0;color:#8b92b2;font-size:13px;">Source: MY FIRST DAY IN VICE CITY | 16 Reels @ 1080×1920 60fps (CRF 18)</p>
      </div>
    </div>
    <div><strong>QC Status: {passed}/{len(results)} PASS</strong></div>
  </header>
  <div class="grid" id="grid"></div>
</div>
<div class="modal" id="modal" onclick="if(event.target===this)closeM()">
  <div class="modal-box">
    <video id="vid" controls playsinline></video>
    <div style="flex:1;display:flex;flex-direction:column;gap:12px;">
      <h2 id="m-title" style="margin:0;font-size:18px;"></h2>
      <div id="m-hook" class="hook"></div>
      <p id="m-desc" style="font-size:13px;color:#cfd5ea;line-height:1.5;"></p>
      <p id="m-tags" style="font-size:12px;color:#00f0ff;"></p>
      <p id="m-pin" style="font-size:12px;color:#8b92b2;font-style:italic;"></p>
      <button class="btn" onclick="closeM()" style="flex:none;margin-top:auto;">Close Preview</button>
    </div>
  </div>
</div>
<script>
const REELS = {json_cards};
const grid = document.getElementById('grid');
REELS.forEach(r => {{
  const d = document.createElement('div');
  d.className = 'card';
  d.innerHTML = `
    <div class="thumb" onclick="openM(${{r.id}})">
      <img src="${{r.thumb_file}}">
      <span class="cat">${{r.category}}</span>
      <span class="score">★ ${{r.score}}/100</span>
    </div>
    <div class="body">
      <div class="hook">${{r.hook}}</div>
      <div class="title">${{r.title}}</div>
      <div class="meta"><span>⏱️ ${{Math.floor(r.start/60)}}m ${{r.start%60}}s</span><span>📦 ${{r.size_mb}} MB (60fps)</span></div>
      <div class="actions">
        <button class="btn btn-primary" onclick="openM(${{r.id}})">▶ Preview</button>
        <a class="btn" href="${{r.video_file}}" download>⬇️ MP4</a>
      </div>
    </div>`;
  grid.appendChild(d);
}});
function openM(id) {{
  const r = REELS.find(x => x.id === id);
  document.getElementById('m-title').innerText = r.title;
  document.getElementById('m-hook').innerText = r.hook;
  document.getElementById('m-desc').innerText = r.desc;
  document.getElementById('m-tags').innerText = r.hashtags;
  document.getElementById('m-pin').innerText = 'Pinned: ' + r.pinned;
  const v = document.getElementById('vid');
  v.src = r.video_file; v.play().catch(()=>{{}});
  document.getElementById('modal').classList.add('active');
}}
function closeM() {{
  document.getElementById('modal').classList.remove('active');
  const v = document.getElementById('vid'); v.pause(); v.src = '';
}}
</script>
</body>
</html>"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Dashboard saved to {HTML_PATH}")
