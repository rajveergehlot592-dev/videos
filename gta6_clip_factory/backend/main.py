import csv
import json
import os
import shutil
import subprocess
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .analyzer import analyze_recording
from .config import APP_ROOT, get_binaries, get_disk_space_gb, load_settings, save_settings
from .media_probe import SUPPORTED_VIDEO_EXTS, generate_thumbnail, probe_video_file
from .metadata_gen import generate_clip_metadata
from .models import (
    AnalyzeRequest,
    BatchExportRequest,
    CandidateClip,
    EditorConfig,
    ExportJob,
    ImportPathsRequest,
    RecordingMetadata,
)
from .renderer import render_clip
from .youtube_ingest import extract_youtube_source

app = FastAPI(title="GTA VI Clip Factory API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_LOCK = threading.RLock()
_ACTIVE_PROCS: Dict[str, subprocess.Popen] = {}
_CANCELLED_JOBS: set = set()
_EXECUTOR: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    global _EXECUTOR
    if _EXECUTOR is None:
        settings = load_settings()
        _EXECUTOR = ThreadPoolExecutor(max_workers=max(1, int(settings.get("max_concurrent_exports", 2))))
    return _EXECUTOR


def _manifest_path() -> Path:
    settings = load_settings()
    p = Path(settings["projects_dir"]) / "manifest.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load_manifest() -> Dict[str, Any]:
    with _LOCK:
        mp = _manifest_path()
        if mp.exists():
            try:
                return json.loads(mp.read_text(encoding="utf-8"))
            except Exception:
                pass
        data = {"recordings": [], "candidates": [], "export_jobs": [], "analysis_reports": {}}
        mp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data


def _save_manifest(data: Dict[str, Any]) -> None:
    with _LOCK:
        mp = _manifest_path()
        mp.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _write_export_manifests(jobs: List[Dict[str, Any]], candidates: List[Dict[str, Any]]) -> None:
    settings = load_settings()
    exports_dir = Path(settings["exports_dir"])
    exports_dir.mkdir(parents=True, exist_ok=True)
    clip_map = {c["id"]: c for c in candidates}

    manifest_rows = []
    for j in jobs:
        c = clip_map.get(j["clip_id"], {})
        manifest_rows.append({
            "job_id": j["id"],
            "clip_id": j["clip_id"],
            "source_filename": c.get("source_filename", ""),
            "start_time": c.get("start_time", 0.0),
            "end_time": c.get("end_time", 0.0),
            "duration": c.get("duration", 0.0),
            "layout": c.get("editor", {}).get("layout", ""),
            "output_filename": j["output_filename"],
            "status": j["status"],
            "resolution_verified": j.get("resolution_verified", ""),
            "duration_verified": j.get("duration_verified", ""),
            "has_audio_verified": j.get("has_audio_verified", ""),
        })

    (exports_dir / "export_manifest.json").write_text(json.dumps(manifest_rows, indent=2), encoding="utf-8")
    with (exports_dir / "export_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        if manifest_rows:
            writer = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()))
            writer.writeheader()
            writer.writerows(manifest_rows)


@app.get("/api/system/health")
def system_health():
    settings = load_settings()
    bins = get_binaries()
    notices = []
    if not bins.get("ffprobe"):
        notices.append("ffprobe not found; using ffmpeg -i fallback for media probing.")
    if not bins.get("whisper"):
        notices.append("whisper.cpp not detected; speech transcription disabled unless .srt sidecars are provided.")
    if not bins.get("opencv") or not bins.get("scenedetect"):
        notices.append("OpenCV/PySceneDetect not installed; using native FFmpeg+NumPy motion and scene detection.")

    return {
        "status": "ok" if bins.get("ffmpeg") else "degraded",
        "local_only": True,
        "binaries": bins,
        "free_disk_gb": {
            "input": get_disk_space_gb(settings["input_dir"]),
            "exports": get_disk_space_gb(settings["exports_dir"]),
        },
        "notices": notices,
        "rights_notice": (
            "GTA VI Clip Factory processes local user-selected recordings only. Copyrighted game footage and in-game "
            "music may be subject to publisher rules, platform claims, and monetization restrictions."
        ),
    }


@app.get("/api/settings")
def get_settings():
    return load_settings()


@app.put("/api/settings")
def update_settings(payload: Dict[str, Any] = Body(...)):
    return save_settings(payload)


