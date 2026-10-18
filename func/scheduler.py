import math
from datetime import datetime, timedelta

from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QSystemTrayIcon

from func import groupstore, schedule

# constants
TICK_MS = 15_000

# format time
def _fmt_time(dt):
    return dt.strftime("%I:%M %p").lstrip("0")

# open a group
class Scheduler(QObject):
    def __init__(self, open_group_cb, tray_getter=lambda: None, parent=None):
        super().__init__(parent)
        self.open_group_cb = open_group_cb
        self.tray_getter = tray_getter
        self.schedule = schedule.Schedule()
        self.state = schedule.load_state()
        self.notified = set()

        self.timer = QTimer(self)
        self.timer.setInterval(TICK_MS)
        self.timer.timeout.connect(self.tick)

    def start(self):
        self.tick()  # catches anything missed while the app/PC was off
        self.timer.start()

    def reload(self): 
        self.schedule.reload()

    # remember a group was opened (by hand or by us) so it isn't opened again as 'missed'
    def record_open(self, group_id):
        schedule.mark_opened(self.state, group_id, datetime.now().astimezone())
        schedule.save_state(self.state)

    # decide what to open
    def tick(self, now=None):
        now = now or datetime.now().astimezone()

        # due events
        due, handled = schedule.pick_due(self.schedule, self.state, now)
        if handled:
            schedule.mark_fired(self.state, [o.key for o in handled], now)
        if due:
            group = groupstore.get_group(due.group_id)
            if group is not None and self.open_group_cb(group):
                schedule.mark_opened(self.state, group["id"], now)
                late = now - due.start > timedelta(minutes=1)
                if late:
                    msg = f"{group['name']} (late: {due.name} was due at {_fmt_time(due.start)})"
                else:
                    msg = f"{group['name']} ({due.name})"
                self._notify("Tab group opened", msg)
        if handled:
            schedule.save_state(self.state)

        # upcoming events
        for occ in schedule.upcoming(self.schedule, self.state, now):
            if occ.key in self.notified:
                continue
            self.notified.add(occ.key)
            group = groupstore.get_group(occ.group_id)
            if group is None:
                continue
            mins = max(1, math.ceil((occ.start - now).total_seconds() / 60))
            unit = "minute" if mins == 1 else "minutes"
            self._notify("Opening soon", f"{group['name']} opens in {mins} {unit} ({occ.name})")

    # notificaitons
    def _notify(self, title, message):
        tray = self.tray_getter()
        tray.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 6000)
