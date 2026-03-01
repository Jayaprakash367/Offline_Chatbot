"""
=============================================================
  MODULE 5 — COMMAND EXECUTION (Safe, Whitelisted)
  Executes ONLY pre-approved system commands.
  No admin privileges, no file deletion, no network.
=============================================================
"""

import os
import subprocess
import psutil
from typing import Tuple

from config import (
    WHITELISTED_APPS,
    CLOSEABLE_APPS,
    BLOCKED_KEYWORDS,
    MAX_INPUT_LENGTH,
)


class CommandExecutor:
    """Safely executes whitelisted OS-level commands."""

    # ── public API ────────────────────────────────────────

    def open_app(self, app_name: str) -> Tuple[bool, str]:
        """
        Open a whitelisted application.

        Returns (success, message).
        """
        if not self._validate_input(app_name):
            return (False, f"'{app_name}' contains blocked content.")

        key = app_name.lower().strip()
        command = WHITELISTED_APPS.get(key)

        if not command:
            # Try partial match
            for wl_name, wl_cmd in WHITELISTED_APPS.items():
                if wl_name in key or key in wl_name:
                    command = wl_cmd
                    key = wl_name
                    break

        if not command:
            return (False, f"'{app_name}' is not in my approved applications list.")

        try:
            subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return (True, key)
        except Exception as e:
            return (False, f"Could not open '{key}': {e}")

    def close_app(self, app_name: str) -> Tuple[bool, str]:
        """
        Close a whitelisted application using taskkill (no /F by default).
        """
        if not self._validate_input(app_name):
            return (False, f"'{app_name}' contains blocked content.")

        key = app_name.lower().strip()
        process_name = CLOSEABLE_APPS.get(key)

        if not process_name:
            for cl_name, cl_proc in CLOSEABLE_APPS.items():
                if cl_name in key or key in cl_name:
                    process_name = cl_proc
                    key = cl_name
                    break

        if not process_name:
            return (False, f"'{app_name}' is not in my closeable applications list.")

        try:
            subprocess.run(
                ["taskkill", "/IM", process_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            return (True, key)
        except Exception as e:
            return (False, f"Could not close '{key}': {e}")

    def get_system_status(self) -> dict:
        """Return current CPU, RAM, and battery information."""
        status = {
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "battery": self._battery_info(),
        }
        return status

    def get_battery(self) -> str:
        return self._battery_info()

    # ── safety ────────────────────────────────────────────

    def _validate_input(self, text: str) -> bool:
        """Check that the input is safe."""
        if not text or len(text) > MAX_INPUT_LENGTH:
            return False
        lower = text.lower()
        for blocked in BLOCKED_KEYWORDS:
            if blocked in lower:
                return False
        return True

    @staticmethod
    def _battery_info() -> str:
        battery = psutil.sensors_battery()
        if battery is None:
            return "No battery detected (desktop PC)"
        plugged = "Charging" if battery.power_plugged else "Not charging"
        return f"{battery.percent}% ({plugged})"
