import re
from datetime import datetime, timezone
 
from dateutil.tz import gettz
 
DEFAULT_TZ = "Pacific/Auckland"  # default timezone (for nz so shouldnt need to change)
_FMT = "%Y%m%dT%H%M%S"
 
# parsing (LLM helped here with error checking/ICS decoding)
def _unfold(text):
    lines = []
    for raw in re.split(r"\r\n|\n|\r", text):
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines

# split each line into name, params, value
def _split_property(line):
    head, _, value = line.partition(":")
    name, *param_parts = head.split(";")
    params = {}
    for p in param_parts:
        k, _, v = p.partition("=")
        params[k.upper()] = v.strip('"')
    return name.upper(), params, value
 
# unescape newlines
def _unescape(text):
    return re.sub(r"\\([nN,;\\])", lambda m: "\n" if m.group(1) in "nN" else m.group(1), text)

# parese date/time 
def _parse_dt(value, params):
    value = value.strip()
    if params.get("VALUE") == "DATE" or len(value) == 8:
        return None
    if value.endswith("Z"):
        return datetime.strptime(value[:-1], _FMT).replace(tzinfo=timezone.utc)
    naive = datetime.strptime(value, _FMT)
    tz = gettz(params.get("TZID") or DEFAULT_TZ) or gettz(DEFAULT_TZ)
    return naive.replace(tzinfo=tz)
 
# build a dict from the parsed properties
def _build(props):
    if "SUMMARY" not in props or "DTSTART" not in props:
        return None
    if props.get("STATUS", ({}, ""))[1].strip().upper() == "CANCELLED":
        return None
    subject = _unescape(props["SUMMARY"][1]).strip()
    if not subject:
        return None
    try:
        start = _parse_dt(props["DTSTART"][1], props["DTSTART"][0])
        if start is None:
            return None
        end = start
        if "DTEND" in props:
            end = _parse_dt(props["DTEND"][1], props["DTEND"][0]) or start
    except ValueError:
        return None
    if end < start:
        end = start
    return {"subject": subject, "start": start.astimezone(), "end": end.astimezone()}

# parse the file
def parse_ics(path):
    # corruption protection (LLM)
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        text = f.read()
 
    events = []
    current = None

    # parse each line
    for line in _unfold(text):
        upper = line.strip().upper()
        if upper == "BEGIN:VEVENT":
            current = {}
            continue
        if upper == "END:VEVENT":
            ev = _build(current or {})
            if ev:
                events.append(ev)
            current = None
            continue
        if current is None or ":" not in line:
            continue
        name, params, value = _split_property(line)
        if name in ("SUMMARY", "DTSTART", "DTEND", "STATUS") and name not in current:
            current[name] = (params, value)
 
    # if we cant find any events, raise an error
    if not events:
        raise ValueError("somethings wrong here.. is this an ics file from parent portal?")
    events.sort(key=lambda e: e["start"])
    return events
 
def subject_counts(events):
    counts = {}
    for e in events:
        counts[e["subject"]] = counts.get(e["subject"], 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: kv[0].lower()))