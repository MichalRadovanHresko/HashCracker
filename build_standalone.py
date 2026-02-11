#!/usr/bin/env python3

import subprocess
import sys
import os
import platform

def get_platform():
    current_os = platform.system()
    return current_os

def build_app():
    current_platform = get_platform()
    print(f"Building for {current_platform}...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=HashCracker",
        "HashCracker.py"
    ]
    
    if current_platform == "Darwin":
        print("Building macOS .app bundle...")
        cmd.extend(["--icon=icon.icns"]) if os.path.exists("icon.icns") else None
        
    elif current_platform == "Windows":
        print("Building Windows .exe executable...")
        cmd.extend(["--icon=icon.ico"]) if os.path.exists("icon.ico") else None
        
    elif current_platform == "Linux":
        print("Building Linux executable...")
    
    result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
    
    if result.returncode == 0:
        print(f"\n[OK] Build successful for {current_platform}!")
        
        if current_platform == "Darwin":
            print("App created: dist/HashCracker.app")
            print("Users can now double-click HashCracker.app!")
            
        elif current_platform == "Windows":
            print("Executable created: dist/HashCracker.exe")
            print("Users can now double-click HashCracker.exe!")
            
        elif current_platform == "Linux":
            print("Executable created: dist/HashCracker")
            print("Users can run: ./HashCracker (from dist/ folder)")
            
        print("\nNo dependencies needed - PyQt6 is included!")
    else:
        print(f"[FAILED] Build failed for {current_platform}!")
        sys.exit(1)

if __name__ == "__main__":
    try:
        import PyInstaller
    except ImportError:
        print("WARNING: PyInstaller not found!")
        print("Install it with: pip install pyinstaller")
        sys.exit(1)
    
    build_app()

