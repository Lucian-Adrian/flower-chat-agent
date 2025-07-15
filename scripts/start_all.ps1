# XOFlowers Dual Bot Launcher
# Runs both Telegram and Instagram bots in separate terminals

Write-Host "🌸 XOFlowers Dual Bot System Launcher" -ForegroundColor Green
Write-Host "🚀 Starting both Telegram and Instagram bots..." -ForegroundColor Yellow

# Get current directory
$currentDir = Get-Location

# Start Telegram bot in new terminal
Write-Host "📱 Launching Telegram bot..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentDir'; python run_telegram.py"

# Wait a moment
Start-Sleep -Seconds 2

# Start Instagram bot in new terminal
Write-Host "📸 Launching Instagram bot..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentDir'; python run_instagram.py"

# Wait a moment
Start-Sleep -Seconds 2

# Start ngrok in new terminal
Write-Host "🌐 Launching ngrok tunnel..." -ForegroundColor Cyan
$ngrokPath = "..\chatbot-main\junk\ngrok.exe"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentDir'; & '$ngrokPath' http 5001"

Write-Host ""
Write-Host "✅ All services launched successfully!" -ForegroundColor Green
Write-Host "📱 Telegram bot: Running in polling mode" -ForegroundColor Blue
Write-Host "📸 Instagram bot: Running on port 5001" -ForegroundColor Magenta
Write-Host "🌐 ngrok tunnel: Forwarding to Instagram webhook" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Check each terminal window for service status" -ForegroundColor Yellow
Write-Host "🔗 Configure Instagram webhook with ngrok URL" -ForegroundColor Yellow
