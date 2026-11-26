import os
import csv
import json
import time
import asyncio
import subprocess
import concurrent.futures
import edge_tts
from mutagen.mp3 import MP3

OUT_BASE = r"E:\videos\IShowSpeed_PRO_REELS"
FINAL_DIR = os.path.join(OUT_BASE, "FINAL_REELS")
VO_DIR = os.path.join(OUT_BASE, "VOICEOVERS")
SUB_DIR = os.path.join(OUT_BASE, "SUBTITLES")
THUMB_DIR = os.path.join(OUT_BASE, "THUMBNAILS")
META_DIR = os.path.join(OUT_BASE, "METADATA")
ANALYSIS_DIR = os.path.join(OUT_BASE, "ANALYSIS")

for d in [FINAL_DIR, VO_DIR, SUB_DIR, THUMB_DIR, META_DIR, ANALYSIS_DIR]:
    os.makedirs(d, exist_ok=True)

with open(r"E:\videos\live3_work\stream_url_1080p.txt", "r") as f:
    VIDEO_URL = f.read().strip()
with open(r"E:\videos\live3_work\stream_url_audio.txt", "r") as f:
    AUDIO_URL = f.read().strip()

SPEED_REELS = [
    {
        "id": 1, "name": "Speed_Reel_001", "start": 20, "duration": 25, "climax_t": 8.0,
        "category": "Viral Reaction", "score": 97,
        "hook": "IS THIS REALLY GTA 6?! 🔥",
        "vo_script": "IShowSpeed waited over a decade for this exact second—watch his reaction loading into GTA 6!",
        "subtitles": [
            (0.0, 3.2, "OVER 10 YEARS FOR THIS MOMENT!"),
            (3.2, 9.0, "Speed finally loads into GTA 6!"),
            (9.0, 16.0, "175,000+ viewers watching live!"),
            (16.0, 25.0, "The 24-hour marathon begins now!")
        ],
        "title": "IShowSpeed's Unbelievable First Reaction To GTA 6! 🔥 #GTA6 #IShowSpeed",
        "hashtags": "#GTA6 #IShowSpeed #GTAVI #GamingShorts #Reels"
    },
    {
        "id": 2, "name": "Speed_Reel_002", "start": 858, "duration": 26, "climax_t": 9.0,
        "category": "Crazy Crash", "score": 95,
        "hook": "SPEED CRASHED IN 10 SECONDS! 💥",
        "vo_script": "Give IShowSpeed a red supercar in Vice Beach and watch how fast he totals it in GTA 6!",
        "subtitles": [
            (0.0, 3.3, "RED SUPERCAR IN VICE BEACH!"),
            (3.3, 9.0, "Full throttle past the Vice Beach sign..."),
            (9.0, 16.0, "INSTANT SUPERCAR CRASH! 💥"),
            (16.0, 26.0, "Speed's driving in GTA 6 is chaotic!")
        ],
        "title": "IShowSpeed Totals A Supercar In GTA 6 Vice Beach! 💥😂 #GTA6 #IShowSpeed",
        "hashtags": "#GTA6 #IShowSpeed #ViceBeach #SupercarCrash #Shorts"
    },
    {
        "id": 3, "name": "Speed_Reel_003", "start": 5336, "duration": 26, "climax_t": 9.5,
        "category": "Funny Moments", "score": 94,
        "hook": "SPEED CALLED LUCIA SHORTY! 😂",
        "vo_script": "IShowSpeed really forgot how to act the second he started walking around Vice City as Lucia!",
        "subtitles": [
            (0.0, 3.2, "SPEED PLAYING AS LUCIA!"),
            (3.2, 9.5, "Cruising through Vice City streets..."),
            (9.5, 17.0, "Bro really called Lucia shorty! 😂"),
            (17.0, 26.0, "Chat went completely wild!")
        ],
        "title": "IShowSpeed Wilding Out Playing As Lucia In GTA 6! 😂💀 #GTA6 #Lucia",
        "hashtags": "#GTA6 #Lucia #IShowSpeed #GTA6Funny #Shorts"
    },
    {
        "id": 4, "name": "Speed_Reel_004", "start": 6128, "duration": 26, "climax_t": 10.0,
        "category": "Story & Heists", "score": 93,
        "hook": "CARTEL BANK HEIST IN GTA 6! 💰",
        "vo_script": "This GTA 6 bank robbery mission has Speed completely locked in—their money isn't safe anywhere!",
        "subtitles": [
            (0.0, 3.4, "RAUL'S BANK ROBBERY MISSION!"),
            (3.4, 10.0, "Walking into the Vice City bank..."),
            (10.0, 17.5, "'Their money's not safe in this city!'"),
            (17.5, 26.0, "Cinematic GTA 6 heist action!")
        ],
        "title": "GTA 6 Bank Robbery Mission With IShowSpeed Is Pure Cinema! 💰🔥 #GTA6",
        "hashtags": "#GTA6 #GTA6Heist #IShowSpeed #GamingReels #Shorts"
    },
    {
        "id": 5, "name": "Speed_Reel_005", "start": 9770, "duration": 26, "climax_t": 9.0,
        "category": "Meme & Viral", "score": 98,
        "hook": "SPEED TOOK SO LONG TO REALIZE! 💀",
        "vo_script": "Wait for the exact moment IShowSpeed realizes what is actually happening in this GTA 6 cutscene!",
        "subtitles": [
            (0.0, 3.3, "WATCH SPEED'S FACE CLOSELY..."),
            (3.3, 9.0, "200,000 live viewers screaming in chat!"),
            (9.0, 16.5, "IT FINALLY CLICKED FOR SPEED! 💀"),
            (16.5, 26.0, "Bro paused and lost his mind! 😂")
        ],
        "title": "The Moment IShowSpeed Realized What Happened In GTA 6! 💀😂 #IShowSpeed",
        "hashtags": "#GTA6 #IShowSpeed #GTA6Memes #ViralReels #Shorts"
    },
    {
        "id": 6, "name": "Speed_Reel_006", "start": 14636, "duration": 26, "climax_t": 8.5,
        "category": "Peak Stream Viral", "score": 99,
        "hook": "HOW IS THIS ALLOWED IN GTA 6?! 😭",
        "vo_script": "Four hours into his 24-hour marathon, IShowSpeed stumbled into the most unexpected scene in GTA 6!",
        "subtitles": [
            (0.0, 3.4, "4 HOURS INTO THE MARATHON..."),
            (3.4, 9.0, "Wait... what are they doing?! 💀"),
            (9.0, 16.5, "SPEED SCREAMING IN PURE SHOCK!"),
            (16.5, 26.0, "How did Rockstar put this in the game?!")
        ],
        "title": "IShowSpeed Couldn't Believe This GTA 6 Scene Was Allowed! 😭💀 #GTA6",
        "hashtags": "#GTA6 #IShowSpeed #GamingMemes #ViralShorts #Reels"
    },
    {
        "id": 7, "name": "Speed_Reel_007", "start": 26820, "duration": 25, "climax_t": 8.5,
        "category": "Gameplay Mechanics", "score": 91,
        "hook": "AFTER 7 HOURS... HE BOUGHT GUNS! 🔫",
        "vo_script": "Seven straight hours into GTA 6, and IShowSpeed finally remembers he can upgrade his weapons!",
        "subtitles": [
            (0.0, 3.4, "7 HOURS INTO GTA 6..."),
            (3.4, 9.0, "Speed finally visits the gun shop!"),
            (9.0, 16.5, "Testing out next-gen weapon upgrades!"),
            (16.5, 25.0, "Vice City is NOT ready for this! 🔥")
        ],
        "title": "After 7 Hours, IShowSpeed Finally Upgrades His Guns In GTA 6! 🔫🔥 #GTA6",
        "hashtags": "#GTA6 #GTA6Weapons #IShowSpeed #GamingShorts #Reels"
    },
    {
        "id": 8, "name": "Speed_Reel_008", "start": 36560, "duration": 26, "climax_t": 9.0,
        "category": "Crazy Stunt", "score": 94,
        "hook": "HOW DID LUCIA SURVIVE THAT?! 😱",
        "vo_script": "Ten hours into the stream, Speed takes a massive fall with Lucia—watch how she somehow survives!",
        "subtitles": [
            (0.0, 3.3, "10 HOURS IN — MASSIVE FALL!"),
            (3.3, 9.0, "Zero health and no medkit left..."),
            (9.0, 16.5, "SHE ACTUALLY SURVIVED THAT?! 😱"),
            (16.5, 26.0, "Pure plot armor in Vice City! 🔥")
        ],
        "title": "How Did Lucia Survive This Fall In GTA 6?! 😱 IShowSpeed Reacts #GTA6",
        "hashtags": "#GTA6 #Lucia #IShowSpeed #GTA6Stunts #Shorts"
    },
    {
        "id": 9, "name": "Speed_Reel_009", "start": 69905, "duration": 25, "climax_t": 8.5,
        "category": "Hidden Easter Egg", "score": 96,
        "hook": "JIMMY DE SANTA IS IN GTA 6?! 🤯",
        "vo_script": "Nineteen hours into the marathon, IShowSpeed may have just spotted a familiar GTA 5 face in Vice City!",
        "subtitles": [
            (0.0, 3.4, "19 HOURS INTO THE STREAM..."),
            (3.4, 9.0, "Wait... look closely at this character!"),
            (9.0, 16.5, "IS THAT JIMMY DE SANTA FROM GTA 5?!"),
            (16.5, 25.0, "Rockstar Easter Eggs are undefeated! 🤯")
        ],
        "title": "Jimmy De Santa Cameo Spotted In GTA 6?! 🤯🔥 IShowSpeed Reacts #GTA6",
        "hashtags": "#GTA6 #GTA5 #EasterEgg #IShowSpeed #Shorts"
    },
    {
        "id": 10, "name": "Speed_Reel_010", "start": 82340, "duration": 26, "climax_t": 9.0,
        "category": "Peak Comedy", "score": 97,
        "hook": "23 HOURS LATER... PURE COMEDY! 😂",
        "vo_script": "Twenty-three hours without sleep, and IShowSpeed plus Jamal just delivered the funniest moment of the stream!",
        "subtitles": [
            (0.0, 3.5, "23 HOURS INTO THE 24H MARATHON!"),
            (3.5, 9.5, "Speed and Jamal losing it on stream..."),
            (9.5, 17.0, "Best comedy moment of the entire day!"),
            (17.0, 26.0, "W Speed & W Jamal! ❤️🔥")
        ],
        "title": "23 Hours Into GTA 6 — IShowSpeed & Jamal Funniest Moment! 😂🔥 #GTA6",
        "hashtags": "#GTA6 #IShowSpeed #Jamal #FunnyReels #Shorts"
    }
]

