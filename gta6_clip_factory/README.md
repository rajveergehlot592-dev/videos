# GTA VI Clip Factory

A **100% local-first** Windows desktop-style web studio (React + FastAPI + FFmpeg) for turning locally stored gameplay recordings into vertical `1080×1920` (9:16) YouTube Shorts, Instagram Reels, and TikTok videos.

## Features
- **Dashboard & Import:** Import local recordings or folders without modifying originals; automatic duplicate detection, stream probing, and free disk space checks.
- **Multi-Signal Highlight Detection:** Uniform `0.5s` analysis combining audio loudness prominence (RMS + MAD), frame-difference motion, visual scene transitions, and optional local `.srt` / `whisper.cpp` transcripts.
- **Clip Reviewer & Editor:** HTML5 video playback, start/end trimming, approval/rejection, live 9:16 preview, 3 vertical layouts (`blurred_bg`, `dynamic_crop`, `manual_crop`), customizable hook/caption overlays, and toggleable effects (color boost, progress bar, EBU R128 `loudnorm`).
- **Batch Export & Metadata:** H.264/AAC MP4 (`-movflags +faststart`, `setsar=1`) with progress polling, cancellation, retry, `.srt` export, CSV/JSON manifests, and original title/caption/hashtag suggestions.

## Quick Start (Windows)
1. Run `install.bat` (creates `.venv`, installs `requirements.txt`, builds `frontend/dist`).
2. Run `diagnostics.bat` to verify Python, Node, FFmpeg/ffprobe, and port `8000`.
3. Run `start.bat` to launch the server and open `http://127.0.0.1:8000` in your browser.

## Rights & Safety Notice
GTA VI Clip Factory processes local user-selected files only and never uploads recordings externally or auto-publishes to social platforms. Copyrighted game footage and in-game music may be subject to publisher rules, platform claims, and monetization restrictions.
