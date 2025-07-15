# XOFlowers Instagram Bot Launcher
# Runs the Instagram bot in a new PowerShell terminal

Write-Host "🌸 XOFlowers Instagram Bot Launcher" -ForegroundColor Green
Write-Host "📸 Starting Instagram bot in new terminal..." -ForegroundColor Yellow

# Get current directory
$currentDir = Get-Location
$parentDir = Split-Path -Parent $currentDir

# Start Instagram bot in new terminal from parent directory
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$parentDir'; python xoflowers-agent/run_instagram.py"

Write-Host "✅ Instagram bot launched in separate terminal!" -ForegroundColor Green
Write-Host "💡 Check the new terminal window for bot status" -ForegroundColor Cyan
Write-Host "🔗 Remember to start ngrok for webhook!" -ForegroundColor Yellow
