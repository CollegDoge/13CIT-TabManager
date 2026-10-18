import os
from datetime import date, datetime, timedelta

from PyQt6.QtCore import QDate, QSize, Qt, QTime, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from func import groupstore, ics, schedule

ACC_COLOR = "#213A73"   # nice blue color
ERROR_COLOR = "#e06c75" # nice red color
DIM_COLOR = "#7f8793"   # nice grey
DELETED = "(deleted group)"

def fmt_time(dt):
    return dt.strftime("%I:%M %p").lstrip("0") # e.g 9:05 AM

def fmt_day(d):
    return f"{d:%A} {d.day} {d:%B %Y}"

def fmt_short(d):
    return f"{d:%a} {d.day} {d:%b}"

def group_names(): # uuid + name
    return {g["id"]: g["name"] for g in groupstore.load_groups()}

# create dropdown for tab groups
def make_group_combo(groups, allow_none): 
    combo = QComboBox()
    if allow_none:
        combo.addItem("- no tab group -", None)
    for g in groups:
        combo.addItem(g["name"], g["id"])
    return combo

# ICS import dialog
class ImportIcsDialog(QDialog):
    def __init__(self, parent, filename, events, groups):
        super().__init__(parent)
        self.setWindowTitle("Import schedule")
        self.setMinimumSize(QSize(560, 460))

        counts = ics.subject_counts(events)
        layout = QVBoxLayout(self)

        intro = QLabel(
            f"Found {len(events)} lessons across {len(counts)} subjects in {filename}.\n"
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setColumnStretch(0, 1)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.combos = {}
        for row, (subject, n) in enumerate(counts.items()):
            label = QLabel(f"{subject}  ({n})")
            label.setTextFormat(Qt.TextFormat.PlainText)
            combo = make_group_combo(groups, allow_none=True)
            combo.setMinimumWidth(200)
            grid.addWidget(label, row, 0)
            grid.addWidget(combo, row, 1)
            self.combos[subject] = combo

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def assignments(self):
        return {subject: combo.currentData() for subject, combo in self.combos.items()}

# custom event dialog
class CustomEventDialog(QDialog):
    def __init__(self, parent, groups):
        # defaults
        super().__init__(parent)
        self.setWindowTitle("Add custom event")
        self.setMinimumWidth(420)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # items
        layout.addWidget(QLabel("Name"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. programming standard")
        self.name_input.setMaxLength(40)
        layout.addWidget(self.name_input)

        row = QHBoxLayout()
        date_col, time_col = QVBoxLayout(), QVBoxLayout()
        date_col.addWidget(QLabel("Date"))
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_col.addWidget(self.date_edit)
        time_col.addWidget(QLabel("Time"))
        soon = datetime.now() + timedelta(minutes=5 - datetime.now().minute % 5)
        self.time_edit = QTimeEdit(QTime(soon.hour, soon.minute))
        self.time_edit.setDisplayFormat("h:mm AP")
        time_col.addWidget(self.time_edit)
        row.addLayout(date_col)
        row.addLayout(time_col)
        layout.addLayout(row)

        repeat_row = QHBoxLayout()
        self.repeat_check = QCheckBox("Repeat?")
        self.repeat_spin = QSpinBox()
        self.repeat_spin.setRange(1, 365)
        self.repeat_spin.setPrefix("every ")
        self.repeat_spin.setSuffix(" days")
        self.repeat_spin.setEnabled(False)
        self.repeat_check.toggled.connect(self.repeat_spin.setEnabled)
        repeat_row.addWidget(self.repeat_check)
        repeat_row.addWidget(self.repeat_spin)
        repeat_row.addStretch()
        layout.addLayout(repeat_row)

        layout.addWidget(QLabel("Tab group to open"))
        self.group_combo = make_group_combo(groups, allow_none=False)
        layout.addWidget(self.group_combo)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {ERROR_COLOR};")
        self.error_label.setWordWrap(True)
        layout.addWidget(self.error_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get the date/time
    def start_datetime(self):
        return datetime.combine(self.date_edit.date().toPyDate(), self.time_edit.time().toPyTime()).replace(
            second=0, microsecond=0
        )

    # get the values from the form
    def values(self):
        # disable repeat items if not checked
        repeat = self.repeat_spin.value() if self.repeat_check.isChecked() else 0
        return (
            self.name_input.text().strip(),
            self.start_datetime(),
            repeat,
            self.group_combo.currentData(),
        )

    # accept the event (unless errors)
    def accept(self):
        name, start, repeat, group_id = self.values()
        if not name:
            self.error_label.setText("give the event a name smh")
        elif group_id is None:
            self.error_label.setText("gotta choose a tab group..")
        elif repeat == 0 and start < datetime.now() - schedule.CUSTOM_LIVE:
            self.error_label.setText("that time has already happened bludaroo.")
        else:
            super().accept()

# custom event card (LEFT BTM)
class CustomEventCard(QFrame):
    enabled_changed = pyqtSignal(str, bool)  # event id, enabled
    delete_requested = pyqtSignal(str)

    def __init__(self, event, group_name):
        # defaults
        super().__init__()
        self.event_id = event["id"]
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        # items
        top = QHBoxLayout()
        check = QCheckBox(event["name"].replace("&", "&&"))
        check.setToolTip("Untick to pause this event without deleting it")
        check.setChecked(bool(event.get("enabled", True)))
        font = check.font()
        font.setBold(True)
        check.setFont(font)
        check.clicked.connect(lambda checked: self.enabled_changed.emit(self.event_id, checked))
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.event_id))
        top.addWidget(check, 1)
        top.addWidget(delete_btn)
        layout.addLayout(top)

        start = datetime.fromisoformat(event["start"])
        step = int(event.get("repeat_days", 0))
        if step > 0:
            when = f"From {fmt_short(start)}, {fmt_time(start)}, every {step} day{'s' if step != 1 else ''}"
        else:
            when = f"{fmt_short(start)}, {fmt_time(start)}"
        detail = QLabel(f"{when}\nOpens: {group_name}")
        detail.setTextFormat(Qt.TextFormat.PlainText)
        detail.setFont(QFont("Inter", 9))
        layout.addWidget(detail)

# calendar page (RIGHT)
class CalendarWindow(QMainWindow):
    back_to_main_signal = pyqtSignal()
    schedule_changed = pyqtSignal()  # main window listens so the scheduler reloads

    def __init__(self):
        # defaults
        super().__init__()
        self.setWindowTitle("TabManager - Manage Calendar")
        self.setFixedSize(QSize(1000, 700))
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        self.view_day = date.today()
        self.sched = schedule.Schedule()

        pagelayout = QVBoxLayout()
        pagelayout.setSpacing(15)

        # items
        title_label = QLabel("<b>Calendar</b>")
        title_label.setFont(QFont("Inter", 24))
        pagelayout.addWidget(title_label)

        body = QHBoxLayout()
        body.setSpacing(20)
        body.setContentsMargins(10, 0, 10, 0)
        body.addLayout(self._build_left_pane(), 1)
        body.addLayout(self._build_right_pane(), 1)
        pagelayout.addLayout(body, 1)

        bottombar = QHBoxLayout()
        bottombar.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottombar.setSpacing(10)
        bottombar.setContentsMargins(10, 5, 0, 0)
        backBtn = QPushButton("Back")
        backBtn.setFixedSize(QSize(80, 30))
        backBtn.setStyleSheet(f"background-color: {ACC_COLOR};")
        backBtn.clicked.connect(self.go_back)
        bottombar.addWidget(backBtn)
        pagelayout.addLayout(bottombar)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

        self.refresh_all()

    # LEFT SIDE BUILD
    def _build_left_pane(self):
        left = QVBoxLayout()
        left.setSpacing(8)

        # imported schedule
        left.addWidget(QLabel("<b>Imported schedule</b>"))
        self.import_status = QLabel()
        self.import_status.setTextFormat(Qt.TextFormat.PlainText)
        self.import_status.setWordWrap(True)
        left.addWidget(self.import_status)

        row = QHBoxLayout()
        self.import_btn = QPushButton("Import ICS...")
        self.import_btn.clicked.connect(self.import_ics)
        self.delete_main_btn = QPushButton("Delete schedule")
        self.delete_main_btn.clicked.connect(self.delete_main)
        row.addWidget(self.import_btn)
        row.addWidget(self.delete_main_btn)
        row.addStretch()
        left.addLayout(row)

        self.main_enabled_cb = QCheckBox("Open tab groups automatically")
        self.main_enabled_cb.setToolTip("Untick to pause the schedule without deleting it")
        self.main_enabled_cb.clicked.connect(self.toggle_main_enabled)
        left.addWidget(self.main_enabled_cb)

        left.addSpacing(10)

        # custom events
        left.addWidget(QLabel("<b>Custom events</b>"))
        add_btn = QPushButton("Add custom event...")
        add_btn.clicked.connect(self.add_custom_event)
        add_row = QHBoxLayout()
        add_row.addWidget(add_btn)
        add_row.addStretch()
        left.addLayout(add_row)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(8)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.cards_container)
        left.addWidget(scroll, 1)
        return left

    # RIGHT SIDE BUILD
    def _build_right_pane(self):
        right = QVBoxLayout()
        right.setSpacing(8)
        right.addWidget(QLabel("<b>Schedule</b>"))

        nav = QHBoxLayout()
        prev_btn = QPushButton("<")
        prev_btn.setFixedWidth(36)
        prev_btn.clicked.connect(lambda: self.change_day(-1))
        next_btn = QPushButton(">")
        next_btn.setFixedWidth(36)
        next_btn.clicked.connect(lambda: self.change_day(1))
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self.go_today)
        self.day_label = QLabel()
        self.day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        day_font = self.day_label.font()
        day_font.setBold(True)
        self.day_label.setFont(day_font)
        nav.addWidget(prev_btn)
        nav.addWidget(self.day_label, 1)
        nav.addWidget(next_btn)
        nav.addWidget(today_btn)
        right.addLayout(nav)

        self.day_list = QListWidget()
        self.day_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.day_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        right.addWidget(self.day_list, 1)

        hint = QLabel("Greyed-out items open nothing (no tab group, or paused).")
        hint.setFont(QFont("Inter", 8))
        right.addWidget(hint)
        return right

    # refresh the calendar
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_all()  # groups may have been renamed/deleted since last time

    # refresh everything else
    def refresh_all(self):
        self.sched.reload()
        self.update_main_status()
        self.refresh_cards()
        self.refresh_day()

    def update_main_status(self):
        # check if the schedule exists
        main = schedule.load_main()
        has = main is not None
        self.delete_main_btn.setEnabled(has)
        self.main_enabled_cb.setEnabled(has)
        self.main_enabled_cb.setChecked(bool(has and main.get("enabled", True)))
        self.import_btn.setText("Import a new ICS schedule" if has else "Import ICS")

        if not has:
            self.import_status.setText("No schedule imported yet.")
            return

        # check schedule
        events = main.get("events", [])
        subjects = {e["subject"] for e in events}
        existing = group_names()
        assigned = sum(1 for s in subjects if main.get("assignments", {}).get(s) in existing)
        try:
            first = datetime.fromisoformat(events[0]["start"])
            last = datetime.fromisoformat(events[-1]["start"])
            span = f"{fmt_short(first)} to {fmt_short(last)}"
        except (IndexError, KeyError, ValueError):
            span = "no dates"
        self.import_status.setText(
            f"{main.get('source', 'schedule')}\n"
            f"{len(events)} lessons ({span})\n"
            f"{assigned} of {len(subjects)} subjects have a tab group"
        )

    # refresh the cards
    def refresh_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        # check if there are any custom events
        events = schedule.load_custom()
        if not events:
            empty = QLabel("No custom events yet!")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.addWidget(empty)
        names = group_names()
        for ev in events:
            card = CustomEventCard(ev, names.get(ev.get("group_id"), DELETED))
            card.enabled_changed.connect(self.custom_enabled_changed)
            card.delete_requested.connect(self.delete_custom_event)
            self.cards_layout.addWidget(card)
        self.cards_layout.addStretch()

    # refresh day (right)
    def refresh_day(self):
        self.day_label.setText(fmt_day(self.view_day) + ("  (today)" if self.view_day == date.today() else ""))
        self.day_list.clear()
        names = group_names()
        occurrences = self.sched.on_day(self.view_day)

        if not occurrences:
            item = QListWidgetItem("Nothing scheduled.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.day_list.addItem(item)
            return

        for occ in occurrences:
            when = fmt_time(occ.start)
            if occ.end and occ.end > occ.start:
                when += f" - {fmt_time(occ.end)}"

            dim = False
            if occ.group_id is None:
                action = "no tab group"
                dim = True
            elif occ.group_id not in names:
                action = DELETED
                dim = True
            else:
                action = f"opens {names[occ.group_id]}"
                if not occ.enabled:
                    action += " [paused]"
                    dim = True

            item = QListWidgetItem(f"{when}    {occ.name}   >   {action}")
            if dim:
                item.setForeground(QBrush(QColor(DIM_COLOR)))
            self.day_list.addItem(item)

    # updates
    def change_day(self, delta):
        self.view_day += timedelta(days=delta)
        self.refresh_day()

    def go_today(self):
        self.view_day = date.today()
        self.refresh_day()

    # ICS functionality/error prevention
    def import_ics(self):
        groups = groupstore.load_groups()
        if not groups:
            QMessageBox.information(
                self, "Create tab groups first",
                "Each subject opens a tab group, so create your tab groups first, then import the schedule.",
            )
            return

        if schedule.load_main() is not None:
            answer = QMessageBox.question(
                self, "Replace schedule?",
                "This replaces the schedule you imported before. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        path, _ = QFileDialog.getOpenFileName(
            self, "Select schedule (.ics)", os.path.expanduser("~"),
            "Calendar files (*.ics);;All files (*)",
        )
        if not path:
            return

        try:
            events = ics.parse_ics(path)
        except (OSError, ValueError) as e:
            QMessageBox.warning(self, "Can't read that file", str(e))
            return

        dialog = ImportIcsDialog(self, os.path.basename(path), events, groups)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        try:
            schedule.save_main(os.path.basename(path), events, dialog.assignments())
        except OSError as e:
            QMessageBox.warning(self, "Couldn't save schedule", str(e))
            return
        self.refresh_all()
        self.schedule_changed.emit()

    # delete the schedule function
    def delete_main(self):
        answer = QMessageBox.question(
            self, "Delete schedule",
            "Delete the imported schedule? You can import it again afterwards.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        schedule.delete_main()
        self.refresh_all()
        self.schedule_changed.emit()

    # enable/disable the schedule
    def toggle_main_enabled(self, checked):
        schedule.set_main_enabled(checked)
        self.refresh_all()
        self.schedule_changed.emit()

    # custom event functionality/error prevention
    def add_custom_event(self):
        groups = groupstore.load_groups()
        if not groups:
            QMessageBox.information(
                self, "Create tab groups first",
                "A custom event opens a tab group, so create one first.",
            )
            return
        dialog = CustomEventDialog(self, groups)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        name, start, repeat, group_id = dialog.values()
        try:
            schedule.add_custom(name, start, repeat, group_id)
        except OSError as e:
            QMessageBox.warning(self, "Couldn't save event", str(e))
            return
        self.refresh_all()
        self.schedule_changed.emit()

    # updates
    def custom_enabled_changed(self, event_id, enabled):
        schedule.set_custom_enabled(event_id, enabled)
        self.refresh_all()
        self.schedule_changed.emit()

    # delete custom event
    def delete_custom_event(self, event_id):
        answer = QMessageBox.question(
            self, "Delete event", "Delete this custom event? This can't be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        schedule.delete_custom(event_id)
        self.refresh_all()
        self.schedule_changed.emit()

    def go_back(self):
        self.back_to_main_signal.emit()
        self.hide()#