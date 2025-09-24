@echo off
echo 🚀 Smart Yad2 Monitor - Scheduled Task Setup

echo.
echo Choose your monitoring method:
echo.
echo 1. Continuous Smart Mode (randomized 7-13 min intervals)
echo 2. Windows Task Scheduler (runs every 10 minutes via Windows)
echo 3. Test the system first
echo.

set /p choice="Enter choice (1-3): "

if "%choice%"=="1" goto continuous
if "%choice%"=="2" goto scheduler
if "%choice%"=="3" goto test
echo Invalid choice
pause
exit

:continuous
echo.
echo 🔄 Running in continuous smart mode...
echo This will run with randomized intervals to avoid detection.
echo Press Ctrl+C to stop.
echo.
python smart_yad2_main.py
pause
exit

:scheduler
echo.
echo ⏰ Setting up Windows Task Scheduler...
echo This will create a task to run every 10 minutes.
echo.

set currentDir=%cd%
set taskName=Yad2SmartMonitor

REM Create the task
schtasks /create /tn "%taskName%" /tr "python \"%currentDir%\smart_yad2_main.py\" --once" /sc minute /mo 10 /f

if errorlevel 1 (
    echo ❌ Failed to create scheduled task. Try running as Administrator.
    pause
    exit
)

echo ✅ Task created successfully!
echo.
echo Task details:
echo • Name: %taskName%
echo • Runs: Every 10 minutes
echo • Command: python smart_yad2_main.py --once
echo.
echo To manage the task:
echo • Start: schtasks /run /tn "%taskName%"
echo • Stop:  schtasks /end /tn "%taskName%"
echo • Delete: schtasks /delete /tn "%taskName%" /f
echo.

set /p startNow="Start the task now? (y/n): "
if /i "%startNow%"=="y" (
    schtasks /run /tn "%taskName%"
    echo ✅ Task started!
)

echo.
echo 📊 Monitor the task with:
echo • Task Scheduler GUI: taskschd.msc
echo • Logs: Check api_monitor.log
echo • Statistics: python smart_yad2_main.py --stats
echo.
pause
exit

:test
echo.
echo 🧪 Testing Smart Yad2 Monitor system...
echo.
python smart_yad2_main.py --test
echo.
echo 📊 Showing statistics...
python smart_yad2_main.py --stats
echo.
pause
exit
