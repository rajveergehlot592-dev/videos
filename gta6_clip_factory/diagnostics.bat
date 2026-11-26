@echo off
setlocal EnableExtensions
pushd "%~dp0" || exit /b 1

if not exist "logs" mkdir logs
for /f %%T in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TS=%%T"
set "REPORT=logs\diagnostics_%TS%.txt"

call :run_checks > "%REPORT%" 2>&1
type "%REPORT%"
echo.
echo [INFO] Diagnostics report saved to: "%CD%\%REPORT%"
popd
exit /b 0

:run_checks
echo ====================================================================
echo  GTA VI CLIP FACTORY - Windows Diagnostics (%DATE% %TIME%)
echo ====================================================================
echo Workspace: "%CD%"
echo.
echo [1] OS ^& Disk Space
ver
powershell -NoProfile -Command "$d=(Get-Item '.').PSDrive.Name; $f=(Get-PSDrive $d).Free/1GB; Write-Host ('Drive ' + $d + ': Free Space = ' + [math]::Round($f,2) + ' GB')"
echo.
echo [2] Python ^& Isolated .venv
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import sys; print('venv Python:', sys.version)"
    ".venv\Scripts\python.exe" -c "import importlib.util; mods=['fastapi','uvicorn','pydantic','numpy','scipy','PIL','pytest','httpx','static_ffmpeg']; [print('  OK:', m) if importlib.util.find_spec(m) else print('  MISSING:', m) for m in mods]"
) else (
    echo [FAIL] .venv\Scripts\python.exe missing ^(run install.bat^)
)
echo.
echo [3] Node.js ^& Frontend
where node >nul 2>&1 && (node -v) || echo [FAIL] node missing
if exist "frontend\node_modules" (echo   OK: frontend\node_modules) else (echo   MISSING: frontend\node_modules)
if exist "frontend\dist\index.html" (echo   OK: frontend\dist\index.html) else (echo   WARN: frontend\dist\index.html not built)
echo.
echo [4] FFmpeg ^& FFprobe
".venv\Scripts\python.exe" -c "from backend.config import get_binaries; import subprocess; b=get_binaries(); print('  ffmpeg:', b['ffmpeg']); print('  ffprobe:', b['ffprobe']); r=subprocess.run([b['ffmpeg'],'-hide_banner','-loglevel','error','-f','lavfi','-i','testsrc2=s=640x360:d=0.2','-f','lavfi','-i','sine=f=440:d=0.2','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-c:a','aac','-f','null','-']); print('  Smoke encode exit:', r.returncode)"
echo.
echo [5] Port 8000 Check
netstat -ano | findstr ":8000 " || echo   Port 8000 is free.
echo ====================================================================
goto :eof
