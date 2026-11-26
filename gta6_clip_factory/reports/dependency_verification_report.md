# Dependency Verification Report — GTA VI Clip Factory

**Verification Date:** 2026-11-26  
**Python Environment:** `E:\videos\gta6_clip_factory\.venv` (Python 3.15.0)

## Verified Core Dependencies (Installed & Tested)
| Package | Version | Purpose | Status |
|---|---|---|---|
| `fastapi` | `0.165.0` | Local REST API backend | Verified |
| `uvicorn[standard]` | `0.54.0` | ASGI server | Verified |
| `pydantic` | `2.14.4` | Request/response & manifest schemas | Verified |
| `python-multipart` | `0.0.34` | Local file/folder upload handling | Verified |
| `numpy` | `2.5.5` | Audio PCM & frame-difference motion math | Verified |
| `scipy` | `1.18.1` | Signal processing & peak detection | Verified |
| `pillow` | `13.0.0` | Thumbnail & preview inspection | Verified |
| `static-ffmpeg` | `3.0` | Bundled `ffmpeg` + `ffprobe` v8.0 binaries | Verified |
| `pytest` | `9.2.0` | Automated test runner | Verified |
| `httpx` | `0.28.1` | FastAPI TestClient transport | Verified |

## Optional Dependencies & Graceful Fallbacks
- **`opencv-python` / `scenedetect`:** Not required in core `.venv` (Python 3.15 prebuilt wheel availability lags). Visual motion & scene change detection are implemented natively via FFmpeg raw gray pipe (`scale=160:90,format=gray,fps=2` + `scdet` scene filter) and NumPy/SciPy, with zero loss of core functionality.
- **`whisper.cpp` / `faster-whisper`:** Not installed (`av` lacks `cp315` wheel without MSVC build tools). The backend checks for local `whisper-cli.exe` / `whisper.cpp` or `.srt` sidecar files at runtime; when unavailable, it discloses reduced speech-transcription functionality in `/api/system/health` and the UI while continuing full audio-peak, motion, and scene analysis.

## Frontend Dependencies
- React 18 + Vite + JavaScript (installed locally in `frontend/node_modules`, zero external runtime CDNs).
