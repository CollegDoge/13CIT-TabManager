import os
import platform
import sys

APP_NAME = "TabManager"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

# only support windows for startup apps, on linux it differs by DE/WM
def is_supported():
    return platform.system() == "Windows"

# launch foreground/background
def launch_command():
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}" --background'

    exe = sys.executable
    pythonw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.exists(pythonw):
        exe = pythonw
    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
    return f'"{exe}" "{main_py}" --background'

# if enabled, launch on startup
def is_enabled():
    if not is_supported():
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except FileNotFoundError:
        return False

# enable on startup
def enable():
    # this should never happen, but its here just in case
    if not is_supported():
        raise OSError("Start with PC is only supported on Windows.")
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, launch_command())

# disable on startup
def disable():
    if not is_supported():
        return
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
    except FileNotFoundError:
        pass

# sync with the registry
def sync():
    if is_enabled():
        try:
            enable()
        except OSError:
            pass