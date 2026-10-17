import os
import sys
import subprocess
import platform

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

def get_available_browsers():
    """Scans the platform-specific text file and returns a list of (display_name, path) tuples."""
    os_name = platform.system()
    
    if os_name == "Windows":
        common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-win.txt")
    elif os_name == "Linux":
        common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-linux.txt")
    elif os_name == "Darwin":
        common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-mac.txt")
    else:
        return []

    if not os.path.exists(common_path_file):
        return []

    available = []
    seen_paths = set()
    
    with open(common_path_file, "r") as f:
        for line in f:
            raw_path = line.strip().strip('"')
            if not raw_path:
                continue
                
            expanded_path = os.path.expandvars(raw_path)
            
            if os.path.exists(expanded_path) and expanded_path not in seen_paths:
                seen_paths.add(expanded_path)
                display_name = get_browser_display_name(expanded_path)
                available.append((display_name, expanded_path))
                
    return available

def grouptest(browser_path=None):
    browsers = get_available_browsers()
    if not browsers:
        print("No common browser found")
        return

    browser = browser_path if browser_path else browsers[0][1]
    
    print("Test launching google, github and spotify")
    print("Using browser:", repr(browser))
    
    urls = [
        "https://www.google.com",
        "https://github.com",
        "https://open.spotify.com"
    ]
    subprocess.Popen([browser] + urls)

if __name__ == "__main__":
    grouptest()