@app.get("/api/recordings")
def list_recordings():
    m = _load_manifest()
    return m["recordings"]


@app.post("/api/youtube/import")
def import_youtube_url(payload: Dict[str, Any] = Body(...)):
    url = (payload.get("url") or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="YouTube URL is required.")
    try:
        rec, candidates = extract_youtube_source(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract YouTube URL: {e}")

    m = _load_manifest()
    m["recordings"] = [r for r in m["recordings"] if r["id"] != rec["id"]]
    m["recordings"].insert(0, rec)
    m["candidates"] = [c for c in m["candidates"] if c["recording_id"] != rec["id"]]
    cand_dicts = [c.model_dump() for c in candidates]
    m["candidates"] = cand_dicts + m["candidates"]
    _save_manifest(m)
    return {"recording": rec, "candidates": cand_dicts}


@app.post("/api/recordings/import")
def import_local_paths(req: ImportPathsRequest):
    settings = load_settings()
    free_gb = get_disk_space_gb(settings["exports_dir"])
    if free_gb < 0.5:
        raise HTTPException(status_code=507, detail=f"Insufficient free disk space ({free_gb} GB remaining).")

    manifest = _load_manifest()
    existing_hashes = {r["file_hash"] for r in manifest["recordings"]}
    thumbs_dir = Path(settings["thumbnails_dir"])

    imported = []
    errors = []
    skipped = []

    candidate_files: List[Path] = []
    for raw in req.paths:
        p = Path(raw)
        if not p.exists():
            errors.append({"path": raw, "error": "Path does not exist."})
            continue
        if p.is_dir():
            for child in sorted(p.iterdir()):
                if child.is_file() and child.suffix.lower() in SUPPORTED_VIDEO_EXTS:
                    candidate_files.append(child)
        elif p.is_file():
            candidate_files.append(p)

    for fp in candidate_files:
        try:
            meta = probe_video_file(str(fp))
            if meta["file_hash"] in existing_hashes:
                skipped.append({"path": str(fp), "reason": "Duplicate recording already imported."})
                continue
            rec_id = f"rec_{uuid.uuid4().hex[:8]}"
            thumb_p = thumbs_dir / f"{rec_id}.jpg"
            generate_thumbnail(meta["filepath"], min(2.0, meta["duration"] * 0.2), str(thumb_p), width=480)
            rec = RecordingMetadata(
                id=rec_id,
                thumbnail_url=f"/api/files/thumbnails/{rec_id}.jpg" if thumb_p.exists() else None,
                **meta,
            ).model_dump()
            manifest["recordings"].append(rec)
            existing_hashes.add(meta["file_hash"])
            imported.append(rec)
        except Exception as e:
            errors.append({"path": str(fp), "error": str(e)})

    _save_manifest(manifest)
    return {"imported": imported, "skipped": skipped, "errors": errors}


@app.post("/api/recordings/upload")
async def upload_recording(file: UploadFile = File(...)):
    settings = load_settings()
    input_dir = Path(settings["input_dir"])
    input_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename or "upload.mp4").name
    dest = input_dir / safe_name
    if dest.exists():
        dest = input_dir / f"{dest.stem}_{uuid.uuid4().hex[:6]}{dest.suffix}"
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)
    res = import_local_paths(ImportPathsRequest(paths=[str(dest)]))
    if res["errors"]:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=res["errors"][0]["error"])
    return res


@app.delete("/api/recordings/{recording_id}")
def delete_recording(recording_id: str):
    m = _load_manifest()
    m["recordings"] = [r for r in m["recordings"] if r["id"] != recording_id]
    m["candidates"] = [c for c in m["candidates"] if c["recording_id"] != recording_id]
    _save_manifest(m)
    return {"deleted": recording_id}


@app.post("/api/analysis/run")
def run_analysis(req: AnalyzeRequest):
    m = _load_manifest()
    rec = next((r for r in m["recordings"] if r["id"] == req.recording_id), None)
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found.")

    candidates, report = analyze_recording(
        rec,
        min_duration=req.min_duration,
        max_duration=req.max_duration,
        pre_padding=req.pre_padding,
        post_padding=req.post_padding,
        merge_gap=req.merge_gap,
    )

    cand_dicts = []
    for c in candidates:
        c.metadata = generate_clip_metadata(c)
        cand_dicts.append(c.model_dump())

    m["candidates"] = [c for c in m["candidates"] if c["recording_id"] != req.recording_id] + cand_dicts
    rec["status"] = "analyzed"
    m["analysis_reports"][req.recording_id] = report
    _save_manifest(m)
    return {"report": report, "candidates": cand_dicts}


