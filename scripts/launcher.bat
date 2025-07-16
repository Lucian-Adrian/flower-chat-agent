@echo off
echo 🌸 XOFlowers Bot System Launcher
echo ================================
echo.
echo Choose an option:
echo 1. Start Telegram bot only
echo 2. Start Instagram bot only  
echo 3. Start both bots (separate terminals)
echo 4. Start both bots (single terminal)
echo 5. Exit
echo.
set /p choice=Enter your choice (1-5): 

if "%choice%"=="1" goto telegram
if "%choice%"=="2" goto instagram
if "%choice%"=="3" goto both_separate
if "%choice%"=="4" goto both_single
if "%choice%"=="5" goto exit
goto invalid

:telegram
echo 📱 Starting Telegram bot...
start cmd /k "python run_telegram.py"
goto end

:instagram
echo 📸 Starting Instagram bot...
start cmd /k "python run_instagram.py"
goto end

:both_separate
echo 🚀 Starting both bots in separate terminals...
start cmd /k "python run_telegram.py"
timeout /t 2 /nobreak > nul
start cmd /k "python run_instagram.py"
timeout /t 2 /nobreak > nul
start cmd /k "..\chatbot-main\junk\ngrok.exe http 5001"
goto end

:both_single
echo 🚀 Starting both bots in single terminal...
python run_both.py
goto end

:invalid
echo ❌ Invalid choice. Please try again.
pause
goto start

:end
echo ✅ Bot(s) launched successfully!
echo 💡 Check the terminal windows for status
pause

:exit
echo 👋 Goodbye!
pause
