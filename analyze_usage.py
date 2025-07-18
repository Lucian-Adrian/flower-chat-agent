#!/usr/bin/env python3
"""
File Usage Analysis for XOFlowers Bot
=====================================

This script analyzes which files are actually used by the working system
and identifies files that can be safely deleted.
"""

import os
from pathlib import Path
import ast
import sys

def find_imports_in_file(file_path):
    """Find all imports in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        imports = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        
        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return set()

def analyze_system_usage():
    """Analyze which files are used by the working system"""
    
    # Start from the main entry points
    entry_points = [
        "src/api/telegram_app.py",
        "launch_bot.py",
        "launch_safe_telegram_bot.py"
    ]
    
    all_python_files = set()
    used_files = set()
    
    # Find all Python files
    src_path = Path("src")
    if src_path.exists():
        for py_file in src_path.rglob("*.py"):
            rel_path = str(py_file).replace("\\", "/")
            all_python_files.add(rel_path)
    
    # Add root level Python files
    for py_file in Path(".").glob("*.py"):
        if py_file.name not in ["analyze_usage.py"]:  # Don't include this analysis script
            all_python_files.add(str(py_file))
    
    def trace_imports(file_path, visited=None):
        """Recursively trace imports to find used files"""
        if visited is None:
            visited = set()
        
        if file_path in visited:
            return
        
        visited.add(file_path)
        used_files.add(file_path)
        
        # Convert relative path to check if file exists
        if os.path.exists(file_path):
            imports = find_imports_in_file(file_path)
            
            for imp in imports:
                # Convert import to file path
                if imp.startswith("src."):
                    # Internal import
                    parts = imp.split(".")
                    potential_file = "/".join(parts) + ".py"
                    if potential_file in all_python_files:
                        trace_imports(potential_file, visited)
                    
                    # Also check for __init__.py in package
                    if len(parts) > 1:
                        package_init = "/".join(parts[:-1]) + "/__init__.py"
                        if package_init in all_python_files:
                            trace_imports(package_init, visited)
    
    # Trace from entry points
    for entry in entry_points:
        if os.path.exists(entry):
            print(f"Tracing from: {entry}")
            trace_imports(entry)
    
    # Core files we know are used
    core_files = [
        "src/intelligence/ai_engine.py",
        "src/data/chromadb_client.py", 
        "src/utils/system_definitions.py",
        "src/utils/utils.py",
        "src/intelligence/security_ai.py",
        "src/intelligence/gemini_chat_manager.py",
        "src/intelligence/context_manager.py",
        "src/intelligence/response_generator.py",
        "src/data/faq_manager.py",
        "src/intelligence/business_info_integrator.py",
        "src/data/redis_client.py",
        "src/database/products.csv"  # Data file
    ]
    
    for core_file in core_files:
        if os.path.exists(core_file):
            used_files.add(core_file)
    
    # Essential directories
    essential_dirs = [
        "src/api",
        "src/intelligence", 
        "src/data",
        "src/utils",
        "src/database",
        "src/config"
    ]
    
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"Total Python files found: {len(all_python_files)}")
    print(f"Used files: {len(used_files)}")
    print(f"Potentially unused files: {len(all_python_files - used_files)}")
    
    print(f"\n✅ CORE USED FILES:")
    for f in sorted(used_files):
        print(f"  {f}")
    
    unused = all_python_files - used_files
    if unused:
        print(f"\n❌ POTENTIALLY UNUSED FILES:")
        for f in sorted(unused):
            print(f"  {f}")
    
    # Check for test files and other categories
    test_files = [f for f in all_python_files if "test_" in f or "/tests/" in f]
    debug_files = [f for f in all_python_files if "debug_" in f or "analyze_" in f]
    
    print(f"\n🧪 TEST FILES ({len(test_files)}):")
    for f in sorted(test_files):
        print(f"  {f}")
    
    print(f"\n🔍 DEBUG/ANALYSIS FILES ({len(debug_files)}):")
    for f in sorted(debug_files):
        print(f"  {f}")
    
    return used_files, unused, test_files, debug_files

if __name__ == "__main__":
    print("🌸 XOFlowers Bot - File Usage Analysis")
    print("=" * 50)
    
    os.chdir(Path(__file__).parent)
    analyze_system_usage()
