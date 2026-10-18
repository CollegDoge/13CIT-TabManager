import json
import os
import tempfile

# variables
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

# load settings from disk
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}

# save settings to disk with crash mitigations
def save_settings(settings):
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, SETTINGS_FILE)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise