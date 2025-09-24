# Yad2 Monitor Service - PowerShell Version
# This version can prevent PC from sleeping during monitoring

Add-Type -AssemblyName System.Windows.Forms

Write-Host "🏠 Yad2 Haifa Property Monitor (Service Mode)" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Prevent system sleep
Write-Host "🔋 Enabling wake mode to prevent system sleep..." -ForegroundColor Yellow
Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;
    public class PowerState {
        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        public static extern uint SetThreadExecutionState(uint esFlags);
        public const uint ES_CONTINUOUS = 0x80000000;
        public const uint ES_SYSTEM_REQUIRED = 0x00000001;
        public const uint ES_AWAYMODE_REQUIRED = 0x00000040;
    }
"@

# Keep system awake
[PowerState]::SetThreadExecutionState([PowerState]::ES_CONTINUOUS -bor [PowerState]::ES_SYSTEM_REQUIRED -bor [PowerState]::ES_AWAYMODE_REQUIRED)

# Change to script directory
Set-Location $PSScriptRoot

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "🐍 Activating virtual environment..." -ForegroundColor Cyan
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "📦 Installing/updating dependencies..." -ForegroundColor Cyan
& python -m pip install -r requirements.txt

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create .env with your Gmail credentials" -ForegroundColor Yellow
    Write-Host "See .env.example for template" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "✅ Starting local monitoring service..." -ForegroundColor Green
Write-Host "⏰ Will check every 10 minutes" -ForegroundColor Cyan
Write-Host "🔋 System sleep prevention: ENABLED" -ForegroundColor Green
Write-Host "📝 Logs saved to: yad2_monitor.log" -ForegroundColor Cyan
Write-Host "⏹️ Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

try {
    # Run the local monitor
    & python local_monitor.py
} catch {
    Write-Host "❌ Error running monitor: $_" -ForegroundColor Red
} finally {
    # Restore normal power state
    Write-Host "🔋 Restoring normal power management..." -ForegroundColor Yellow
    [PowerState]::SetThreadExecutionState([PowerState]::ES_CONTINUOUS)
    Write-Host "Service stopped." -ForegroundColor Gray
}

Read-Host "Press Enter to exit"
