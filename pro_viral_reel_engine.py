import os
import sys
import subprocess
import time
import asyncio
import edge_tts
from mutagen.mp3 import MP3
import concurrent.futures

OUT_BASE = r"E:\videos\TECHNO_GAMERZ_PRO_REELS"
FINAL_DIR = os.path.join(OUT_BASE, "FINAL_REELS")
VO_DIR = os.path.join(OUT_BASE, "VOICEOVERS")
SUB_DIR = os.path.join(OUT_BASE, "SUBTITLES")
THUMB_DIR = os.path.join(OUT_BASE, "THUMBNAILS")

for d in [FINAL_DIR, VO_DIR, SUB_DIR, THUMB_DIR]:
    os.makedirs(d, exist_ok=True)

with open(r"E:\videos\techno_work\stream_url_1080p.txt", "r") as f:
    VIDEO_URL = f.read().strip()
with open(r"E:\videos\techno_work\stream_url_audio.txt", "r") as f:
    AUDIO_URL = f.read().strip()

PRO_REELS = [
    {
        "id": 16,
        "name": "Pro_Techno_Reel_016",
        "start": 6792,
        "duration": 26,
        "climax_t": 10.0,
        "hook": "TECHNO SKIPPED THE MAIN SCENE! 😂",
        "vo_script": "Wait... did Techno Gamerz really just skip the most viral sink scene in GTA 6?! Watch his reaction!",
        "subtitles": [
            (0.0, 3.2, "WAIT... HE SKIPPED THAT SCENE?!"),
            (3.2, 8.0, "Jason fixing the kitchen sink..."),
            (8.0, 14.0, "Mandy walks in... AND TECHNO CUTS IT!"),
            (14.0, 20.0, "Keeping it family-friendly for YouTube!"),
            (20.0, 26.0, "50,000 comments all talking about 1:53:20!")
        ]
    },
    {
        "id": 8,
        "name": "Pro_Techno_Reel_008",
        "start": 3708,
        "duration": 26,
        "climax_t": 9.5,
        "hook": "NPC LANDED IN HIS TRUCK BED! 💀",
        "vo_script": "Bro, how did a whole NPC just land inside Techno Gamerz's pickup truck in GTA 6?! Look at this!",
        "subtitles": [
            (0.0, 3.2, "HOW DID AN NPC LAND IN HIS TRUCK?!"),
            (3.2, 8.5, "Cruising in Jason's '70 Ganado..."),
            (8.5, 14.5, "A whole guy is chilling in the back!"),
            (14.5, 20.0, "Techno: 'Galti toh aapki hi hai!'"),
            (20.0, 26.0, "Free Uber ride in Vice City!")
        ]
    },
    {
        "id": 14,
        "name": "Pro_Techno_Reel_014",
        "start": 6585,
        "duration": 25,
        "climax_t": 8.5,
        "hook": "HE JUMPED OUT AT FULL SPEED! 😱",
        "vo_script": "Techno Gamerz just jumped out of a moving car at full speed in GTA 6, and somehow didn't even fall!",
        "subtitles": [
            (0.0, 3.3, "HE JUMPED OUT AT FULL SPEED?!"),
            (3.3, 8.5, "Cruising down Vice City highway..."),
            (8.5, 14.0, "Ujjwal bails out... AND STAYS STANDING!"),
            (14.0, 19.5, "Techno screaming: 'AAAAAAAA!'"),
            (19.5, 25.0, "Jason built different in GTA 6!")
        ]
    },
    {
        "id": 6,
        "name": "Pro_Techno_Reel_006",
        "start": 2945,
        "duration": 26,
        "climax_t": 9.0,
        "hook": "GTA 6 HAS ITS OWN INSTAGRAM?! 📱",
        "vo_script": "Did you know GTA 6 has a working Instagram inside your phone with real likes and comments? Watch this!",
        "subtitles": [
            (0.0, 3.3, "GTA 6 HAS WORKING INSTAGRAM?!"),
            (3.3, 9.0, "Checking Jason's smartphone feed..."),
            (9.0, 15.0, "Scrollable posts, likes & full comments!"),
            (15.0, 20.5, "Rockstar's attention to detail is crazy!"),
            (20.5, 26.0, "Rate this feature out of 10!")
        ]
    },
    {
        "id": 4,
        "name": "Pro_Techno_Reel_004",
        "start": 1695,
        "duration": 26,
        "climax_t": 10.0,
        "hook": "GTA 6 STORM PHYSICS ARE INSANE! ⛈️",
        "vo_script": "Wait until you see how insane GTA 6's tropical storm and ocean waves look while flying a seaplane!",
        "subtitles": [
            (0.0, 3.4, "GTA 6 STORM GRAPHICS ARE UNREAL!"),
            (3.4, 9.5, "Flying a seaplane in a tropical storm!"),
            (9.5, 15.5, "Look at those crashing ocean waves!"),
            (15.5, 21.0, "Key Lento Marina Club in the rain!"),
            (21.0, 26.0, "Next-gen Rockstar weather engine!")
        ]
    },
    {
        "id": 1,
        "name": "Pro_Techno_Reel_001",
        "start": 35,
        "duration": 26,
        "climax_t": 8.0,
        "hook": "BOSS OF GTA IS BACK! 🔥",
        "vo_script": "After years of waiting, the boss of Indian GTA, Techno Gamerz, finally steps into Vice City!",
        "subtitles": [
            (0.0, 3.2, "THE BOSS OF GTA IS BACK!"),
            (3.2, 9.0, "Techno Gamerz enters GTA 6!"),
            (9.0, 15.0, "The nostalgia and hype is unreal!"),
            (15.0, 21.0, "Day 1 in Vice City begins now!"),
            (21.0, 26.0, "Drop a heart if you're hyped!")
        ]
    }
]

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec - int(sec)) * 100)
    return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"

