import asyncio
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple

import yt_dlp

from .config import load_settings
from .models import CandidateClip, EditorConfig, CaptionSegment, SignalBreakdown
from .metadata_gen import generate_clip_metadata


def _parse_ts(s: str) -> int:
    m = re.search(r"(\d+):(\d{2})(?::(\d{2}))?", s)
    if not m:
        return -1
    parts = [p for p in m.groups() if p is not None]
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return -1


def extract_youtube_source(url: str, max_comments: int = 200) -> Tuple[Dict[str, Any], List[CandidateClip]]:
    settings = load_settings()
    ydl_opts = {
        "skip_download": True,
        "getcomments": True,
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"comment_sort": ["top"], "max_comments": [str(max_comments), "all", "100", "0"]}},
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get("formats", [])
    v_fmt = next((f for f in formats if f.get("format_id") == "299" and f.get("protocol") == "https"), None)
    if not v_fmt:
        v_fmt = next((f for f in formats if (f.get("height") or 0) >= 1070 and "avc1" in (f.get("vcodec") or "") and f.get("protocol") == "https"), None)
    if not v_fmt:
        v_fmt = next((f for f in formats if (f.get("height") or 0) >= 720 and f.get("vcodec") != "none" and f.get("protocol") == "https"), None)
    if not v_fmt:
        raise ValueError("Could not find a compatible HD HTTPS video stream for this YouTube URL.")

    a_fmt = next((f for f in formats if f.get("format_id") == "140" and f.get("protocol") == "https"), None)
    if not a_fmt:
        a_fmt = next((f for f in formats if f.get("vcodec") == "none" and f.get("acodec") != "none" and f.get("protocol") == "https"), None)

    duration = float(info.get("duration") or 0.0)
    rec_id = f"yt_{info.get('id', uuid.uuid4().hex[:8])}"
    rec = {
        "id": rec_id,
        "source_type": "youtube",
        "youtube_url": url,
        "filename": f"{info.get('title', 'YouTube Video')[:60]}",
        "filepath": v_fmt["url"],
        "audio_filepath": a_fmt["url"] if a_fmt else None,
        "file_hash": rec_id,
        "size_bytes": 0,
        "duration": duration,
        "width": int(v_fmt.get("width") or 1920),
        "height": int(v_fmt.get("height") or 1080),
        "fps": float(v_fmt.get("fps") or 60.0),
        "rotation": 0,
        "vcodec": v_fmt.get("vcodec") or "h264",
        "acodec": a_fmt.get("acodec") if a_fmt else None,
        "has_audio": a_fmt is not None,
        "thumbnail_url": info.get("thumbnail"),
        "uploader": info.get("uploader") or "Creator",
        "status": "analyzed",
        "imported_at": datetime.now(timezone.utc).isoformat(),
    }

    # Extract top timestamped moments from comments
    comments = info.get("comments") or []
    ts_hits: List[Tuple[int, int, str]] = []
    for c in comments:
        likes = int(c.get("like_count") or 0)
        for line in (c.get("text") or "").splitlines():
            line = line.strip()
            t = _parse_ts(line)
            if 0 <= t < max(1.0, duration - 15.0):
                ts_hits.append((likes, t, line))

    # Cluster nearby timestamps (within 35s)
    ts_hits.sort(key=lambda x: x[0], reverse=True)
    picked: List[Tuple[int, int, str]] = []
    for likes, t, line in ts_hits:
        if all(abs(t - pt) > 35 for _, pt, _ in picked):
            picked.append((likes, t, line))
        if len(picked) >= 12:
            break

    # Fallback evenly spaced highlights if comments had no timestamps
    if not picked and duration > 30:
        step = max(30.0, duration / 7.0)
        t_cur = 15.0
        while t_cur < duration - 25.0 and len(picked) < 6:
            picked.append((0, int(t_cur), f"Highlight at {int(t_cur)}s"))
            t_cur += step

    candidates: List[CandidateClip] = []
    for idx, (likes, t, line) in enumerate(picked, 1):
        start_t = float(max(0, t - 4))
        dur = 25.0
        end_t = min(duration, start_t + dur)
        clip_id = f"clip_{uuid.uuid4().hex[:8]}"
        score = round(min(99.0, 82.0 + min(17.0, (likes ** 0.35) * 2.5 + (12 - idx) * 0.6)), 1)
        clean_note = re.sub(r"\s+", " ", line)[:80]

        clip = CandidateClip(
            id=clip_id,
            recording_id=rec_id,
            source_filename=rec["filename"],
            start_time=start_t,
            end_time=end_t,
            duration=round(end_t - start_t, 2),
            heuristic_score=score,
            rationale=f"Community highlight ({likes} likes): \"{clean_note}\"",
            signals=SignalBreakdown(audio_peak=0.85, motion_score=0.80, scene_change=0.70, speech_event=0.90),
            thumbnail_url=info.get("thumbnail"),
            status="approved" if idx <= 3 else "pending",
            editor=EditorConfig(
                layout="blurred_bg",
                fps=int(min(60, rec["fps"])),
                crf=19,
                hook_text=f"WAIT FOR THIS MOMENT! 🔥",
                effect_color_boost=True,
                effect_progress_bar=True,
                effect_loudnorm=True,
                captions=[
                    CaptionSegment(start=0.0, end=4.0, text="WAIT UNTIL YOU SEE THIS!"),
                    CaptionSegment(start=4.0, end=12.0, text=clean_note[:48] or "INSANE GAMEPLAY MOMENT!"),
                    CaptionSegment(start=12.0, end=20.0, text="CHAT WENT COMPLETELY WILD!"),
                ],
            ),
        )
        clip.metadata = generate_clip_metadata(clip)
        clip.metadata["vo_script"] = f"Wait until you see what just happened in {rec['uploader']}'s GTA 6 stream!"
        clip.metadata["vo_voice"] = "en-US-AndrewMultilingualNeural"
        clip.metadata["pro_mode"] = True
        candidates.append(clip)

    return rec, candidates
