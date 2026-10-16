import os
import sys
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
    common_paths = f.readlines()

browser = common_paths[0].strip()
    
def grouptest():
    print("Test launching google, github and spotify")
    print("Default browser:", repr(browser))
    os.system(f'"{browser}" https://www.google.com')
    os.system(f'"{browser}" https://github.com')
    os.system(f'"{browser}" https://open.spotify.com')