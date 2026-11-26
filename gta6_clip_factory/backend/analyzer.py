import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import numpy as np

from .config import get_binaries, load_settings
from .media_probe import generate_thumbnail
from .models import CandidateClip, EditorConfig, CaptionSegment, SignalBreakdown


def _extract_audio_signal(filepath: str, duration: float, has_audio: bool, bin_sec: float = 0.5) -> np.ndarray:
    num_bins = max(1, int(np.ceil(duration / bin_sec)))
    if not has_audio or duration <= 0:
        return np.zeros(num_bins, dtype=np.float32)

    ffmpeg_bin = get_binaries().get("ffmpeg")
    if not ffmpeg_bin:
        return np.zeros(num_bins, dtype=np.float32)

    sr = 16000
    cmd = [
        ffmpeg_bin, "-hide_banner", "-loglevel", "error",
        "-i", filepath,
        "-vn", "-ac", "1", "-ar", str(sr),
        "-f", "f32le", "pipe:1",
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0 or not res.stdout:
        return np.zeros(num_bins, dtype=np.float32)

    pcm = np.frombuffer(res.stdout, dtype=np.float32)
    if pcm.size == 0:
        return np.zeros(num_bins, dtype=np.float32)

    samples_per_bin = int(sr * bin_sec)
    scores = np.zeros(num_bins, dtype=np.float32)
    for i in range(num_bins):
        chunk = pcm[i * samples_per_bin : (i + 1) * samples_per_bin]
        if chunk.size > 0:
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            scores[i] = rms

    # Baseline-relative prominence (robust z-score using median/MAD)
    med = float(np.median(scores))
    mad = float(np.median(np.abs(scores - med))) + 1e-6
    prom = np.clip((scores - med) / (1.4826 * mad * 3.0), 0.0, 1.0)
    return prom.astype(np.float32)


def _extract_motion_signal(filepath: str, duration: float, bin_sec: float = 0.5) -> np.ndarray:
    num_bins = max(1, int(np.ceil(duration / bin_sec)))
    ffmpeg_bin = get_binaries().get("ffmpeg")
    if not ffmpeg_bin or duration <= 0:
        return np.zeros(num_bins, dtype=np.float32)

    w, h = 160, 90
    fps = 1.0 / bin_sec  # 2 fps for 0.5s bins
    cmd = [
        ffmpeg_bin, "-hide_banner", "-loglevel", "error",
        "-i", filepath,
        "-an",
        "-vf", f"fps={fps:.2f},scale={w}:{h},format=gray",
        "-f", "rawvideo", "pipe:1",
    ]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0 or not res.stdout:
        return np.zeros(num_bins, dtype=np.float32)

    frame_bytes = w * h
    total_frames = len(res.stdout) // frame_bytes
    if total_frames < 2:
        return np.zeros(num_bins, dtype=np.float32)

    frames = np.frombuffer(res.stdout[: total_frames * frame_bytes], dtype=np.uint8).reshape((total_frames, frame_bytes))
    diffs = np.mean(np.abs(np.diff(frames.astype(np.float32), axis=0)), axis=1) / 255.0

    scores = np.zeros(num_bins, dtype=np.float32)
    n = min(num_bins - 1, diffs.size)
    scores[1 : 1 + n] = diffs[:n]

    p95 = float(np.percentile(scores, 95)) + 1e-6
    return np.clip(scores / p95, 0.0, 1.0).astype(np.float32)


def _extract_scene_events(filepath: str, duration: float, bin_sec: float = 0.5) -> np.ndarray:
    num_bins = max(1, int(np.ceil(duration / bin_sec)))
    ffmpeg_bin = get_binaries().get("ffmpeg")
    if not ffmpeg_bin or duration <= 0:
        return np.zeros(num_bins, dtype=np.float32)

    cmd = [
        ffmpeg_bin, "-hide_banner", "-i", filepath,
        "-an", "-vf", "select='gt(scene,0.28)',showinfo",
        "-f", "null", "-",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    scores = np.zeros(num_bins, dtype=np.float32)
    for m in re.finditer(r"pts_time:(\d+(?:\.\d+)?)", res.stderr or ""):
        t = float(m.group(1))
        idx = min(num_bins - 1, max(0, int(t / bin_sec)))
        scores[idx] = 1.0
    return scores


def _parse_srt_sidecar(filepath: str) -> List[CaptionSegment]:
    srt_path = Path(filepath).with_suffix(".srt")
    if not srt_path.exists():
        return []
    text = srt_path.read_text(encoding="utf-8", errors="replace")
    pattern = re.compile(
        r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*\r?\n(.*?)(?=\r?\n\r?\n|\Z)",
        re.S,
    )
    segs: List[CaptionSegment] = []
    for m in pattern.finditer(text):
        sh, sm, ss, sms, eh, em, es, ems, body = m.groups()
        start = int(sh) * 3600 + int(sm) * 60 + int(ss) + int(sms) / 1000.0
        end = int(eh) * 3600 + int(em) * 60 + int(es) + int(ems) / 1000.0
        clean = " ".join(line.strip() for line in body.strip().splitlines())
        if clean:
            segs.append(CaptionSegment(start=round(start, 2), end=round(end, 2), text=clean))
    return segs


def analyze_recording(
    recording: Dict[str, Any],
    min_duration: Optional[float] = None,
    max_duration: Optional[float] = None,
    pre_padding: Optional[float] = None,
    post_padding: Optional[float] = None,
    merge_gap: Optional[float] = None,
) -> Tuple[List[CandidateClip], Dict[str, Any]]:
    settings = load_settings()
    bins = get_binaries()

    min_dur = float(min_duration if min_duration is not None else settings["min_clip_duration"])
    max_dur = float(max_duration if max_duration is not None else settings["max_clip_duration"])
    pre_pad = float(pre_padding if pre_padding is not None else settings["pre_padding"])
    post_pad = float(post_padding if post_padding is not None else settings["post_padding"])
    m_gap = float(merge_gap if merge_gap is not None else settings["merge_gap"])

    filepath = recording["filepath"]
    duration = float(recording["duration"])
    has_audio = bool(recording.get("has_audio", True))
    bin_sec = 0.5

    aud_sig = _extract_audio_signal(filepath, duration, has_audio, bin_sec)
    mot_sig = _extract_motion_signal(filepath, duration, bin_sec)
    scn_sig = _extract_scene_events(filepath, duration, bin_sec)

    sidecar_captions = _parse_srt_sidecar(filepath)
    speech_sig = np.zeros_like(mot_sig)
    for seg in sidecar_captions:
        s_idx = max(0, int(seg.start / bin_sec))
        e_idx = min(len(speech_sig), int(np.ceil(seg.end / bin_sec)))
        speech_sig[s_idx:e_idx] = 0.8

    # Weight adaptation if no audio stream
    if has_audio:
        combined = 0.45 * aud_sig + 0.35 * mot_sig + 0.12 * scn_sig + 0.08 * speech_sig
    else:
        combined = 0.72 * mot_sig + 0.20 * scn_sig + 0.08 * speech_sig

    # Find top local windows
    num_bins = len(combined)
    threshold = max(0.22, float(np.percentile(combined, 72)))
    active_indices = np.where(combined >= threshold)[0]

    raw_windows: List[Tuple[float, float, float]] = []
    if len(active_indices) > 0:
        cur_start = active_indices[0] * bin_sec
        cur_end = (active_indices[0] + 1) * bin_sec
        peak_val = float(combined[active_indices[0]])
        for idx in active_indices[1:]:
            t0 = idx * bin_sec
            t1 = (idx + 1) * bin_sec
            if t0 - cur_end <= m_gap:
                cur_end = t1
                peak_val = max(peak_val, float(combined[idx]))
            else:
                raw_windows.append((cur_start, cur_end, peak_val))
                cur_start, cur_end, peak_val = t0, t1, float(combined[idx])
        raw_windows.append((cur_start, cur_end, peak_val))

    # Fallback if video is very short or uniform
    if not raw_windows and duration > 0:
        raw_windows.append((0.0, min(duration, max_dur), 0.5))

    # Pad, clamp to [min_dur, max_dur], and merge overlapping windows
    padded: List[Tuple[float, float, float]] = []
    for s, e, pk in raw_windows:
        ns = max(0.0, s - pre_pad)
        ne = min(duration, e + post_pad)
        if ne - ns < min_dur and duration >= min_dur:
            extra = (min_dur - (ne - ns)) / 2.0
            ns = max(0.0, ns - extra)
            ne = min(duration, ns + min_dur)
            if ne - ns < min_dur:
                ns = max(0.0, ne - min_dur)
        if ne - ns > max_dur:
            # Center around peak inside [s, e]
            mid = (s + e) / 2.0
            ns = max(0.0, mid - max_dur / 2.0)
            ne = min(duration, ns + max_dur)
        padded.append((round(ns, 2), round(ne, 2), pk))

    # Merge overlapping
    padded.sort(key=lambda x: x[0])
    merged: List[Tuple[float, float, float]] = []
    for s, e, pk in padded:
        if merged and s <= merged[-1][1] + 1.0:
            ps, pe, ppk = merged[-1]
            new_end = min(duration, max(pe, e))
            if new_end - ps > max_dur:
                new_end = ps + max_dur
            merged[-1] = (ps, round(new_end, 2), max(ppk, pk))
        else:
            merged.append((s, e, pk))

    # Build CandidateClip objects
    candidates: List[CandidateClip] = []
    thumbs_dir = Path(settings["thumbnails_dir"])
    for idx, (s, e, pk) in enumerate(merged, 1):
        dur = round(e - s, 2)
        if dur < 1.0:
            continue
        i0 = max(0, int(s / bin_sec))
        i1 = min(num_bins, max(i0 + 1, int(np.ceil(e / bin_sec))))
        a_sc = float(np.max(aud_sig[i0:i1])) if i1 > i0 else 0.0
        m_sc = float(np.max(mot_sig[i0:i1])) if i1 > i0 else 0.0
        sc_sc = float(np.max(scn_sig[i0:i1])) if i1 > i0 else 0.0
        sp_sc = float(np.max(speech_sig[i0:i1])) if i1 > i0 else 0.0

        heuristic = round(min(98.0, max(45.0, 45.0 + 53.0 * (0.45 * a_sc + 0.35 * m_sc + 0.12 * sc_sc + 0.08 * sp_sc))), 1)

        reasons = []
        if a_sc >= 0.45:
            reasons.append("elevated audio loudness peak")
        if m_sc >= 0.45:
            reasons.append("high visual frame-difference motion")
        if sc_sc >= 0.5:
            reasons.append("visual scene transition")
        if sp_sc > 0:
            reasons.append("local transcript activity")
        if not reasons:
            reasons.append("representative gameplay segment")

        clip_id = f"clip_{uuid.uuid4().hex[:8]}"
        thumb_path = thumbs_dir / f"{clip_id}.jpg"
        generate_thumbnail(filepath, s + dur * 0.35, str(thumb_path), width=420)

        clip_caps = [
            CaptionSegment(
                start=round(max(0.0, c.start - s), 2),
                end=round(min(dur, c.end - s), 2),
                text=c.text,
            )
            for c in sidecar_captions
            if c.end > s and c.start < e
        ]

        candidates.append(
            CandidateClip(
                id=clip_id,
                recording_id=recording["id"],
                source_filename=recording["filename"],
                start_time=s,
                end_time=e,
                duration=dur,
                heuristic_score=heuristic,
                rationale="Detected via " + ", ".join(reasons) + " (signal heuristic, not a virality guarantee).",
                signals=SignalBreakdown(
                    audio_peak=round(a_sc, 3),
                    motion_score=round(m_sc, 3),
                    scene_change=round(sc_sc, 3),
                    speech_event=round(sp_sc, 3),
                ),
                thumbnail_url=f"/api/files/thumbnails/{clip_id}.jpg" if thumb_path.exists() else None,
                editor=EditorConfig(
                    layout=settings["default_layout"],
                    fps=settings["default_fps"],
                    crf=settings["default_crf"],
                    font_name=settings["caption_font"],
                    font_size=settings["caption_size"],
                    text_color=settings["caption_color"],
                    highlight_color=settings["caption_highlight_color"],
                    safe_margin_bottom=settings["safe_margin_bottom"],
                    captions=clip_caps,
                    hook_text=f"HIGHLIGHT #{idx}",
                ),
            )
        )

    candidates.sort(key=lambda c: c.heuristic_score, reverse=True)

    notes = []
    if not has_audio:
        notes.append("Source has no audio stream; detection used motion and scene signals only.")
    if not bins.get("whisper") and not sidecar_captions:
        notes.append("Local whisper.cpp binary not detected and no .srt sidecar found; speech transcription disabled (graceful fallback active).")

    report = {
        "recording_id": recording["id"],
        "total_candidates": len(candidates),
        "signals_used": {
            "audio_peaks": has_audio,
            "motion_frame_diff": True,
            "scene_changes": True,
            "speech_transcript": bool(sidecar_captions or bins.get("whisper")),
        },
        "notices": notes,
    }
    return candidates, report
