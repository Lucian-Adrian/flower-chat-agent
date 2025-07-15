#!/usr/bin/env python3
"""
XOFlowers Bot System - Quick Launcher
Main entry point for running the XOFlowers chatbot system
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main launcher function"""
    print("🌸 XOFlowers Bot System - Quick Launcher")
    print("=" * 50)
    print()
    print("Choose how to run the system:")
    print("1. Run Telegram bot only")
    print("2. Run Instagram bot only")
    print("3. Run both bots")
    print("4. Run tests")
    print("5. Open setup guide")
    print("6. Exit")
    print()
    
    choice = input("Enter your choice (1-6): ").strip()
    
    if choice == "1":
        print("🚀 Starting Telegram bot...")
        subprocess.run([sys.executable, "run_telegram.py"])
    elif choice == "2":
        print("🚀 Starting Instagram bot...")
        subprocess.run([sys.executable, "run_instagram.py"])
    elif choice == "3":
        print("🚀 Starting both bots...")
        subprocess.run([sys.executable, "run_both.py"])
    elif choice == "4":
        print("🧪 Running tests...")
        subprocess.run([sys.executable, "run_tests.py"])
    elif choice == "5":
        print("📖 Opening setup guide...")
        setup_guide = Path("../docs/BOT_SETUP_GUIDE.md")
        if setup_guide.exists():
            print(f"Setup guide: {setup_guide.absolute()}")
        else:
            print("Setup guide not found!")
    elif choice == "6":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice. Please try again.")
        main()

if __name__ == "__main__":
    main()