@app.get("/api/candidates")
def list_candidates(recording_id: Optional[str] = None):
    m = _load_manifest()
    cands = m["candidates"]
    if recording_id:
        cands = [c for c in cands if c["recording_id"] == recording_id]
    return cands


@app.patch("/api/candidates/{clip_id}")
def update_candidate(clip_id: str, patch: Dict[str, Any] = Body(...)):
    m = _load_manifest()
    clip = next((c for c in m["candidates"] if c["id"] == clip_id), None)
    if not clip:
        raise HTTPException(status_code=404, detail="Candidate clip not found.")

    rec = next((r for r in m["recordings"] if r["id"] == clip["recording_id"]), None)
    max_dur = rec["duration"] if rec else 999999.0

    if "start_time" in patch:
        clip["start_time"] = round(max(0.0, min(float(patch["start_time"]), max_dur - 0.5)), 2)
    if "end_time" in patch:
        clip["end_time"] = round(max(clip["start_time"] + 0.5, min(float(patch["end_time"]), max_dur)), 2)
    clip["duration"] = round(clip["end_time"] - clip["start_time"], 2)

    if "status" in patch and patch["status"] in ("pending", "approved", "rejected"):
        clip["status"] = patch["status"]

    if "editor" in patch and isinstance(patch["editor"], dict):
        merged_editor = {**clip.get("editor", {}), **patch["editor"]}
        clip["editor"] = EditorConfig(**merged_editor).model_dump()

    if "metadata" in patch and isinstance(patch["metadata"], dict):
        clip["metadata"] = {**clip.get("metadata", {}), **patch["metadata"]}

    _save_manifest(m)
    return clip


@app.post("/api/candidates/{clip_id}/metadata")
def regenerate_metadata(clip_id: str):
    m = _load_manifest()
    clip = next((c for c in m["candidates"] if c["id"] == clip_id), None)
    if not clip:
        raise HTTPException(status_code=404, detail="Candidate clip not found.")
    meta = generate_clip_metadata(CandidateClip(**clip))
    clip["metadata"] = meta
    _save_manifest(m)
    return meta


def _execute_export_job(job_id: str, fps_override: Optional[int], crf_override: Optional[int]) -> None:
    if job_id in _CANCELLED_JOBS:
        return

    m = _load_manifest()
    job = next((j for j in m["export_jobs"] if j["id"] == job_id), None)
    if not job:
        return
    clip = next((c for c in m["candidates"] if c["id"] == job["clip_id"]), None)
    rec = next((r for r in m["recordings"] if r["id"] == job["recording_id"]), None)
    if not clip or not rec:
        job["status"] = "failed"
        job["error"] = "Source recording or clip missing."
        _save_manifest(m)
        return

    job["status"] = "running"
    job["progress"] = 15.0
    job["error"] = None
    _save_manifest(m)

    settings = load_settings()
    out_path = Path(settings["exports_dir"]) / job["output_filename"]

    def _track_proc(proc: subprocess.Popen) -> None:
        with _LOCK:
            _ACTIVE_PROCS[job_id] = proc

    try:
        src_path = rec["filepath"]
        aud_path = rec.get("audio_filepath")
        if rec.get("source_type") == "youtube" and rec.get("youtube_url"):
            try:
                fresh_rec, _ = extract_youtube_source(rec["youtube_url"], max_comments=10)
                src_path = fresh_rec["filepath"]
                aud_path = fresh_rec.get("audio_filepath")
            except Exception:
                pass

        srt_p = render_clip(
            src_path,
            CandidateClip(**clip),
            out_path,
            has_audio=bool(rec.get("has_audio", True)),
            on_process_start=_track_proc,
            fps_override=fps_override,
            crf_override=crf_override,
            audio_filepath=aud_path,
        )
        if job_id in _CANCELLED_JOBS:
            out_path.unlink(missing_ok=True)
            return

        verified = probe_video_file(str(out_path))
        m2 = _load_manifest()
        j2 = next((j for j in m2["export_jobs"] if j["id"] == job_id), None)
        if j2:
            j2["status"] = "completed"
            j2["progress"] = 100.0
            j2["output_path"] = str(out_path)
            j2["srt_path"] = str(srt_p) if srt_p else None
            j2["duration_verified"] = verified["duration"]
            j2["resolution_verified"] = f"{verified['width']}x{verified['height']}"
            j2["has_audio_verified"] = verified["has_audio"]
            j2["completed_at"] = datetime.now(timezone.utc).isoformat()
            _save_manifest(m2)
            _write_export_manifests(m2["export_jobs"], m2["candidates"])
    except Exception as e:
        if job_id in _CANCELLED_JOBS:
            return
        m2 = _load_manifest()
        j2 = next((j for j in m2["export_jobs"] if j["id"] == job_id), None)
        if j2:
            j2["status"] = "failed"
            j2["error"] = str(e)
            _save_manifest(m2)
            _write_export_manifests(m2["export_jobs"], m2["candidates"])
    finally:
        with _LOCK:
            _ACTIVE_PROCS.pop(job_id, None)


