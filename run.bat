@echo off
REM AI Content Moderation API Startup Script for Windows

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%cd%

REM Default values
if "%HOST%"=="" set HOST=0.0.0.0
if "%PORT%"=="" set PORT=8000
if "%WORKERS%"=="" set WORKERS=1
if "%LOG_LEVEL%"=="" set LOG_LEVEL=info

echo 🚀 Starting AI Content Moderation API...
echo 📍 Host: %HOST%
echo 🔌 Port: %PORT%
echo 👥 Workers: %WORKERS%
echo 📊 Log Level: %LOG_LEVEL%

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Start the server
echo 🎯 Starting server...
uvicorn app.main:app --host %HOST% --port %PORT% --workers %WORKERS% --log-level %LOG_LEVEL% --reload

pause
