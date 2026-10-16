import os
import sys
import subprocess
import platform

os_name = platform.system()
print("OS:", os_name)

if os_name == "Windows":
    common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-win.txt")
elif os_name == "Linux":
    common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-linux.txt")
elif os_name == "Darwin":
    common_path_file = os.path.join(os.path.dirname(__file__), "../data/commonpath-mac.txt")
else:
    print("Unsupported OS")
    sys.exit(1)

common_paths = []
with open(common_path_file, "r") as f:
    for line in f:
        raw_path = line.strip().strip('"')
        if not raw_path:
            continue
            
        expanded_path = os.path.expandvars(raw_path)
        
        if os.path.exists(expanded_path):
            common_paths.append(expanded_path)

browser = common_paths[0] if common_paths else None

if browser is None:
    print("No common browser found")
    sys.exit(1)

def grouptest():
    print("Test launching google, github and spotify")
    print("Default browser:", repr(browser))
    urls = [
        "https://www.google.com",
        "https://github.com",
        "https://open.spotify.com"
    ]
    subprocess.Popen([browser] + urls)

if __name__ == "__main__":
    grouptest()