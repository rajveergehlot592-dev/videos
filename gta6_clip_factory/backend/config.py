import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except Exception:
    pass

APP_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_SETTINGS: Dict[str, Any] = {
    "input_dir": str(APP_ROOT / "media" / "input"),
    "working_dir": str(APP_ROOT / "media" / "working"),
    "thumbnails_dir": str(APP_ROOT / "media" / "thumbnails"),
    "candidates_dir": str(APP_ROOT / "media" / "candidates"),
    "exports_dir": str(APP_ROOT / "media" / "exports"),
    "projects_dir": str(APP_ROOT / "projects"),
    "logs_dir": str(APP_ROOT / "logs"),
    "reports_dir": str(APP_ROOT / "reports"),
    "min_clip_duration": 15.0,
    "max_clip_duration": 55.0,
    "pre_padding": 3.0,
    "post_padding": 3.0,
    "merge_gap": 4.0,
    "default_layout": "blurred_bg",
    "default_fps": 30,
    "default_crf": 20,
    "max_concurrent_exports": 2,
    "enable_transcription": True,
    "whisper_cli_path": "",
    "caption_font": "Arial",
    "caption_size": 52,
    "caption_color": "#FFFFFF",
    "caption_highlight_color": "#FFE600",
    "safe_margin_bottom": 210,
}

SETTINGS_FILE = APP_ROOT / "projects" / "settings.json"


def load_settings() -> Dict[str, Any]:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if SETTINGS_FILE.exists():
        try:
            saved = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            merged = {**DEFAULT_SETTINGS, **saved}
            return merged
        except Exception:
            pass
    save_settings(DEFAULT_SETTINGS)
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    merged = {**DEFAULT_SETTINGS, **settings}
    for key in [
        "input_dir", "working_dir", "thumbnails_dir", "candidates_dir",
        "exports_dir", "projects_dir", "logs_dir", "reports_dir"
    ]:
        Path(merged[key]).mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return merged


def get_binaries() -> Dict[str, Any]:
    ffmpeg_bin = shutil.which("ffmpeg")
    ffprobe_bin = shutil.which("ffprobe")
    settings = load_settings()
    whisper_bin = settings.get("whisper_cli_path") or shutil.which("whisper-cli") or shutil.which("whisper")
    if whisper_bin and not Path(whisper_bin).exists():
        whisper_bin = None

    has_cv2 = False
    has_scenedetect = False
    try:
        import cv2  # noqa: F401
        has_cv2 = True
    except Exception:
        pass
    try:
        import scenedetect  # noqa: F401
        has_scenedetect = True
    except Exception:
        pass

    return {
        "ffmpeg": ffmpeg_bin,
        "ffprobe": ffprobe_bin,
        "whisper": whisper_bin,
        "opencv": has_cv2,
        "scenedetect": has_scenedetect,
    }


def get_disk_space_gb(path_str: str) -> float:
    try:
        p = Path(path_str)
        while not p.exists() and p.parent != p:
            p = p.parent
        usage = shutil.disk_usage(str(p))
        return round(usage.free / (1024 ** 3), 2)
    except Exception:
        return 0.0
