import bisect
import json
import math
import os
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, time, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MAIN_FILE = os.path.join(DATA_DIR, "calendar-main.json") # imported ICS
CUSTOM_FILE = os.path.join(DATA_DIR, "calendar-custom.json") # custom events
STATE_FILE = os.path.join(DATA_DIR, "schedule-state.json") # what already fired / when each group was last opened

NOTIFY_BEFORE = timedelta(minutes=5)   # opens in 5 minutes notification
MIN_LIVE = timedelta(minutes=10)       # a lesson counts as "still on" for at least this long
CUSTOM_LIVE = timedelta(minutes=60)    # how late a custom event may still be opened
LOOKBACK = timedelta(hours=12)         # how far to look back for missed events
KEEP_FIRED = timedelta(days=3)         # forget fired-event records after this


# json file checking with corruption protection (LLM recommended)
def _read(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    try:  # set a broken file aside rather than silently overwriting it
        os.replace(path, path + ".corrupt")
    except OSError:
        pass
    return default

# write to json file with crash mitigations (LLM recommended)
def _write(path, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise

# imported ICS
def load_main():
    return _read(MAIN_FILE, None)

# save the imported ICS schedule to json
def save_main(source_name, events, assignments, enabled=True):
    """events: from ics.parse_ics. assignments: {subject: group_id or None}."""
    _write(MAIN_FILE, {
        "version": 1,
        "enabled": enabled,
        "source": source_name,
        "imported_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "assignments": assignments,
        "events": [
            {"subject": e["subject"], "start": e["start"].isoformat(), "end": e["end"].isoformat()}
            for e in events
        ],
    })

# delete the imported ICS schedule
def delete_main():
    if os.path.exists(MAIN_FILE):
        os.remove(MAIN_FILE)

# if enabled, open tab groups automatically
def set_main_enabled(enabled):
    data = load_main()
    if data is not None:
        data["enabled"] = bool(enabled)
        _write(MAIN_FILE, data)

# custom events (load, save, add w json, delete)
def load_custom():
    return list(_read(CUSTOM_FILE, {}).get("events", []))

def _save_custom(events):
    _write(CUSTOM_FILE, {"version": 1, "events": events})

def add_custom(name, start, repeat_days, group_id):
    event = {
        "id": uuid.uuid4().hex, # generated uuids
        "name": name.strip(),
        "start": start.replace(second=0, microsecond=0).isoformat(),
        "repeat_days": max(0, int(repeat_days)),
        "group_id": group_id,
        "enabled": True,
    }
    events = load_custom()
    events.append(event)
    _save_custom(events)
    return event

def delete_custom(event_id):
    events = load_custom()
    remaining = [e for e in events if e["id"] != event_id]
    if len(remaining) == len(events):
        return False
    _save_custom(remaining)
    return True

# if enabled, open custom events
def set_custom_enabled(event_id, enabled):
    events = load_custom()
    for e in events:
        if e["id"] == event_id:
            e["enabled"] = bool(enabled)
            _save_custom(events)
            return

# current state (fired events, last opened groups)
def load_state():
    state = _read(STATE_FILE, {})
    state.setdefault("fired", {})
    state.setdefault("last_opened", {})
    return state

# save the state
def save_state(state):
    cutoff = datetime.now().astimezone() - KEEP_FIRED
    keep = {}
    for key, when in state["fired"].items():
        try:
            if datetime.fromisoformat(when) >= cutoff:
                keep[key] = when
        except ValueError:
            pass
    state["fired"] = keep
    _write(STATE_FILE, {"version": 1, "fired": keep, "last_opened": state["last_opened"]})

# if a group was fired, remember it
def mark_fired(state, keys, now):
    for k in keys:
        state["fired"][k] = now.isoformat(timespec="seconds")

# if a group was opened, remember it
def mark_opened(state, group_id, now):
    state["last_opened"][group_id] = now.isoformat(timespec="seconds")

# occurrences (between, on_day, upcoming) - LLM assisted because my version was super screwed
@dataclass(frozen=True)
class Occurrence:
    key: str              # unique per occurrence; used to remember it already fired
    start: datetime       # aware, local time zone
    end: datetime | None
    name: str             # subject or custom event name
    group_id: str | None
    enabled: bool
    source: str           # "ics" or "custom"
    live_for: timedelta   # how long after `start` it's still worth opening

class Schedule:
    def __init__(self):
        self.reload()

    # reload the schedule
    def reload(self):
        main = load_main() or {}
        self.main_enabled = bool(main) and bool(main.get("enabled", True))
        assignments = main.get("assignments", {})

        # load imported ics
        self._ics = []
        for e in main.get("events", []):
            try:
                start = datetime.fromisoformat(e["start"]).astimezone()
                end = datetime.fromisoformat(e["end"]).astimezone()
                self._ics.append((start, end, e["subject"], assignments.get(e["subject"])))
            except (KeyError, ValueError):
                continue
        self._ics.sort(key=lambda x: x[0])
        self._ics_starts = [x[0] for x in self._ics]

        # also load custom events
        self._custom = []
        for e in load_custom():
            try:
                self._custom.append((e, datetime.fromisoformat(e["start"])))
            except (KeyError, ValueError):
                continue

    # occurrences starting within [t0, t1] (aware datetimes), sorted by start
    def between(self, t0, t1):
        out = []

        i = bisect.bisect_left(self._ics_starts, t0)
        while i < len(self._ics) and self._ics[i][0] <= t1:
            start, end, subject, group_id = self._ics[i]
            out.append(Occurrence(
                key=f"ics|{start.isoformat()}|{subject}",
                start=start, end=end, name=subject, group_id=group_id,
                enabled=self.main_enabled, source="ics",
                live_for=max(end - start, MIN_LIVE),
            ))
            i += 1

        # custom events are wall-clock local times; work in naive local time
        t0n = t0.astimezone().replace(tzinfo=None)
        t1n = t1.astimezone().replace(tzinfo=None)
        
        for ev, first in self._custom:
            step = int(ev.get("repeat_days", 0))
            if step <= 0:
                starts = [first] if t0n <= first <= t1n else []
            else:
                delta = timedelta(days=step)
                k = max(0, math.ceil((t0n - first) / delta))
                starts = []
                while first + k * delta <= t1n:
                    starts.append(first + k * delta)
                    k += 1
            for s in starts:
                out.append(Occurrence(
                    key=f"custom|{ev['id']}|{s.isoformat()}",
                    start=s.astimezone(), end=None, name=ev["name"],
                    group_id=ev.get("group_id"), enabled=bool(ev.get("enabled", True)),
                    source="custom", live_for=CUSTOM_LIVE,
                ))

        out.sort(key=lambda o: o.start)
        return out

    def on_day(self, day):
        # the day starts at midnight and ends at 11:59:59 PM
        t0 = datetime.combine(day, time.min).astimezone()
        t1 = datetime.combine(day + timedelta(days=1), time.min).astimezone() - timedelta(microseconds=1)
        return self.between(t0, t1)


# decide what to open
def pick_due(sched, state, now):
    candidates = []
    for occ in sched.between(now - LOOKBACK, now):
        if not occ.enabled or not occ.group_id:
            continue
        if now > occ.start + occ.live_for:
            continue
        if occ.key in state["fired"]:
            continue
        opened = state["last_opened"].get(occ.group_id)
        if opened and datetime.fromisoformat(opened) >= occ.start:
            continue  # the group was already opened since it was due
        candidates.append(occ)

    candidates.sort(key=lambda o: o.start)
    return (candidates[-1] if candidates else None), candidates

def upcoming(sched, state, now):
    # occurrences due within NOTIFY_BEFORE that haven't fired
    return [
        o for o in sched.between(now, now + NOTIFY_BEFORE)
        if o.enabled and o.group_id and o.start > now and o.key not in state["fired"]
    ]