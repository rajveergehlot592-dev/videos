import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from .config import get_binaries

SUPPORTED_VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".ts", ".flv"}


def compute_fast_hash(filepath: Path) -> str:
    h = hashlib.sha256()
    size = filepath.stat().st_size
    h.update(str(size).encode("utf-8"))
    with filepath.open("rb") as f:
        h.update(f.read(1024 * 1024))
    return h.hexdigest()[:16]


def _parse_fps(rate_str: Optional[str]) -> float:
    if not rate_str or rate_str in ("0/0", "N/A"):
        return 30.0
    if "/" in rate_str:
        num, den = rate_str.split("/", 1)
        try:
            d = float(den)
            return round(float(num) / d, 2) if d > 0 else 30.0
        except Exception:
            return 30.0
    try:
        return round(float(rate_str), 2)
    except Exception:
        return 30.0


def probe_video_file(filepath_str: str) -> Dict[str, Any]:
    path = Path(filepath_str)
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {filepath_str}")
    if path.suffix.lower() not in SUPPORTED_VIDEO_EXTS:
        raise ValueError(f"Unsupported file extension '{path.suffix}': {path.name}")

    bins = get_binaries()
    ffprobe_bin = bins.get("ffprobe")
    ffmpeg_bin = bins.get("ffmpeg")

    if not ffmpeg_bin and not ffprobe_bin:
        raise RuntimeError("Neither ffprobe nor ffmpeg is available on PATH or in .venv.")

    if ffprobe_bin:
        return _probe_with_ffprobe(ffprobe_bin, path)
    return _probe_with_ffmpeg_fallback(ffmpeg_bin, path)


def _probe_with_ffprobe(ffprobe_bin: str, path: Path) -> Dict[str, Any]:
    cmd = [
        ffprobe_bin, "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0 or not res.stdout.strip():
        raise ValueError(f"Corrupted or unreadable media file: {path.name}")

    try:
        data = json.loads(res.stdout)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse ffprobe output for {path.name}: {e}")

    streams = data.get("streams", [])
    fmt = data.get("format", {})

    v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    if not v_stream:
        raise ValueError(f"No video stream found in file: {path.name}")

    a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    width = int(v_stream.get("width") or 0)
    height = int(v_stream.get("height") or 0)
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid video dimensions ({width}x{height}) in: {path.name}")

    duration = float(fmt.get("duration") or v_stream.get("duration") or 0.0)
    fps = _parse_fps(v_stream.get("avg_frame_rate") or v_stream.get("r_frame_rate"))

    rotation = 0
    tags = v_stream.get("tags") or {}
    if "rotate" in tags:
        try:
            rotation = int(float(tags["rotate"])) % 360
        except Exception:
            rotation = 0
    for sd in v_stream.get("side_data_list") or []:
        if "rotation" in sd:
            try:
                rotation = int(float(sd["rotation"])) % 360
            except Exception:
                pass

    return {
        "filename": path.name,
        "filepath": str(path.resolve()),
        "file_hash": compute_fast_hash(path),
        "size_bytes": path.stat().st_size,
        "duration": round(duration, 3),
        "width": width,
        "height": height,
        "fps": fps,
        "rotation": rotation,
        "vcodec": v_stream.get("codec_name") or "unknown",
        "acodec": a_stream.get("codec_name") if a_stream else None,
        "has_audio": a_stream is not None,
        "audio_sample_rate": int(a_stream["sample_rate"]) if a_stream and a_stream.get("sample_rate") else None,
        "audio_channels": int(a_stream["channels"]) if a_stream and a_stream.get("channels") else None,
        "imported_at": datetime.now(timezone.utc).isoformat(),
    }


def _probe_with_ffmpeg_fallback(ffmpeg_bin: str, path: Path) -> Dict[str, Any]:
    cmd = [ffmpeg_bin, "-hide_banner", "-i", str(path)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    stderr = res.stderr or ""

    if "Invalid data found" in stderr or "could not find codec parameters" in stderr:
        raise ValueError(f"Corrupted or unreadable media file: {path.name}")

    dur_m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
    duration = 0.0
    if dur_m:
        h, m, s = dur_m.groups()
        duration = int(h) * 3600 + int(m) * 60 + float(s)

    v_m = re.search(r"Stream #\d+:\d+.*?Video:\s*([^,\s]+).*?,\s*(\d{2,5})x(\d{2,5})", stderr)
    if not v_m:
        raise ValueError(f"No valid video stream found in: {path.name}")

    vcodec, w_s, h_s = v_m.groups()
    width, height = int(w_s), int(h_s)

    fps_m = re.search(r"(\d+(?:\.\d+)?)\s*fps", stderr)
    fps = float(fps_m.group(1)) if fps_m else 30.0

    a_m = re.search(r"Stream #\d+:\d+.*?Audio:\s*([^,\s]+).*?,\s*(\d+)\s*Hz", stderr)
    has_audio = a_m is not None
    acodec = a_m.group(1) if a_m else None
    sample_rate = int(a_m.group(2)) if a_m else None

    rot_m = re.search(r"rotate\s*:\s*(-?\d+)", stderr)
    rotation = int(rot_m.group(1)) % 360 if rot_m else 0

    return {
        "filename": path.name,
        "filepath": str(path.resolve()),
        "file_hash": compute_fast_hash(path),
        "size_bytes": path.stat().st_size,
        "duration": round(duration, 3),
        "width": width,
        "height": height,
        "fps": round(fps, 2),
        "rotation": rotation,
        "vcodec": vcodec,
        "acodec": acodec,
        "has_audio": has_audio,
        "audio_sample_rate": sample_rate,
        "audio_channels": 2 if has_audio else None,
        "imported_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_thumbnail(filepath_str: str, timestamp: float, out_path_str: str, width: int = 480) -> bool:
    bins = get_binaries()
    ffmpeg_bin = bins.get("ffmpeg")
    if not ffmpeg_bin:
        return False
    out_path = Path(out_path_str)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{max(0.0, timestamp):.3f}",
        "-i", filepath_str,
        "-vframes", "1",
        "-vf", f"scale={width}:-2",
        "-q:v", "3",
        "-update", "1",
        str(out_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return res.returncode == 0 and out_path.exists()
