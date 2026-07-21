import argparse
import sys
import winreg
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "AISmartMirror"


def command():
    watchdog = PROJECT_ROOT / "tools" / "watchdog.py"
    return f'"{sys.executable}" "{watchdog}"'


def enable():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, command())
    print("AI Smart Mirror autostart enabled for the current Windows user.")


def disable():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        try:
            winreg.DeleteValue(key, VALUE_NAME)
        except FileNotFoundError:
            pass
    print("AI Smart Mirror autostart disabled.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("enable", "disable"))
    args = parser.parse_args()
    enable() if args.action == "enable" else disable()