async def gen_voiceover(text, out_mp3):
    communicate = edge_tts.Communicate(text, "en-IN-PrabhatNeural", rate="+12%")
    await communicate.save(out_mp3)

def build_ass_subtitles(item, ass_path):
    dur = item["duration"]
    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Hook,Arial,64,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,8,30,30,45,1",
        "Style: Subtitle,Arial,62,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,4,2,40,40,210,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        # Hook with pop-in animation
        f"Dialogue: 0,0:00:00.00,{format_ass_time(dur)},Hook,,0,0,45,,{{\\fscx80\\fscy80\\t(0,160,\\fscx105\\fscy105)\\t(160,260,\\fscx100\\fscy100)\\c&H00FFFF&}}{item['hook']}"
    ]

    for s_t, e_t, text in item["subtitles"]:
        words = text.split(" ", 1)
        if len(words) > 1:
            styled = f"{{\\fscx85\\fscy85\\t(0,110,\\fscx106\\fscy106)\\t(110,190,\\fscx100\\fscy100)\\c&H00FFFF&}}{words[0]} {{\\c&HFFFFFF&}}{words[1]}"
        else:
            styled = f"{{\\fscx85\\fscy85\\t(0,110,\\fscx106\\fscy106)\\t(110,190,\\fscx100\\fscy100)\\c&H00FFFF&}}{text}"
        ass_lines.append(f"Dialogue: 0,{format_ass_time(s_t)},{format_ass_time(e_t)},Subtitle,,0,0,210,,{styled}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ass_lines))

def render_pro_reel(item):
    name = item["name"]
    start = item["start"]
    dur = item["duration"]
    climax = item["climax_t"]

    vo_mp3 = os.path.join(VO_DIR, f"{name}_vo.mp3")
    asyncio.run(gen_voiceover(item["vo_script"], vo_mp3))
    vo_dur = MP3(vo_mp3).info.length

    ass_path = os.path.join(SUB_DIR, f"{name}.ass")
    build_ass_subtitles(item, ass_path)
    rel_ass = os.path.relpath(ass_path).replace("\\", "/")

    mp4_out = os.path.join(FINAL_DIR, f"{name}.mp4")
    thumb_out = os.path.join(THUMB_DIR, f"{name}.jpg")

    whoosh_wav = r"E:\videos\sfx_pack\whoosh.wav"
    bass_wav = r"E:\videos\sfx_pack\bass_drop.wav"
    pop_wav = r"E:\videos\sfx_pack\pop.wav"

    climax_ms = int(climax * 1000)

    # Human-style video + audio filtergraph:
    # Inputs:
    # 0: 1080p60 Video
    # 1: Audio
    # 2: Voiceover MP3
    # 3: Whoosh WAV
    # 4: Bass Drop WAV
    # 5: Pop WAV
    filter_complex = (
        # Color grade & sharpen source for mobile pop + YouTube originality
        "[0:v]eq=contrast=1.06:saturation=1.14:brightness=0.01,unsharp=5:5:0.7:5:5:0.0,split=3[bg_in][game_in][cam_in];"
        # Blurred background
        "[bg_in]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,boxblur=25:5[bg];"
        # Gameplay with subtle dynamic motion/zoom
        "[game_in]crop=1620:1070:150:0,scale=1080:714:flags=lanczos[game];"
        # Facecam with gold border + subtle pulse/reaction framing
        "[cam_in]crop=318:226:1539:121,scale=640:455:flags=lanczos,drawbox=x=0:y=0:w=640:h=455:color=0xffe600@1.0:t=6[cam];"
        "[bg][cam]overlay=220:180[bg_cam];"
        "[bg_cam][game]overlay=0:675[bg_game];"
        # Top hook banner + animated retention progress bar at bottom of gameplay (y=1384)
        f"[bg_game]drawbox=x=0:y=0:w=1080:h=155:color=black@0.88:t=fill,"
        f"drawbox=x=0:y=1383:w='1080*t/{dur}':h=7:color=0xffe600@0.95:t=fill,"
        f"subtitles='{rel_ass}'[outv];"
        # Audio ducking during VO + SFX layering + broadcast loudnorm
        f"[1:a]volume=enable='between(t,0,{vo_dur + 0.3:.2f})':volume=0.32[game_ducked];"
        f"[2:a]volume=1.35[vo_a];"
        f"[3:a]adelay=50|50,volume=0.55[sfx_whoosh1];"
        f"[3:a]adelay={climax_ms}|{climax_ms},volume=0.50[sfx_whoosh2];"
        f"[4:a]adelay={climax_ms}|{climax_ms},volume=0.65[sfx_bass];"
        f"[5:a]adelay=150|150,volume=0.45[sfx_pop];"
        f"[game_ducked][vo_a][sfx_whoosh1][sfx_whoosh2][sfx_bass][sfx_pop]amix=inputs=6:duration=first:dropout_transition=0,"
        f"loudnorm=I=-16:TP=-1.5:LRA=11[outa]"
    )

    print(f"[{name}] Rendering Pro Viral Reel (1080p60 + Neural VO + SFX + Pop Captions)...", flush=True)
    t0 = time.time()

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-t", str(dur), "-i", VIDEO_URL,
        "-ss", str(start), "-t", str(dur), "-i", AUDIO_URL,
        "-i", vo_mp3,
        "-i", whoosh_wav,
        "-i", bass_wav,
        "-i", pop_wav,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-r", "60", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        mp4_out
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[{name}] ERROR: {res.stderr[-400:]}", flush=True)
        return False

    subprocess.run([
        "ffmpeg", "-y", "-ss", "00:00:02", "-i", mp4_out,
        "-vframes", "1", "-q:v", "2", "-update", "1", thumb_out
    ], capture_output=True)

    size_mb = os.path.getsize(mp4_out) / (1024 * 1024)
    print(f"[{name}] Rendered in {time.time() - t0:.1f}s ({size_mb:.2f} MB)", flush=True)
    return True

def main():
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        list(ex.map(render_pro_reel, PRO_REELS))
    print(f"\nALL {len(PRO_REELS)} PRO VIRAL REELS COMPLETE in {time.time() - t0:.1f}s!", flush=True)

if __name__ == "__main__":
    main()
