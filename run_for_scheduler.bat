@echo off
REM Yad2 Monitor - Windows Task Scheduler Runner
REM This script runs the monitor once and exits

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment
call ".venv\Scripts\activate.bat"

REM Run the scheduler runner
python scheduler_runner.py

REM Exit with the same code as Python script
exit /b %ERRORLEVEL%