@app.post("/api/exports/batch")
def start_batch_export(req: BatchExportRequest):
    m = _load_manifest()
    settings = load_settings()
    if get_disk_space_gb(settings["exports_dir"]) < 0.25:
        raise HTTPException(status_code=507, detail="Insufficient disk space for export.")

    jobs_created = []
    for clip_id in req.clip_ids:
        clip = next((c for c in m["candidates"] if c["id"] == clip_id), None)
        if not clip:
            continue
        job_id = f"exp_{uuid.uuid4().hex[:8]}"
        stem = Path(clip["source_filename"]).stem[:24]
        out_name = f"{stem}_{clip_id}_{int(clip['start_time'])}s.mp4"
        job = ExportJob(
            id=job_id,
            clip_id=clip_id,
            recording_id=clip["recording_id"],
            output_filename=out_name,
            status="queued",
            created_at=datetime.now(timezone.utc).isoformat(),
        ).model_dump()
        m["export_jobs"].insert(0, job)
        jobs_created.append(job)

    _save_manifest(m)
    ex = _get_executor()
    for j in jobs_created:
        ex.submit(_execute_export_job, j["id"], req.fps, req.crf)

    return {"queued": len(jobs_created), "jobs": jobs_created}


@app.get("/api/exports")
def list_exports():
    m = _load_manifest()
    return m["export_jobs"]


@app.post("/api/exports/{job_id}/cancel")
def cancel_export(job_id: str):
    with _LOCK:
        _CANCELLED_JOBS.add(job_id)
        proc = _ACTIVE_PROCS.get(job_id)
        if proc and proc.poll() is None:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
            else:
                proc.terminate()
    m = _load_manifest()
    job = next((j for j in m["export_jobs"] if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found.")
    job["status"] = "cancelled"
    job["error"] = "Cancelled by user."
    _save_manifest(m)
    _write_export_manifests(m["export_jobs"], m["candidates"])
    return job


@app.post("/api/exports/{job_id}/retry")
def retry_export(job_id: str):
    with _LOCK:
        _CANCELLED_JOBS.discard(job_id)
    m = _load_manifest()
    job = next((j for j in m["export_jobs"] if j["id"] == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail="Export job not found.")
    job["status"] = "queued"
    job["progress"] = 0.0
    job["error"] = None
    _save_manifest(m)
    _get_executor().submit(_execute_export_job, job_id, None, None)
    return job


@app.get("/api/files/thumbnails/{filename}")
def serve_thumbnail(filename: str):
    settings = load_settings()
    p = Path(settings["thumbnails_dir"]) / Path(filename).name
    if not p.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found.")
    return FileResponse(str(p))


@app.get("/api/files/exports/{filename}")
def serve_export(filename: str):
    settings = load_settings()
    p = Path(settings["exports_dir"]) / Path(filename).name
    if not p.exists():
        raise HTTPException(status_code=404, detail="Export file not found.")
    return FileResponse(str(p), media_type="video/mp4")


@app.get("/api/files/video/{recording_id}")
def serve_recording_video(recording_id: str):
    m = _load_manifest()
    rec = next((r for r in m["recordings"] if r["id"] == recording_id), None)
    if not rec or not Path(rec["filepath"]).exists():
        raise HTTPException(status_code=404, detail="Recording file not found.")
    return FileResponse(rec["filepath"], media_type="video/mp4")


_FRONTEND_DIST = APP_ROOT / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIST), html=True), name="frontend")
