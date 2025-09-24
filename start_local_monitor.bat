@echo off
echo 🏠 Starting Yad2 Haifa Property Monitor (Local)
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/update dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️ WARNING: .env file not found!
    echo Please create .env with your Gmail credentials
    echo See .env.example for template
    pause
)

echo.
echo ✅ Starting local monitoring...
echo ⏰ Will check every 10 minutes
echo 📝 Logs saved to yad2_monitor.log
echo ⏹️ Press Ctrl+C to stop
echo.

REM Run the local monitor
python local_monitor.py

pause
