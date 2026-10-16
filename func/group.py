import os
import sys
import subprocess
import platform

os_name = platform.system()

if os_name == "Windows":
    common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-win.txt")
elif os_name == "Linux":
    common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-linux.txt")
elif os_name == "Darwin":
    common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-mac.txt")
else:
    print("Unsupported OS")
    sys.exit(1)

with open(common_path_file, "r") as f:
    # remove empty lines, and only keep lines that exist
    common_paths = [line.strip() for line in f if line.strip() and os.path.exists(line.strip())]

browser = common_paths[0] if common_paths else None

def grouptest():
    print("Test launching google, github and spotify")
    print("Default browser:", repr(browser))
    urls = [
        "https://www.google.com",
        "https://github.com",
        "https://open.spotify.com"
    ]
    subprocess.Popen([browser] + urls)