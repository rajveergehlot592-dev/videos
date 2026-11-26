import asyncio
import os
import subprocess
from pathlib import Path
from typing import Callable, Optional, List

import edge_tts
from mutagen.mp3 import MP3

from .config import get_binaries, load_settings
from .models import CandidateClip, EditorConfig, CaptionSegment


def _hex_to_ass_bgr(hex_color: str) -> str:
    h = hex_color.strip().lstrip("#")
    if len(h) != 6:
        return "&H00FFFFFF"
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b}{g}{r}".upper()


def _escape_ffmpeg_filter_path(p: Path) -> str:
    s = str(p.resolve()).replace("\\", "/")
    s = s.replace(":", "\\:")
    s = s.replace("'", "\\'")
    return s


def _format_ass_time(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec - int(sec)) * 100)
    return f"{h:01d}:{m:02d}:{s:02d}.{cs:02d}"


def _format_srt_time(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec - int(sec)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt_file(captions: List[CaptionSegment], out_srt: Path) -> Optional[Path]:
    if not captions:
        return None
    out_srt.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for idx, seg in enumerate(captions, 1):
        lines.append(f"{idx}\n{_format_srt_time(seg.start)} --> {_format_srt_time(seg.end)}\n{seg.text}\n")
    out_srt.write_text("\n".join(lines), encoding="utf-8")
    return out_srt


def write_ass_file(editor: EditorConfig, duration: float, out_ass: Path) -> Optional[Path]:
    has_hook = editor.hook_enabled and bool(editor.hook_text.strip())
    has_caps = editor.captions_enabled and len(editor.captions) > 0
    if not has_hook and not has_caps:
        return None

    out_ass.parent.mkdir(parents=True, exist_ok=True)
    primary_bgr = _hex_to_ass_bgr(editor.text_color)
    hl_bgr = _hex_to_ass_bgr(editor.highlight_color)
    font = editor.font_name or "Arial"
    fsize = editor.font_size
    margin_v = editor.safe_margin_bottom

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Hook,{font},58,{hl_bgr},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,8,40,40,70,1",
        f"Style: Caption,{font},{fsize},{primary_bgr},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,50,50,{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    if has_hook:
        hook_dur = min(duration, 4.0)
        lines.append(f"Dialogue: 0,0:00:00.00,{_format_ass_time(hook_dur)},Hook,,0,0,70,,{editor.hook_text.strip()}")

    if has_caps:
        for seg in editor.captions:
            s_t = max(0.0, min(duration, seg.start))
            e_t = max(s_t + 0.1, min(duration, seg.end))
            words = seg.text.strip().split(" ", 1)
            if len(words) > 1:
                txt = f"{{\\c{hl_bgr}&}}{words[0]} {{\\c{primary_bgr}&}}{words[1]}"
            else:
                txt = f"{{\\c{hl_bgr}&}}{seg.text.strip()}"
            lines.append(f"Dialogue: 0,{_format_ass_time(s_t)},{_format_ass_time(e_t)},Caption,,0,0,{margin_v},,{txt}")

    out_ass.write_text("\n".join(lines), encoding="utf-8")
    return out_ass


def build_filter_complex(editor: EditorConfig, duration: float, ass_path: Optional[Path]) -> str:
    layout = editor.layout
    chains = []

    if layout == "dynamic_crop":
        # Crop 9:16 slice from input with zoom & tracking bias, scale to 1080x1920
        z = max(1.0, min(2.0, editor.zoom))
        tx = max(0.0, min(1.0, editor.track_x))
        ty = max(0.0, min(1.0, editor.track_y))
        chains.append(
            f"[0:v]scale='max(1080,iw*1920/ih)':'max(1920,ih*1080/iw)':flags=lanczos,"
            f"scale=iw*{z:.3f}:ih*{z:.3f}:flags=lanczos,"
            f"crop=1080:1920:'(iw-1080)*{tx:.3f}':'(ih-1920)*{ty:.3f}',setsar=1[base]"
        )
    elif layout == "manual_crop":
        cw = max(0.05, min(1.0, editor.crop_w))
        ch = max(0.05, min(1.0, editor.crop_h))
        cx = max(0.0, min(1.0 - cw, editor.crop_x))
        cy = max(0.0, min(1.0 - ch, editor.crop_y))
        blur = max(1, editor.bg_blur)
        dark = max(0.0, min(0.85, editor.bg_darken))
        chains.append(
            f"[0:v]split=2[bg_in][fg_in];"
            f"[bg_in]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,boxblur={blur}:3,eq=brightness=-{dark:.2f}[bg];"
            f"[fg_in]crop=iw*{cw:.3f}:ih*{ch:.3f}:iw*{cx:.3f}:ih*{cy:.3f},"
            f"scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[base]"
        )
    else:
        # blurred_bg: landscape/portrait centered over blurred darkened 9:16 background
        blur = max(1, editor.bg_blur)
        dark = max(0.0, min(0.85, editor.bg_darken))
        chains.append(
            f"[0:v]split=2[bg_in][fg_in];"
            f"[bg_in]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,boxblur={blur}:3,eq=brightness=-{dark:.2f}[bg];"
            f"[fg_in]scale=1080:1920:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[base]"
        )

    post_filters = []
    if editor.effect_color_boost:
        post_filters.append("eq=contrast=1.06:saturation=1.12")
    if editor.effect_progress_bar and duration > 0:
        post_filters.append(f"drawbox=x=0:y=1912:w='1080*t/{duration:.3f}':h=8:color=0xFFE600@0.95:t=fill")
    if ass_path and ass_path.exists():
        esc = _escape_ffmpeg_filter_path(ass_path)
        post_filters.append(f"subtitles='{esc}'")

    if post_filters:
        chains.append(f"[base]{','.join(post_filters)}[outv]")
    else:
        chains.append("[base]null[outv]")

    return ";".join(chains)


def render_clip(
    source_filepath: str,
    clip: CandidateClip,
    output_mp4: Path,
    has_audio: bool,
    on_process_start: Optional[Callable[[subprocess.Popen], None]] = None,
    fps_override: Optional[int] = None,
    crf_override: Optional[int] = None,
    audio_filepath: Optional[str] = None,
) -> Optional[Path]:
    bins = get_binaries()
    ffmpeg_bin = bins.get("ffmpeg")
    if not ffmpeg_bin:
        raise RuntimeError("FFmpeg binary not found.")

    settings = load_settings()
    output_mp4.parent.mkdir(parents=True, exist_ok=True)
    working_dir = Path(settings["working_dir"])
    working_dir.mkdir(parents=True, exist_ok=True)

    duration = max(0.5, clip.end_time - clip.start_time)
    editor = clip.editor
    fps = fps_override if fps_override is not None else editor.fps
    crf = crf_override if crf_override is not None else editor.crf

    ass_path = write_ass_file(editor, duration, working_dir / f"{clip.id}.ass")
    srt_path = None
    if editor.captions_enabled and editor.captions:
        srt_path = write_srt_file(editor.captions, output_mp4.with_suffix(".srt"))

    filter_complex = build_filter_complex(editor, duration, ass_path)

    # Optional Pro Viral Mode (Neural VO + SFX)
    meta = clip.metadata or {}
    pro_mode = bool(meta.get("pro_mode", False))
    vo_script = (meta.get("vo_script") or "").strip()
    vo_voice = meta.get("vo_voice") or "en-US-AndrewMultilingualNeural"
    sfx_dir = Path(r"E:\videos\sfx_pack")
    has_sfx = (sfx_dir / "whoosh.wav").exists() and (sfx_dir / "bass_drop.wav").exists() and (sfx_dir / "pop.wav").exists()

    cmd = [
        ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{clip.start_time:.3f}",
        "-t", f"{duration:.3f}",
        "-i", source_filepath,
    ]

    audio_idx = 0
    next_idx = 1
    if audio_filepath:
        cmd.extend(["-ss", f"{clip.start_time:.3f}", "-t", f"{duration:.3f}", "-i", audio_filepath])
        audio_idx = next_idx
        next_idx += 1

    vo_mp3 = None
    vo_dur = 0.0
    if pro_mode and vo_script and has_audio:
        vo_mp3 = working_dir / f"{clip.id}_vo.mp3"
        try:
            asyncio.run(edge_tts.Communicate(vo_script, vo_voice, rate="+12%").save(str(vo_mp3)))
            vo_dur = MP3(str(vo_mp3)).info.length
        except Exception:
            vo_mp3 = None

    if pro_mode and vo_mp3 and has_sfx and has_audio:
        vo_idx = next_idx
        w_idx = next_idx + 1
        b_idx = next_idx + 2
        p_idx = next_idx + 3
        cmd.extend([
            "-i", str(vo_mp3),
            "-i", str(sfx_dir / "whoosh.wav"),
            "-i", str(sfx_dir / "bass_drop.wav"),
            "-i", str(sfx_dir / "pop.wav"),
        ])
        climax_ms = int(min(duration * 0.45, 9.0) * 1000)
        filter_complex += (
            f";[{audio_idx}:a]volume=enable='between(t,0,{vo_dur + 0.3:.2f})':volume=0.28[g_duck];"
            f"[{vo_idx}:a]volume=1.35[vo_a];"
            f"[{w_idx}:a]adelay=50|50,volume=0.55[s_w];"
            f"[{b_idx}:a]adelay={climax_ms}|{climax_ms},volume=0.60[s_b];"
            f"[{p_idx}:a]adelay=150|150,volume=0.45[s_p];"
            f"[g_duck][vo_a][s_w][s_b][s_p]amix=inputs=5:duration=first:dropout_transition=0,"
            f"loudnorm=I=-16:TP=-1.5:LRA=11[outa]"
        )
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]", "-map", "[outa]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
            "-r", str(fps), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
        ])
    else:
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
            "-r", str(fps), "-pix_fmt", "yuv420p",
        ])
        if has_audio:
            cmd.extend(["-map", f"{audio_idx}:a:0", "-c:a", "aac", "-b:a", "192k"])
            if editor.effect_loudnorm:
                cmd.extend(["-af", "loudnorm=I=-16:TP=-1.5:LRA=11"])
        else:
            cmd.append("-an")

    cmd.extend(["-movflags", "+faststart", str(output_mp4)])

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    if on_process_start:
        on_process_start(proc)

    _, stderr = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg render failed (code {proc.returncode}): {stderr[-400:]}")

    return srt_path
