import json
import os
import tempfile
import uuid
from urllib.parse import urlparse

# variables
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
GROUPS_FILE = os.path.join(DATA_DIR, "groups.json")
SCHEMA_VERSION = 1

# error class
class InvalidURL(ValueError):
    pass

# check for https://, spaces, stuff like that. should work for most cases i think?
def normalize_url(raw):
    url = raw.strip()
    if not url:
        raise InvalidURL("URL is empty.")
    if any(c.isspace() for c in url):
        raise InvalidURL(f"'{raw}' contains spaces.")

    if "://" not in url:
        url = "https://" + url  # e.g "github.com" becomes "https://github.com"

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise InvalidURL(f"'{raw}' - make sure it's an http or https link.")

    host = parsed.hostname
    if not host or ("." not in host and host != "localhost"):
        raise InvalidURL(f"'{raw}' - this is NOT a valid URL lil bro.")
    return url

# load existing groups from disk
def load_groups():
    if not os.path.exists(GROUPS_FILE):
        return []
    try:
        # read the file/check for corruption (recommended by LLM).
        with open(GROUPS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return list(data.get("groups", []))
    except (json.JSONDecodeError, OSError, AttributeError):
        try:
            os.replace(GROUPS_FILE, GROUPS_FILE + ".corrupt")
        except OSError:
            pass
        return []

# save the list of groups to disk with crash mitigations (recommended by LLM).
def save_groups(groups):
    os.makedirs(DATA_DIR, exist_ok=True)
    payload = {"version": SCHEMA_VERSION, "groups": groups}
    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, GROUPS_FILE)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

# create, update, delete groups (CRUD)
def get_group(group_id):
    for g in load_groups():
        if g["id"] == group_id:
            return g
    return None

# check for duplicate names, and clean up user input. most of this was recommended by an LLM.
def _clean(name, urls, groups, ignore_id=None):
    name = name.strip()
    if not name:
        raise ValueError("give the group a name smh")

    for g in groups:
        if g["id"] != ignore_id and g["name"].lower() == name.lower():
            raise ValueError(f"this group '{g['name']}' already exists matey")

    cleaned = []
    for u in urls:
        n = normalize_url(u)
        if n not in cleaned:
            cleaned.append(n)
    if not cleaned:
        raise ValueError("gotta add atleast a single URL smh")
    return name, cleaned

# add group to list of groups
def add_group(name, urls):
    groups = load_groups()
    name, urls = _clean(name, urls, groups)
    group = {"id": uuid.uuid4().hex, "name": name, "urls": urls}
    groups.append(group)
    save_groups(groups)
    return group

# update group in list of groups
def update_group(group_id, name, urls):
    groups = load_groups()
    name, urls = _clean(name, urls, groups, ignore_id=group_id)
    for g in groups:
        if g["id"] == group_id:
            g["name"] = name
            g["urls"] = urls
            save_groups(groups)
            return g
    raise KeyError("has been deleted already D:")

# delte group from list of groups
def delete_group(group_id):
    groups = load_groups()
    remaining = [g for g in groups if g["id"] != group_id]
    if len(remaining) == len(groups):
        return False
    save_groups(remaining)
    return True