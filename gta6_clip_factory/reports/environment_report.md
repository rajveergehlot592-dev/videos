# Environment Audit Report — GTA VI Clip Factory

**Audit Date:** 2026-11-26  
**Workspace:** `E:\videos\gta6_clip_factory` (preserving existing `E:\videos` files)

## Hardware & OS
- **Operating System:** Microsoft Windows Server 2022 Standard (`10.0.20348`)
- **CPU:** Intel(R) Core(TM) Ultra 5 245K (14 Cores / 14 Threads)
- **GPU:** Intel(R) Graphics (integrated)
- **Memory:** 15.38 GB total (~6.39 GB free at audit time)
- **Storage:**
  - `E:\`: ~196.47 GB free
  - `C:\`: ~109.69 GB free

## Runtimes & System Tools
- **Python:** `3.15.0` (isolated virtual environment created at `E:\videos\gta6_clip_factory\.venv`)
- **Node.js / npm:** `v24.21.0` / `npm 11.19.0`
- **Git:** `2.47.1.windows.1`
- **FFmpeg (System PATH):** `6.1.1-essentials` at `C:\Users\Admin\AppData\Roaming\npm\ffmpeg.exe` (`ffprobe.exe` absent on system PATH)
- **FFmpeg / ffprobe (Isolated `.venv`):** `static-ffmpeg 3.0` provides FFmpeg `8.0` (`ffmpeg.EXE` and `ffprobe.EXE`) inside `.venv\Lib\site-packages\static_ffmpeg\bin\win32\`. Backend also includes an automatic `ffmpeg -i` fallback if `ffprobe` is ever unavailable.
