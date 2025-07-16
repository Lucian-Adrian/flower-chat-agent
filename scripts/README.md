# Scripts Folder

This folder contains utility scripts for the XOFlowers Bot System.

## Files:

- **`launcher.bat`** - Windows batch launcher with interactive menu
- **`start_all.ps1`** - PowerShell script to start both bots + ngrok
- **`start_telegram.ps1`** - PowerShell script to start Telegram bot only
- **`start_instagram.ps1`** - PowerShell script to start Instagram bot only
- **`run_tests.py`** - Python script to run all tests

## Usage:

### Windows (PowerShell):
```powershell
.\scripts\start_all.ps1        # Start both bots
.\scripts\start_telegram.ps1   # Start Telegram bot only
.\scripts\start_instagram.ps1  # Start Instagram bot only
```

### Windows (Batch):
```cmd
.\scripts\launcher.bat         # Interactive menu
```

### Python:
```bash
python scripts/run_tests.py   # Run all tests
```

## Quick Access:

For easier access, use the root `launcher.py`:
```bash
python launcher.py
```
