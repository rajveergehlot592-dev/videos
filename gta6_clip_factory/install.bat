@echo off
setlocal EnableExtensions
pushd "%~dp0" || exit /b 1

echo ====================================================================
echo  GTA VI CLIP FACTORY - Installer (Isolated .venv + Frontend Build)
echo ====================================================================

where python >nul 2>&1 || (
    echo [ERROR] Python not found on PATH. Install Python 3.11+ and retry.
    exit /b 1
)
where node >nul 2>&1 || (
    echo [ERROR] Node.js not found on PATH. Install Node.js 18+ and retry.
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/4] Creating isolated virtual environment .venv...
    python -m venv .venv || exit /b 1
) else (
    echo [1/4] Reusing existing .venv...
)

echo [2/4] Installing pinned Python dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
".venv\Scripts\python.exe" -m pip install -r requirements.txt || exit /b 1

echo [3/4] Installing and building React frontend...
pushd frontend
call npm install || (popd & popd & exit /b 1)
call npm run build || (popd & popd & exit /b 1)
popd

echo [4/4] Verifying FFmpeg/ffprobe availability...
".venv\Scripts\python.exe" -c "from backend.config import get_binaries; print(get_binaries())"

echo.
echo [SUCCESS] Installation complete! Run start.bat to launch GTA VI Clip Factory.
popd
exit /b 0
