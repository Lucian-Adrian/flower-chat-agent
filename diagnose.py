#!/usr/bin/env python3
"""
XOFlowers Bot Diagnostic Tool
=============================

Quick diagnostic to identify configuration issues
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_environment():
    """Check environment configuration"""
    print("🔍 XOFlowers Bot Diagnostic")
    print("=" * 40)
    
    # Load environment
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv()
        print("✅ .env file found")
    else:
        print("❌ .env file missing!")
        print("   Create a .env file with your API keys")
        return False
    
    # Check required variables
    checks = {
        "TELEGRAM_BOT_TOKEN": "Telegram Bot",
        "GEMINI_API_KEY": "Gemini AI", 
        "OPENAI_API_KEY": "OpenAI (optional)"
    }
    
    all_good = True
    for var, desc in checks.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {desc}: {'*' * 10}{value[-4:]}")
        else:
            if var == "OPENAI_API_KEY":
                print(f"⚠️  {desc}: Missing (optional)")
            else:
                print(f"❌ {desc}: Missing!")
                all_good = False
    
    # Check ChromaDB
    products_file = Path("src/database/products.csv")
    if products_file.exists():
        print(f"✅ Products database: {products_file} found")
    else:
        print(f"❌ Products database missing: {products_file}")
        all_good = False
    
    # Check main files
    main_files = [
        "src/api/telegram_app.py",
        "src/intelligence/ai_engine.py", 
        "src/data/chromadb_client.py"
    ]
    
    for file_path in main_files:
        if Path(file_path).exists():
            print(f"✅ Core file: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            all_good = False
    
    print("\n" + "=" * 40)
    
    if all_good:
        print("🎉 All checks passed! Bot should work properly.")
        print("🚀 Run: python launch_bot.py")
    else:
        print("⚠️  Issues found! Please fix them before launching.")
        print("📖 See LAUNCH_GUIDE.md for help")
    
    return all_good

if __name__ == "__main__":
    check_environment()
