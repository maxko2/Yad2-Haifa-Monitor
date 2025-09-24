# Setup Windows Task Scheduler for Yad2 Monitor
# Run this script as Administrator to create the scheduled task

param(
    [int]$IntervalMinutes = 10
)

Write-Host "🏠 Yad2 Haifa Monitor - Task Scheduler Setup" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "❌ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BatchFile = Join-Path $ScriptDir "run_for_scheduler.bat"

# Check if batch file exists
if (-not (Test-Path $BatchFile)) {
    Write-Host "❌ Batch file not found: $BatchFile" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Task details
$TaskName = "Yad2 Haifa Property Monitor"
$TaskDescription = "Monitors Yad2 for new rental properties in Haifa every $IntervalMinutes minutes"

Write-Host "📝 Creating scheduled task..." -ForegroundColor Cyan
Write-Host "   Name: $TaskName" -ForegroundColor Gray
Write-Host "   Interval: Every $IntervalMinutes minutes" -ForegroundColor Gray
Write-Host "   Script: $BatchFile" -ForegroundColor Gray
Write-Host ""

try {
    # Remove existing task if it exists
    $existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "🗑️ Removing existing task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }

    # Create the action
    $Action = New-ScheduledTaskAction -Execute $BatchFile -WorkingDirectory $ScriptDir

    # Create the trigger (every X minutes)
    $Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) -RepetitionDuration ([TimeSpan]::MaxValue)

    # Create the settings
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

    # Create the principal (run as current user)
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

    # Register the task
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description $TaskDescription

    Write-Host "✅ Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎯 Task Details:" -ForegroundColor Cyan
    Write-Host "   • Runs every $IntervalMinutes minutes" -ForegroundColor White
    Write-Host "   • Starts even if on battery power" -ForegroundColor White
    Write-Host "   • Runs only when network is available" -ForegroundColor White
    Write-Host "   • Logs saved to: yad2_scheduler.log" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Management:" -ForegroundColor Cyan
    Write-Host "   • Open Task Scheduler: taskschd.msc" -ForegroundColor White
    Write-Host "   • Find task: Task Scheduler Library > '$TaskName'" -ForegroundColor White
    Write-Host "   • Right-click task for options (Run, Disable, Delete)" -ForegroundColor White
    Write-Host ""
    
    # Ask if user wants to run the task immediately
    $runNow = Read-Host "Would you like to run the task once now to test it? (y/n)"
    if ($runNow -eq "y" -or $runNow -eq "Y") {
        Write-Host "▶️ Running task now..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "✅ Task started! Check yad2_scheduler.log for results." -ForegroundColor Green
    }

} catch {
    Write-Host "❌ Error creating scheduled task: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "📋 Quick Commands:" -ForegroundColor Cyan
Write-Host "   • View task: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "   • Run task: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "   • Stop task: Stop-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "   • Delete task: Unregister-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray

Read-Host "Press Enter to exit"
