"""
=============================================================
  BUILD SCRIPT — Package JARVIS as a Windows executable

  Usage:
    python build_jarvis.py
=============================================================
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
DATA_DIR = PROJECT_DIR / "data"
STATIC_DIR = PROJECT_DIR / "jarvis" / "static"
VOSK_MODEL_DIR = PROJECT_DIR / "vosk-model"

APP_NAME = "JarvisAI"
ENTRY_SCRIPT = PROJECT_DIR / "jarvis_app.py"


def ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # type: ignore

        print(f"[ok] PyInstaller {PyInstaller.__version__} found")
    except Exception:
        print("[info] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def clean_old_builds() -> None:
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"[clean] {directory}")


def pyinstaller_cmd() -> list[str]:
    return [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--name",
        APP_NAME,
        "--console",
        "--add-data",
        f"{DATA_DIR};data",
        "--add-data",
        f"{STATIC_DIR};jarvis\\static",
        "--hidden-import",
        "pyttsx3.drivers",
        "--hidden-import",
        "pyttsx3.drivers.sapi5",
        "--hidden-import",
        "speech_recognition",
        "--hidden-import",
        "psutil",
        str(ENTRY_SCRIPT),
    ]


def copy_optional_assets(app_dir: Path) -> None:
    # Include offline speech model if present.
    if VOSK_MODEL_DIR.exists():
        target = app_dir / "vosk-model"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(VOSK_MODEL_DIR, target)
        print(f"[copy] vosk-model -> {target}")

    # Ensure user memory folder exists in packaged output.
    user_dir = app_dir / "data" / "user"
    user_dir.mkdir(parents=True, exist_ok=True)


def write_launchers(app_dir: Path) -> None:
    desktop_launcher = app_dir / "Start-JARVIS-Desktop.bat"
    web_launcher = app_dir / "Start-JARVIS-Web.bat"

    desktop_launcher.write_text(
        "@echo off\n"
        "cd /d %~dp0\n"
        f"{APP_NAME}.exe --desktop\n",
        encoding="utf-8",
    )

    web_launcher.write_text(
        "@echo off\n"
        "cd /d %~dp0\n"
        f"{APP_NAME}.exe\n",
        encoding="utf-8",
    )

    print(f"[write] {desktop_launcher.name}")
    print(f"[write] {web_launcher.name}")


def main() -> None:
    print("=" * 62)
    print("  JARVIS Build Script")
    print("=" * 62)

    ensure_pyinstaller()
    clean_old_builds()

    cmd = pyinstaller_cmd()
    print("[build] Running PyInstaller...")
    subprocess.check_call(cmd)

    app_dir = DIST_DIR / APP_NAME
    if not app_dir.exists():
        raise RuntimeError(f"Build output not found: {app_dir}")

    copy_optional_assets(app_dir)
    write_launchers(app_dir)

    print("\n" + "=" * 62)
    print("  Build complete")
    print(f"  Output folder: {app_dir}")
    print(f"  Desktop launch: {app_dir / 'Start-JARVIS-Desktop.bat'}")
    print(f"  Web launch: {app_dir / 'Start-JARVIS-Web.bat'}")
    print("=" * 62)


if __name__ == "__main__":
    main()
