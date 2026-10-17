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

# check for browsers against predefined lists
def get_available_browsers():
    os_name = platform.system()
    
    if os_name == "Windows":
        common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-win.txt")
    elif os_name == "Linux":
        common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-linux.txt")
    elif os_name == "Darwin":
        common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-mac.txt")
    else:
        return []

    # if a path doesnt exist
    if not os.path.exists(common_path_file):
        return []

    # build a list of (display_name, path) tuples (available browsers)
    available = []
    seen_paths = set()
    
    # read the file
    with open(common_path_file, "r") as f:
        for line in f:
            raw_path = line.strip().strip('"')
            if not raw_path:
                continue
                
            expanded_path = os.path.expandvars(raw_path)
            
            # check if the path exists and is not already in the list
            if os.path.exists(expanded_path) and expanded_path not in seen_paths:
                seen_paths.add(expanded_path)
                display_name = get_browser_display_name(expanded_path)
                available.append((display_name, expanded_path))
                
    # finally, return the list of actually available browsers
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
 
    settings = load_settings()
    custom = settings.setdefault("custom_browsers", [])
    custom.append(path)
    save_settings(settings)
    return get_browser_display_name(path), path


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
        subprocess.Popen([browser] + urls)
    except OSError as e: 
        print("something died :( -", e)
        return False
    return True


if __name__ == "__main__":
    grouptest()