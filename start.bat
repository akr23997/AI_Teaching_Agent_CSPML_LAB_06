@echo off
setlocal

cd /d "%~dp0"

echo ==========================================
echo   AI Teaching Agent - Power Electronics
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -3.12 -m venv .venv
    if errorlevel 1 (
        echo.
        echo Could not create a Python 3.12 environment.
        echo Install Python 3.11 or 3.12 and run this file again.
        pause
        exit /b 1
    )
)

echo Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo.
echo Starting server...
echo Open http://127.0.0.1:8000 in your browser.
echo Keep this window open while using the application.
echo.

".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

pause
