import os
import sys
import subprocess
import platform

from func.settings import load_settings, save_settings

# nicer name for browser selection
def get_browser_display_name(path):
    path_lower = path.lower()
    if "brave" in path_lower:
        return "Brave"
    elif "chrome" in path_lower and "sxs" in path_lower:
        return "Google Chrome Canary"
    elif "chrome" in path_lower and "beta" in path_lower:
        return "Google Chrome Beta"
    elif "chrome" in path_lower:
        return "Google Chrome"
    elif "firefox" in path_lower:
        return "Firefox"
    elif "librewolf" in path_lower:
        return "LibreWolf"
    elif "floorp" in path_lower:
        return "Floorp"
    elif "vivaldi" in path_lower:
        return "Vivaldi"
    elif "opera" in path_lower:
        return "Opera"
    elif "edge" in path_lower:
        return "Microsoft Edge"
    elif "chromium" in path_lower:
        return "Chromium"
    else:
        # fallback name for other browsers, still looks nice enough
        base = os.path.basename(path)
        return os.path.splitext(base)[0].replace("-", " ").title()

# common path files for windows, linux
def _common_path_file():
    names = {"Windows": "commonpath-win.txt", "Linux": "commonpath-linux.txt"}
    name = names.get(platform.system())
    if name is None:
        return None
    return os.path.join(os.path.dirname(__file__), "../data", name)

# check for browsers against predefined lists
def get_available_browsers():
    available = []
    seen_paths = set()

    def _add(path):
        key = os.path.normcase(os.path.abspath(path))
        if key in seen_paths or not os.path.exists(path):
            return
        seen_paths.add(key)
        available.append((get_browser_display_name(path), path))

    common_path_file = _common_path_file()
    if common_path_file and os.path.exists(common_path_file):
        with open(common_path_file, "r") as f:
            for line in f:
                raw_path = line.strip().strip('"')
                if raw_path:
                    _add(os.path.expandvars(raw_path))

    # user-selected browsers (see add_custom_browser). Stale paths are skipped.
    for path in load_settings().get("custom_browsers", []):
        _add(path)

    return available

def add_custom_browser(path):
    path = os.path.abspath(path)  # also normalises the "/" the file dialog returns on Windows
    if not os.path.isfile(path):
        raise ValueError("That file doesn't exist.")
    if platform.system() == "Windows":
        if not path.lower().endswith(".exe"):
            raise ValueError("Please choose an .exe file.")
    elif not os.access(path, os.X_OK):
        raise ValueError("That file isn't executable.")

    # already in the list? reuse the existing entry instead of duplicating it
    key = os.path.normcase(path)
    for name, existing in get_available_browsers():
        if os.path.normcase(os.path.abspath(existing)) == key:
            return name, existing

    # add a browser to the list of available browsers + settings for persistence
    settings = load_settings()
    custom = settings.setdefault("custom_browsers", [])
    custom.append(path)
    save_settings(settings)
    return get_browser_display_name(path), path

# firefox and its forks
FIREFOX_BASED = ("firefox", "librewolf", "floorp", "waterfox")

def is_firefox_based(browser_path):
    names = {
        os.path.basename(browser_path).lower(),
        os.path.basename(os.path.realpath(browser_path)).lower(),
    }
    return any(f in n for n in names for f in FIREFOX_BASED)

# launch args per browser platform
def build_launch_args(browser_path, urls):
    if is_firefox_based(browser_path):
        if len(urls) == 1:
            return ["-new-window", urls[0]]
        return list(urls)
    return ["--new-window"] + list(urls)

def open_group(group, browser_path=None):
    # probably useless, but just in case
    urls = group.get("urls", [])
    if not urls:
        print("group has no urls ???")
        return False

    # specified browser
    browser = browser_path

    # no browser found/specified
    if not browser:
        browsers = get_available_browsers()
        if not browsers:
            print("No common browser found")
            return False
        browser = browsers[0][1]

    # should catch most problems, i didnt have any in testing
    try:
        subprocess.Popen([browser] + build_launch_args(browser, urls))
    except OSError as e:
        print("something died :( -", e)
        return False
    return True

if __name__ == "__main__":
    grouptest()