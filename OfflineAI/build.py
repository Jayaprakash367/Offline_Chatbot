"""
=============================================================
  BUILD SCRIPT — Package OfflineAI as a Windows .exe
  Uses PyInstaller to create a standalone executable
  that does NOT require Python to be installed.
  
  Usage:
    python build.py
=============================================================
"""

import subprocess
import sys
import os
import shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(PROJECT_DIR, "dist")
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
DATA_DIR = os.path.join(PROJECT_DIR, "data")


def main():
    print("=" * 60)
    print("  OfflineAI — Build Script")
    print("  Creating Windows .exe with PyInstaller")
    print("=" * 60)

    # 1. Check PyInstaller
    try:
        import PyInstaller
        print(f"\n✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("\n✗ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 2. Clean previous builds
    for d in [DIST_DIR, BUILD_DIR]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  Cleaned: {d}")

    # 3. Run PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",                     # One folder with all files
        "--name", "OfflineAI",
        "--icon", "NONE",               # No custom icon (add .ico if desired)
        "--add-data", f"{DATA_DIR};data",  # Bundle the data folder
        "--hidden-import", "pyttsx3.drivers",
        "--hidden-import", "pyttsx3.drivers.sapi5",
        "--hidden-import", "speech_recognition",
        "--hidden-import", "psutil",
        "--console",                    # Console window (needed for text mode)
        os.path.join(PROJECT_DIR, "main.py"),
    ]

    print("\n🔨  Building executable...\n")
    subprocess.check_call(cmd)

    # 4. Copy data folder to dist (in case --add-data didn't place it right)
    dist_data = os.path.join(DIST_DIR, "OfflineAI", "data")
    if not os.path.exists(dist_data):
        shutil.copytree(DATA_DIR, dist_data)
        print(f"\n  Copied data → {dist_data}")

    # Ensure user data dir exists in dist
    user_dir = os.path.join(dist_data, "user")
    os.makedirs(user_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print("  ✅  BUILD COMPLETE!")
    print(f"  Executable: {os.path.join(DIST_DIR, 'OfflineAI', 'OfflineAI.exe')}")
    print("  Run it on any Windows PC — no Python needed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
