#!/usr/bin/env python3
"""
Clean Up Unused Files
=====================

This script removes all files that are not part of the working system
to keep only the essential files for the XOFlowers bot.
"""

import os
import shutil
from pathlib import Path

def cleanup_unused_files():
    """Remove unused files while keeping the working system"""
    
    # Files to keep (working system)
    keep_files = {
        # Core system files
        "launch_bot.py",
        "launch_safe_telegram_bot.py", 
        "LAUNCH_GUIDE.md",
        "requirements.txt",
        ".env",
        ".env.example", 
        ".env.production",
        "README.md",
        "docs/architecture.md",
        "tests.md",
        "PRODUCT_ENHANCEMENTS_GUIDE.md",
        
        # Working Python files
        "src/__init__.py",
        "src/api/__init__.py",
        "src/api/telegram_app.py",
        "src/intelligence/__init__.py", 
        "src/intelligence/ai_engine.py",
        "src/intelligence/security_ai.py",
        "src/intelligence/gemini_chat_manager.py",
        "src/intelligence/context_manager.py",
        "src/intelligence/response_generator.py",
        "src/intelligence/business_info_integrator.py",
        "src/data/chromadb_client.py",
        "src/data/faq_manager.py", 
        "src/data/redis_client.py",
        "src/utils/system_definitions.py",
        "src/utils/utils.py",
        
        # Essential data
        "src/database/products.csv",
        
        # Keep a few useful test files
        "test_enhanced_products.py",
        "test_enhanced_ai_engine.py",
        "test_bot_launch_readiness.py"
    }
    
    # Directories to keep
    keep_dirs = {
        "src",
        "src/api", 
        "src/intelligence",
        "src/data",
        "src/utils", 
        "src/database",
        "docs",
        "logs",
        "chroma_db_flowers",
        ".git",
        ".venv"
    }
    
    # Files to remove
    remove_files = [
        # Debug and analysis files
        "analyze_chromadb.py",
        "analyze_usage.py",
        "compare_chromadb_calls.py", 
        "debug_chromadb.py",
        "debug_chromadb_search.py",
        "fix_unicode_logging.py",
        "launch_enhanced_telegram_bot.py",
        
        # Unused API files
        "src/api/instagram_app.py",
        "src/api/instagram_integration.py", 
        "src/api/main.py",
        "src/api/telegram_integration.py",
        
        # Unused config
        "src/config/environment.py",
        
        # Unused database files
        "src/database/__init__.py",
        "src/database/manager.py",
        "src/database/simplified_search.py",
        "src/database/vector_search.py",
        
        # Unused helpers
        "src/helpers/__init__.py",
        "src/helpers/debug_manager.py",
        "src/helpers/llm_client.py", 
        "src/helpers/monitoring.py",
        "src/helpers/system_definitions.py",
        "src/helpers/utils.py",
        
        # Unused intelligence files
        "src/intelligence/action_handler.py",
        "src/intelligence/conversation_context.py",
        "src/intelligence/intent_classifier.py",
        "src/intelligence/product_recommender.py",
        "src/intelligence/product_search.py", 
        "src/intelligence/prompts.py",
        
        # Unused security files
        "src/security/__init__.py",
        "src/security/filters.py",
        
        # Most test files (keep only essential ones)
        "test_ai_engine_path.py",
        "test_ai_quick.py", 
        "test_bypass_security.py",
        "test_enhanced_gemini_chromadb.py",
        "test_enhanced_integration.py", 
        "test_gemini_analysis.py",
        "test_rest_to_python.py",
        "test_simple_components.py",
        "test_telegram_bot_integration.py"
    ]
    
    # Directories to remove entirely
    remove_dirs = [
        "src/config",
        "src/helpers", 
        "src/security",
        "tests",  # Old tests directory
        "test_db",
        "debug_logs",
        ".pytest_cache",
        "__pycache__"
    ]
    
    print("🧹 Cleaning up unused files...")
    
    removed_files = 0
    removed_dirs = 0
    
    # Remove specific files
    for file_path in remove_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"❌ Removed file: {file_path}")
                removed_files += 1
            except Exception as e:
                print(f"⚠️  Error removing {file_path}: {e}")
    
    # Remove directories
    for dir_path in remove_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"❌ Removed directory: {dir_path}")
                removed_dirs += 1
            except Exception as e:
                print(f"⚠️  Error removing {dir_path}: {e}")
    
    # Remove __pycache__ directories recursively
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                    print(f"❌ Removed cache: {pycache_path}")
                    removed_dirs += 1
                except Exception as e:
                    print(f"⚠️  Error removing {pycache_path}: {e}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"📊 Removed {removed_files} files and {removed_dirs} directories")
    
    print(f"\n🌸 Core system files preserved:")
    for file_path in sorted(keep_files):
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
    
    print(f"\n🚀 System is now clean and ready to launch!")
    print(f"   Run: python launch_bot.py")

if __name__ == "__main__":
    print("🌸 XOFlowers Bot - File Cleanup")
    print("=" * 40)
    
    # Change to the script directory
    os.chdir(Path(__file__).parent)
    
    # Ask for confirmation
    response = input("❓ Do you want to clean up unused files? (y/N): ")
    if response.lower() in ['y', 'yes']:
        cleanup_unused_files()
    else:
        print("👍 Cleanup cancelled. Files unchanged.")
