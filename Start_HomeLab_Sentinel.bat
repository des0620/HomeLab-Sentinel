
@echo off
setlocal
cd /d "%~dp0"

title HomeLab Sentinel Launcher

echo ========================================
echo       HomeLab Sentinel
echo ========================================
echo.

where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON=py -3"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo Python 3 is required.
        echo Install Python from https://www.python.org/
        pause
        exit /b 1
    )
    set "PYTHON=python"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto error
)

echo Installing project dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo Starting HomeLab Sentinel...
echo Dashboard: http://127.0.0.1:5000
echo.
echo Keep this window open while using the app.
echo Press Ctrl+C to stop the server.
echo.

start "" "http://127.0.0.1:5000"
".venv\Scripts\python.exe" app.py

if errorlevel 1 goto error
exit /b 0

:error
echo.
echo HomeLab Sentinel could not start.
pause
exit /b 1
