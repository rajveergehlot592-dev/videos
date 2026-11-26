@echo off
setlocal EnableExtensions
pushd "%~dp0" || exit /b 1

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv not found. Please run install.bat first.
    pause
    exit /b 1
)

if not exist "logs" mkdir logs

netstat -ano | findstr ":8000 " | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [INFO] Port 8000 is already listening. Opening http://127.0.0.1:8000 ...
    start "" "http://127.0.0.1:8000"
    popd
    exit /b 0
)

echo [INFO] Starting GTA VI Clip Factory backend on http://127.0.0.1:8000 ...
start "GTA VI Clip Factory Server" /min cmd /c ""%~dp0.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > "%~dp0logs\server.log" 2>&1"

echo [INFO] Waiting for server readiness...
powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 25;$i++){ try { $r=Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/system/health' -UseBasicParsing -TimeoutSec 2; if($r.StatusCode -eq 200){ $ok=$true; break } } catch {}; Start-Sleep -Milliseconds 500 }; if(-not $ok){ Write-Host '[ERROR] Server did not respond in time. Check logs\server.log'; exit 1 }"
if errorlevel 1 (
    popd
    pause
    exit /b 1
)

echo [INFO] Launching browser at http://127.0.0.1:8000 ...
start "" "http://127.0.0.1:8000"
popd
exit /b 0
