# to interpret
# 
# for each subject
# SUMMARY:FP (13MPH)
# DTSTART;TZID=Pacific/Auckland:20260203T100000
# DTEND;TZID=Pacific/Auckland:20260203T110000

import sys
import os

from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import gettz


def interpret(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("SUMMARY:"):
            summary = line.split(":")[1].strip()
            print("SUBJECT: " + str(summary))

        elif line.startswith("DTSTART"):
            start = line.split(":")[1].strip()
            start = parse(start)
            start = start.astimezone(gettz("Pacific/Auckland"))
            print("FROM: " + str(start))
        elif line.startswith("DTEND"):
            end = line.split(":")[1].strip()
            end = parse(end)
            end = end.astimezone(gettz("Pacific/Auckland"))
            print("TO: " + str(end))
            print("")