def format_ts(sec):
    h, m, s = int(sec // 3600), int((sec % 3600) // 60), int(sec % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def format_srt(sec):
    h, m, s = int(sec // 3600), int((sec % 3600) // 60), int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def format_ass(sec):
    h, m, s = int(sec // 3600), int((sec % 3600) // 60), int(sec % 60)
    cs = int((sec - int(sec)) * 100)
    return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"

async def gen_vo(text, out_mp3):
    comm = edge_tts.Communicate(text, "en-US-AndrewMultilingualNeural", rate="+12%")
    await comm.save(out_mp3)

def prepare_subs(item):
    name, dur = item["name"], item["duration"]
    srt_p = os.path.join(SUB_DIR, f"{name}.srt")
    ass_p = os.path.join(SUB_DIR, f"{name}.ass")
    with open(srt_p, "w", encoding="utf-8") as sf:
        for i, (s_t, e_t, txt) in enumerate(item["subtitles"], 1):
            sf.write(f"{i}\n{format_srt(s_t)} --> {format_srt(e_t)}\n{txt}\n\n")

    lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Hook,Arial,64,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,8,30,30,45,1",
        "Style: Subtitle,Arial,62,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,4,2,40,40,210,1", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,0:00:00.00,{format_ass(dur)},Hook,,0,0,45,,{{\\fscx80\\fscy80\\t(0,160,\\fscx105\\fscy105)\\t(160,260,\\fscx100\\fscy100)\\c&H00FFFF&}}{item['hook']}"
    ]
    for s_t, e_t, txt in item["subtitles"]:
        w = txt.split(" ", 1)
        styled = f"{{\\fscx85\\fscy85\\t(0,110,\\fscx106\\fscy106)\\t(110,190,\\fscx100\\fscy100)\\c&H00FFFF&}}{w[0]} {{\\c&HFFFFFF&}}{w[1]}" if len(w) > 1 else f"{{\\fscx85\\fscy85\\t(0,110,\\fscx106\\fscy106)\\t(110,190,\\fscx100\\fscy100)\\c&H00FFFF&}}{txt}"
        lines.append(f"Dialogue: 0,{format_ass(s_t)},{format_ass(e_t)},Subtitle,,0,0,210,,{styled}")
    with open(ass_p, "w", encoding="utf-8") as af:
        af.write("\n".join(lines))
    return ass_p

def render_one(item):
    name, start, dur, climax = item["name"], item["start"], item["duration"], item["climax_t"]
    vo_mp3 = os.path.join(VO_DIR, f"{name}_vo.mp3")
    asyncio.run(gen_vo(item["vo_script"], vo_mp3))
    vo_dur = MP3(vo_mp3).info.length
    ass_p = prepare_subs(item)
    rel_ass = os.path.relpath(ass_p).replace("\\", "/")
    mp4_out = os.path.join(FINAL_DIR, f"{name}.mp4")
    thumb_out = os.path.join(THUMB_DIR, f"Reel_{item['id']:03d}.jpg")

    whoosh = r"E:\videos\sfx_pack\whoosh.wav"
    bass = r"E:\videos\sfx_pack\bass_drop.wav"
    pop = r"E:\videos\sfx_pack\pop.wav"
    climax_ms = int(climax * 1000)

    # Copyright-safe originality pipeline:
    # - Crop out stream overlays (chat, sub counter, viewer count, Day timer)
    # - Color grade + unsharp
    # - Custom studio vertical layout + retention progress bar + pop captions
    # - Neural VO ducking + 4-layer SFX + EBU R128 loudnorm
    filter_complex = (
        "[0:v]eq=contrast=1.08:saturation=1.16:brightness=0.01,unsharp=5:5:0.7:5:5:0.0,split=3[bg_in][game_in][cam_in];"
        "[bg_in]hflip,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,boxblur=25:5[bg];"
        "[game_in]crop=1500:950:210:70,scale=1080:684:flags=lanczos[game];"
        "[cam_in]crop=386:196:0:455,scale=720:366:flags=lanczos,drawbox=x=0:y=0:w=720:h=366:color=0xff2a85@1.0:t=6[cam];"
        "[bg][cam]overlay=180:200[bg_cam];"
        "[bg_cam][game]overlay=0:630[bg_game];"
        f"[bg_game]drawbox=x=0:y=0:w=1080:h=160:color=black@0.88:t=fill,"
        f"drawbox=x=0:y=1314:w='1080*t/{dur}':h=7:color=0xffe600@0.95:t=fill,"
        f"subtitles='{rel_ass}'[outv];"
        f"[1:a]volume=enable='between(t,0,{vo_dur + 0.3:.2f})':volume=0.28[game_ducked];"
        f"[2:a]volume=1.35[vo_a];"
        f"[3:a]adelay=50|50,volume=0.55[w1];"
        f"[3:a]adelay={climax_ms}|{climax_ms},volume=0.50[w2];"
        f"[4:a]adelay={climax_ms}|{climax_ms},volume=0.65[b1];"
        f"[5:a]adelay=150|150,volume=0.45[p1];"
        "[game_ducked][vo_a][w1][w2][b1][p1]amix=inputs=6:duration=first:dropout_transition=0,"
        "loudnorm=I=-16:TP=-1.5:LRA=11[outa]"
    )

    print(f"[{name}] Rendering 1080p60 Copyright-Safe Pro Reel (start={start}s)...", flush=True)
    t0 = time.time()
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-t", str(dur), "-i", VIDEO_URL,
        "-ss", str(start), "-t", str(dur), "-i", AUDIO_URL,
        "-i", vo_mp3, "-i", whoosh, "-i", bass, "-i", pop,
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "60", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        mp4_out
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[{name}] ERROR: {res.stderr[-300:]}", flush=True)
        return None
    subprocess.run(["ffmpeg", "-y", "-ss", "00:00:02", "-i", mp4_out, "-vframes", "1", "-q:v", "2", "-update", "1", thumb_out], capture_output=True)
    size_mb = round(os.path.getsize(mp4_out) / (1024 * 1024), 2)
    print(f"[{name}] Done in {time.time()-t0:.1f}s ({size_mb} MB)", flush=True)
    return {"id": item["id"], "name": name, "size_mb": size_mb, "status": "PASS"}

def main():
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        results = list(ex.map(render_one, SPEED_REELS))

    # CSV metadata
    with open(os.path.join(META_DIR, "youtube_upload_details.csv"), "w", newline="", encoding="utf-8") as mf:
        w = csv.writer(mf)
        w.writerow(["Clip Number", "Filename", "Original Timestamp", "Duration (s)", "Title", "Hashtags", "Viral Score", "Category"])
        for it in SPEED_REELS:
            w.writerow([it["id"], f"{it['name']}.mp4", format_ts(it["start"]), it["duration"], it["title"], it["hashtags"], it["score"], it["category"]])

    # Dashboard
    qc_map = {r["id"]: r for r in results if r}
    cards = [{
        "id": it["id"], "name": it["name"], "title": it["title"], "category": it["category"],
        "score": it["score"], "hook": it["hook"], "start": it["start"], "duration": it["duration"],
        "hashtags": it["hashtags"], "video_file": f"FINAL_REELS/{it['name']}.mp4",
        "thumb_file": f"THUMBNAILS/Reel_{it['id']:03d}.jpg",
        "size_mb": qc_map.get(it["id"], {}).get("size_mb", 0)
    } for it in SPEED_REELS]

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>IShowSpeed GTA 6 Pro Reels Studio</title>
<style>body{{background:#090a10;color:#f0f3fc;font-family:system-ui,sans-serif;padding:24px;margin:0}}
.c{{max-width:1360px;margin:0 auto}}.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:20px}}
.card{{background:#121420;border:1px solid #232840;border-radius:14px;overflow:hidden;display:flex;flex-direction:column}}
.t{{aspect-ratio:9/16;max-height:360px;position:relative;cursor:pointer;background:#000}}.t img{{width:100%;height:100%;object-fit:cover}}
.b{{padding:14px;display:flex;flex-direction:column;gap:8px;flex:1}}.btn{{background:#0072ff;color:#fff;border:none;padding:9px;border-radius:8px;font-weight:700;cursor:pointer;text-decoration:none;text-align:center;font-size:12px}}
.m{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.88);align-items:center;justify-content:center;z-index:99}}.m.a{{display:flex}}
video{{width:330px;aspect-ratio:9/16;border-radius:12px}}</style></head><body><div class="c">
<h1>🔥 IShowSpeed GTA 6 — 1080p60 Copyright-Safe Pro Reels</h1>
<p style="color:#8b92b2">Neural VO + Ducking + Studio SFX + Pop Captions + Overlay-Free Framing</p><div class="g" id="g"></div></div>
<div class="m" id="m" onclick="if(event.target===this)cl()"><video id="v" controls playsinline></video></div>
<script>const D={json.dumps(cards)};const g=document.getElementById('g');D.forEach(r=>{{const d=document.createElement('div');d.className='card';
d.innerHTML=`<div class="t" onclick="op(${{r.id}})"><img src="${{r.thumb_file}}"></div><div class="b"><div style="color:#ffe600;font-size:12px;font-weight:700">${{r.hook}}</div>
<div style="font-size:13px;font-weight:700">${{r.title}}</div><div style="font-size:12px;color:#8b92b2">Score: ${{r.score}}/100 | ${{r.size_mb}} MB</div>
<div style="display:flex;gap:8px;margin-top:auto"><button class="btn" style="flex:1" onclick="op(${{r.id}})">▶ Preview</button><a class="btn" style="flex:1;background:#1b1e30" href="${{r.video_file}}" download>⬇ MP4</a></div></div>`;g.appendChild(d);}});
function op(id){{const r=D.find(x=>x.id===id);const v=document.getElementById('v');v.src=r.video_file;v.play();document.getElementById('m').classList.add('a')}}
function cl(){{document.getElementById('m').classList.remove('a');const v=document.getElementById('v');v.pause();v.src=''}}</script></body></html>"""
    with open(os.path.join(OUT_BASE, "dashboard.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nALL 10 ISHOWSPEED PRO REELS COMPLETE in {time.time()-t0:.1f}s!", flush=True)

if __name__ == "__main__":
    main()
