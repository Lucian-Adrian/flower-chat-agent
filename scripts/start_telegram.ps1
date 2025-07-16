# XOFlowers Telegram Bot Launcher
# Runs the Telegram bot in a new PowerShell terminal

Write-Host "🌸 XOFlowers Telegram Bot Launcher" -ForegroundColor Green
Write-Host "📱 Starting Telegram bot in new terminal..." -ForegroundColor Yellow

# Get current directory
$currentDir = Get-Location
$parentDir = Split-Path -Parent $currentDir

# Start Telegram bot in new terminal from parent directory
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$parentDir'; python xoflowers-agent/run_telegram.py"

Write-Host "✅ Telegram bot launched in separate terminal!" -ForegroundColor Green
Write-Host "💡 Check the new terminal window for bot status" -ForegroundColor Cyan
