#!/usr/bin/env python3
"""Generate schedule-first course pages for Jupyter Book.

Outputs:
- course_schedule/days/DayXX_Topic.md (one file per course day)
- course_schedule/Schedule.md
- course_schedule/Semester_Assignments.md
- _toc.yml (schedule-focused navigation)

Single-source inputs:
- config/[semester]_calendar.yml
- config/topics_per_day.yml
"""

from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DayEntry:
    day_id: str
    module: str
    title: str
    status: str = "planned"
    studio: str = ""


@dataclass(frozen=True)
class DayAssignment:
    entry: DayEntry
    date: datetime | None
    status: str
    note: str = ""


VALID_WEEKDAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}


@dataclass(frozen=True)
class ParsedScheduleFilename:
    file_path: Path
    anchor_day: int
    relation: str
    slug: str
    offset_days: int | None = None
    weekday: str | None = None


@dataclass(frozen=True)
class ScheduleFilenameWarning:
    file_path: Path
    message: str


def parse_schedule_filename(file_path: Path) -> tuple[ParsedScheduleFilename | None, ScheduleFilenameWarning | None]:
    """Parse one Schedule filename using the instructor convention.

    Supported patterns:
    - NN-class-topic-slug.md
    - NN-same-topic-slug.md
    - NN-plus-D-topic-slug.md
    - NN-next-WDAY-topic-slug.md
    """

    stem = file_path.stem.strip().lower()

    class_match = re.match(r"^(\d{2})-class-([a-z0-9][a-z0-9-]*)$", stem)
    if class_match:
        return (
            ParsedScheduleFilename(
                file_path=file_path,
                anchor_day=int(class_match.group(1)),
                relation="class",
                slug=class_match.group(2),
            ),
            None,
        )

    same_match = re.match(r"^(\d{2})-same-([a-z0-9][a-z0-9-]*)$", stem)
    if same_match:
        return (
            ParsedScheduleFilename(
                file_path=file_path,
                anchor_day=int(same_match.group(1)),
                relation="same",
                slug=same_match.group(2),
            ),
            None,
        )

    plus_match = re.match(r"^(\d{2})-plus-(\d+)-([a-z0-9][a-z0-9-]*)$", stem)
    if plus_match:
        return (
            ParsedScheduleFilename(
                file_path=file_path,
                anchor_day=int(plus_match.group(1)),
                relation="plus",
                offset_days=int(plus_match.group(2)),
                slug=plus_match.group(3),
            ),
            None,
        )

    next_match = re.match(r"^(\d{2})-next-([a-z]{3})-([a-z0-9][a-z0-9-]*)$", stem)
    if next_match:
        weekday = next_match.group(2)
        if weekday not in VALID_WEEKDAYS:
            return None, ScheduleFilenameWarning(file_path=file_path, message=f"Invalid weekday token: {weekday}")

        return (
            ParsedScheduleFilename(
                file_path=file_path,
                anchor_day=int(next_match.group(1)),
                relation="next",
                weekday=weekday,
                slug=next_match.group(3),
            ),
            None,
        )

    return None, ScheduleFilenameWarning(
        file_path=file_path,
        message=(
            "Filename does not match convention. Expected one of: "
            "NN-class-*, NN-same-*, NN-plus-D-*, NN-next-WDAY-*"
        ),
    )


def parse_schedule_directory(schedule_dir: Path) -> tuple[list[ParsedScheduleFilename], list[ScheduleFilenameWarning]]:
    """Parse all markdown files in a Schedule folder.

    This is a Step 1 parser-only utility. Step 2 will wire parser output
    into schedule generation behavior.
    """

    parsed: list[ParsedScheduleFilename] = []
    warnings: list[ScheduleFilenameWarning] = []

    for file_path in sorted(schedule_dir.glob("*.md")):
        item, warning = parse_schedule_filename(file_path)
        if item is not None:
            parsed.append(item)
        elif warning is not None:
            warnings.append(warning)

    return parsed, warnings


def prettify_slug(slug: str) -> str:
    words = [part for part in slug.strip().split("-") if part]
    if not words:
        return "TBD"
    return " ".join(word.capitalize() for word in words)


def markdown_title_for_file(file_path: Path) -> str:
    """Extract a readable title from markdown content.

    Priority:
    1) YAML frontmatter `title:`
    2) First markdown H1 heading
    3) Prettified filename slug
    """

    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if lines and lines[0].strip() == "---":
        for line in lines[1:]:
            if line.strip() == "---":
                break
            match = re.match(r"^\s*title\s*:\s*[\"']?(.*?)[\"']?\s*$", line)
            if match and match.group(1).strip():
                return match.group(1).strip()

    for line in lines:
        heading = line.strip()
        if heading.startswith("# "):
            return heading[2:].strip()

    return prettify_slug(file_path.stem)


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def day_number(day_id: str) -> int:
    digits = "".join(ch for ch in day_id if ch.isdigit())
    return int(digits) if digits else 0


def format_date(day: datetime | None) -> str:
    if day is None:
        return "TBD"
    return f"{day.strftime('%A')}, {day.strftime('%B')} {day.day}, {day.year}"


def format_short_date(day: datetime | None) -> str:
    if day is None:
        return "TBD"
    return day.strftime("%b %d")


def iso_date(day: datetime | None) -> str:
    if day is None:
        return ""
    return day.strftime("%Y-%m-%d")


def jekyll_date(day: datetime | None) -> str:
    if day is None:
        return "TBD"
    return day.strftime("%Y-%m-%d")


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    return re.sub(r"_+", "_", cleaned).strip("_") or "milestone"


class ScheduleSiteGenerator:
    def __init__(self, calendar_path: Path, content_path: Path):
        self.calendar_path = calendar_path
        self.content_path = content_path
        self.calendar = read_yaml(calendar_path)
        self.content = read_yaml(content_path)

    def semester_name(self) -> str:
        return self.calendar.get("semester_info", {}).get("name", "Semester")

    def first_day(self) -> datetime:
        return datetime.strptime(self.calendar["semester_info"]["first_day"], "%Y-%m-%d")

    def last_day(self) -> datetime:
        return datetime.strptime(self.calendar["semester_info"]["last_day"], "%Y-%m-%d")

    def meeting_days(self) -> list[str]:
        semester_days = self.calendar.get("semester_info", {}).get("meeting_days")
        class_days = self.calendar.get("class_days")
        return list(semester_days or class_days or ["Tuesday", "Thursday"])

    def break_ranges(self) -> list[tuple[datetime, datetime]]:
        ranges: list[tuple[datetime, datetime]] = []

        for info in (self.calendar.get("breaks") or {}).values():
            if "date" in info:
                day = datetime.strptime(info["date"], "%Y-%m-%d")
                ranges.append((day, day))
            elif "start" in info and "end" in info:
                start = datetime.strptime(info["start"], "%Y-%m-%d")
                end = datetime.strptime(info["end"], "%Y-%m-%d")
                ranges.append((start, end))

        cancelled_classes = self.calendar.get("schedule_adjustments", {}).get("cancelled_classes", [])
        for cancelled in cancelled_classes:
            day = datetime.strptime(cancelled["date"], "%Y-%m-%d")
            ranges.append((day, day))

        return ranges

    def is_break(self, day: datetime) -> bool:
        return any(start <= day <= end for start, end in self.break_ranges())

    def meeting_dates(self) -> list[datetime]:
        dates: list[datetime] = []
        cursor = self.first_day()
        end = self.last_day()
        valid_days = set(self.meeting_days())

        while cursor <= end:
            if cursor.strftime("%A") in valid_days and not self.is_break(cursor):
                dates.append(cursor)
            cursor += timedelta(days=1)

        return dates

    def day_overrides(self) -> dict[str, dict[str, Any]]:
        return self.calendar.get("schedule_adjustments", {}).get("day_overrides", {}) or {}

    def ordered_day_entries(self) -> list[DayEntry]:
        days = self.content.get("days") or {}
        entries: list[DayEntry] = []
        for day_id in sorted(days, key=day_number):
            info = days[day_id] or {}
            entries.append(
                DayEntry(
                    day_id=day_id,
                    module=info.get("module", "Unassigned"),
                    title=info.get("title", day_id),
                    status=info.get("status", "planned"),
                    studio=info.get("studio", ""),
                )
            )
        return entries

    def day_assignments(self) -> list[DayAssignment]:
        entries = self.ordered_day_entries()
        dates = self.meeting_dates()
        overrides = self.day_overrides()

        override_dates = {
            datetime.strptime(override["date"], "%Y-%m-%d")
            for override in overrides.values()
            if override.get("date")
        }
        automatic_dates = [day for day in dates if day not in override_dates]

        result: list[DayAssignment] = []
        for entry in entries:
            override = overrides.get(entry.day_id, {})
            status = override.get("status", entry.status)
            note = override.get("note", "")

            if override.get("date"):
                assigned_date = datetime.strptime(override["date"], "%Y-%m-%d")
            elif automatic_dates:
                assigned_date = automatic_dates.pop(0)
            else:
                assigned_date = None

            result.append(DayAssignment(entry=entry, date=assigned_date, status=status, note=note))

        return result

    def _week_start_iso_for(self, day: datetime) -> str:
        return (day - timedelta(days=day.weekday())).strftime("%Y-%m-%d")

    def _next_weekday_after(self, day: datetime, weekday_token: str) -> datetime:
        weekday_map = {
            "mon": 0,
            "tue": 1,
            "wed": 2,
            "thu": 3,
            "fri": 4,
            "sat": 5,
            "sun": 6,
        }
        target = weekday_map[weekday_token]
        delta = (target - day.weekday()) % 7
        if delta == 0:
            delta = 7
        return day + timedelta(days=delta)

    def _build_calendar_first_schedule_events(
        self,
        schedule_source_dir: Path,
    ) -> tuple[list[dict[str, str | None]], list[str], list[Path]]:
        """Build schedule events from calendar slots plus Schedule-file overlays.

        Step 2 behavior:
        - Compute all class days from the semester calendar.
        - Overlay `Schedule` filenames parsed by convention.
        - Emit `TBD` rows for missing class files.
        """

        parsed_items, parse_warnings = parse_schedule_directory(schedule_source_dir)
        warnings: list[str] = [f"{w.file_path.name}: {w.message}" for w in parse_warnings]
        source_files = [item.file_path for item in parsed_items]

        class_dates = self.meeting_dates()
        events: list[dict[str, str | None]] = []

        class_items = [item for item in parsed_items if item.relation == "class"]
        class_items.sort(key=lambda item: item.file_path.name)
        class_by_anchor: dict[int, ParsedScheduleFilename] = {}
        for item in class_items:
            if item.anchor_day in class_by_anchor:
                warnings.append(
                    f"{item.file_path.name}: duplicate class anchor {item.anchor_day:02d}; "
                    f"using {class_by_anchor[item.anchor_day].file_path.name}"
                )
                continue
            class_by_anchor[item.anchor_day] = item

        for index, class_date in enumerate(class_dates, start=1):
            class_item = class_by_anchor.get(index)
            if class_item is None:
                events.append(
                    {
                        "date": iso_date(class_date),
                        "week_start": self._week_start_iso_for(class_date),
                        "title": "TBD",
                        "url": None,
                        "event_type": "class",
                        "day_id": f"Day{index:02d}",
                        "module": None,
                    }
                )
                continue

            title = markdown_title_for_file(class_item.file_path)
            events.append(
                {
                    "date": iso_date(class_date),
                    "week_start": self._week_start_iso_for(class_date),
                    "title": title,
                    "url": f"/Schedule/{class_item.file_path.stem}",
                    "event_type": "class",
                    "day_id": f"Day{index:02d}",
                    "module": None,
                }
            )

        for item in parsed_items:
            if item.relation == "class":
                continue

            if item.anchor_day < 1 or item.anchor_day > len(class_dates):
                warnings.append(
                    f"{item.file_path.name}: anchor {item.anchor_day:02d} is out of range for this semester"
                )
                continue

            anchor_date = class_dates[item.anchor_day - 1]
            target_date: datetime
            if item.relation == "same":
                target_date = anchor_date
            elif item.relation == "plus":
                target_date = anchor_date + timedelta(days=int(item.offset_days or 0))
            elif item.relation == "next":
                if not item.weekday:
                    warnings.append(f"{item.file_path.name}: missing weekday token")
                    continue
                target_date = self._next_weekday_after(anchor_date, item.weekday)
            else:
                warnings.append(f"{item.file_path.name}: unsupported relation {item.relation}")
                continue

            title = markdown_title_for_file(item.file_path)
            events.append(
                {
                    "date": iso_date(target_date),
                    "week_start": self._week_start_iso_for(target_date),
                    "title": title,
                    "url": f"/Schedule/{item.file_path.stem}",
                    "event_type": item.relation,
                    "day_id": f"Day{item.anchor_day:02d}",
                    "module": None,
                }
            )

        events.sort(key=lambda entry: (str(entry.get("date", "")), str(entry.get("title", ""))))
        return events, warnings, source_files

    def week_number(self, day: datetime | None) -> str:
        if day is None:
            return ""
        week = ((day - self.first_day()).days // 7) + 1
        return str(week)

    def week_start(self, week_number_value: int) -> datetime:
        return self.first_day() + timedelta(days=(week_number_value - 1) * 7)

    def date_for_weekday_in_week(self, week_number_value: int, weekday_name: str) -> datetime | None:
        weekday_map = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }
        target = weekday_map.get(weekday_name.strip().lower())
        if target is None:
            return None

        week_start = self.week_start(week_number_value)
        offset = target - week_start.weekday()
        day = week_start + timedelta(days=offset)
        if day < self.first_day() or day > self.last_day():
            return None
        return day

    def milestone_due_dates(self) -> list[dict[str, str]]:
        milestones = self.content.get("milestone_due_dates") or []
        rows: list[dict[str, str | list[str]]] = []

        for index, milestone in enumerate(milestones, start=1):
            week_value = milestone.get("week")
            title = milestone.get("title", "Milestone")
            weekday = milestone.get("day", "Monday")
            notes = milestone.get("notes", "")
            milestone_id = milestone.get("id", f"M{index:02d}")
            focus = milestone.get("focus", "")
            required_items = milestone.get("required_items", [])
            rubric = milestone.get("rubric", [])

            if isinstance(week_value, int):
                due_date = self.date_for_weekday_in_week(week_value, weekday)
                week_text = str(week_value)
            else:
                due_date = None
                week_text = ""

            rows.append(
                {
                    "id": milestone_id,
                    "week": week_text,
                    "due_date": format_date(due_date),
                    "due_short": format_short_date(due_date),
                    "due_iso": iso_date(due_date),
                    "title": title,
                    "notes": notes,
                    "focus": focus,
                    "required_items": required_items,
                    "rubric": rubric,
                }
            )

        return rows

    def homework_due_dates(self) -> list[dict[str, str]]:
        deadlines = self.content.get("homework_deadlines") or []
        rows: list[dict[str, str]] = []

        for entry in deadlines:
            week_value = entry.get("week")
            weekday = entry.get("day", "Friday")
            title = entry.get("title", "Homework deadline")

            if isinstance(week_value, int):
                due_date = self.date_for_weekday_in_week(week_value, weekday)
                week_text = str(week_value)
            else:
                due_date = None
                week_text = ""

            rows.append(
                {
                    "week": week_text,
                    "due_date": format_date(due_date),
                    "due_iso": iso_date(due_date),
                    "title": title,
                }
            )

        return rows

    def due_items_by_iso(
        self,
        day_files: list[tuple[DayAssignment, Path]],
        milestone_files: list[tuple[dict[str, str | list[str]], Path]],
    ) -> dict[str, list[str]]:
        milestone_by_id = {str(m.get("id", "")): p for m, p in milestone_files}
        assignment_by_day_id = {assignment.entry.day_id: assignment for assignment, _ in day_files}
        due_items: dict[str, list[str]] = {}

        for milestone in self.milestone_due_dates():
            due_iso = str(milestone.get("due_iso", ""))
            if not due_iso:
                continue
            milestone_id = str(milestone.get("id", ""))
            detail_path = milestone_by_id.get(milestone_id)
            if detail_path is not None:
                label = f"Milestone: [{milestone['title']}](milestones/{detail_path.name})"
            else:
                label = f"Milestone: {milestone['title']}"
            due_items.setdefault(due_iso, []).append(label)

        for homework in self.homework_due_dates():
            due_iso = str(homework.get("due_iso", ""))
            if not due_iso:
                continue
            due_items.setdefault(due_iso, []).append(f"Homework: {homework['title']}")

        for repo in (self.content.get("assignment_repositories") or []):
            start_day = str(repo.get("start_day", ""))
            checkpoint = str(repo.get("checkpoint", "")).strip()
            repo_id = str(repo.get("id", "")).strip()
            repo_name = str(repo.get("name", "")).strip()
            start_assignment = assignment_by_day_id.get(start_day)
            if start_assignment is None or start_assignment.date is None:
                continue
            due_iso = iso_date(start_assignment.date)
            if not due_iso:
                continue

            if checkpoint:
                label = f"Checkpoint: {checkpoint}"
            else:
                label = "Assignment start"

            if repo_id:
                label = f"{label} ({repo_id})"
            if repo_name:
                label = f"{label} - {repo_name}"

            due_items.setdefault(due_iso, []).append(label)

        return due_items

    def write_milestone_files(
        self,
        milestones_dir: Path,
        milestones: list[dict[str, str | list[str]]],
    ) -> list[tuple[dict[str, str | list[str]], Path]]:
        milestones_dir.mkdir(parents=True, exist_ok=True)
        written: list[tuple[dict[str, str | list[str]], Path]] = []

        for milestone in milestones:
            milestone_id = str(milestone.get("id", "M00"))
            title = str(milestone.get("title", "Milestone"))
            file_name = f"{milestone_id}_{slugify(title)}.md"
            file_path = milestones_dir / file_name

            required_items = milestone.get("required_items") or []
            rubric = milestone.get("rubric") or []
            if not isinstance(required_items, list):
                required_items = []
            if not isinstance(rubric, list):
                rubric = []

            lines = [
                f"# {title}\n\n",
                "## Milestone Metadata\n",
                f"- Milestone ID: {milestone_id}\n",
                f"- Due date: {milestone['due_date']}\n",
                f"- Week: {milestone['week']}\n",
                f"- Focus: {milestone.get('focus', '')}\n",
                f"- Notes: {milestone['notes']}\n\n",
                "## Student Instructions (Draft)\n",
                "1. Follow the assignment repository instructions for this milestone.\n",
                "2. Commit your milestone work with clear messages.\n",
                "3. Submit repository evidence and short reflection as requested.\n\n",
                "## Required Submission Items\n",
            ]

            if required_items:
                for item in required_items:
                    lines.append(f"- [ ] {item}\n")
            else:
                lines.extend(
                    [
                        "- [ ] Repository link and branch/tag\n",
                        "- [ ] Evidence artifact(s)\n",
                        "- [ ] Short reflection note\n",
                    ]
                )

            lines.extend(["\n", "## Rubric (Draft)\n"])
            if rubric:
                for criterion in rubric:
                    lines.append(f"- [ ] {criterion}\n")
            else:
                lines.extend(
                    [
                        "- [ ] Completeness of required work\n",
                        "- [ ] Reproducibility evidence quality\n",
                        "- [ ] Code quality and documentation clarity\n",
                    ]
                )

            lines.extend(
                [
                    "\n",
                    "## Instructor Notes\n",
                    "- Common failure modes:\n",
                    "- Fast feedback points:\n",
                    "- Follow-up for next Tuesday project review:\n",
                ]
            )

            file_path.write_text("".join(lines), encoding="utf-8")
            written.append((milestone, file_path))

        return written

    def write_milestones_page(
        self,
        milestones_page_path: Path,
        milestone_files: list[tuple[dict[str, str | list[str]], Path]],
    ) -> None:
        lines = [
            "# Milestones\n",
            "\n",
            "| Milestone | Due Date | Focus | Instructions |\n",
            "| --- | --- | --- | --- |\n",
        ]

        for milestone, file_path in milestone_files:
            relative_link = f"milestones/{file_path.name}"
            lines.append(
                f"| {milestone['title']} | {milestone['due_date']} | {milestone.get('focus', '')} | [Open milestone]({relative_link}) |\n"
            )

        milestones_page_path.parent.mkdir(parents=True, exist_ok=True)
        milestones_page_path.write_text("".join(lines), encoding="utf-8")

    def day_topic_file_name(self, day_id: str) -> str:
        return f"{day_id}_Topic.md"

    def write_day_files(self, days_dir: Path, assignments: list[DayAssignment]) -> list[tuple[DayAssignment, Path]]:
        days_dir.mkdir(parents=True, exist_ok=True)
        written: list[tuple[DayAssignment, Path]] = []

        for assignment in assignments:
            filename = self.day_topic_file_name(assignment.entry.day_id)
            file_path = days_dir / filename
            date_text = format_date(assignment.date)
            week_text = self.week_number(assignment.date) or "TBD"
            studio_text = assignment.entry.studio or "None"
            note_text = assignment.note or ""
            project_review_line = ""
            if assignment.date is not None and assignment.date.strftime("%A") == "Tuesday":
                project_review_line = "4. Project review and checkpoint discussion (15-20 min)\n"
                wrap_up_line = "5. Debugging, discussion, and wrap-up (10-15 min)\n\n"
            else:
                wrap_up_line = "4. Debugging, discussion, and wrap-up (10-20 min)\n\n"

            text = (
                f"# {assignment.entry.title}\n\n"
                f"## Session Metadata\n"
                f"- Week: {week_text}\n"
                f"- Date: {date_text}\n"
                f"- Module: {assignment.entry.module}\n"
                f"- Status: {assignment.status}\n"
                f"- Studio Anchor: {studio_text}\n"
                f"- Notes: {note_text}\n\n"
                "## Day Agenda (Draft)\n"
                "1. Short lecture and framing (10-15 min)\n"
                "2. Assignment repository onboarding or progress check (10 min)\n"
                "3. In-class coding block (45-60 min)\n"
                f"{project_review_line}"
                f"{wrap_up_line}"
                "## Assignment Repository Link\n"
                "- Repo: TODO\n"
                "- Branch/tag for today: TODO\n"
                "- Checkpoint target: TODO\n\n"
                "## Evidence To Capture Today\n"
                "- Command(s) run:\n"
                "- Key output/result:\n"
                "- One challenge and fix:\n"
                "- Commit or issue link:\n"
            )
            file_path.write_text(text, encoding="utf-8")
            written.append((assignment, file_path))

        return written

    def write_schedule_page(
        self,
        schedule_path: Path,
        day_files: list[tuple[DayAssignment, Path]],
        milestone_files: list[tuple[dict[str, str | list[str]], Path]],
    ) -> None:
        due_items_by_iso = self.due_items_by_iso(day_files, milestone_files)

        lines = [
            f"# CMSE 802 Daily Schedule - {self.semester_name()}\n",
            "\n",
            "| Week | Date | Topic | Module | Due | Agenda |\n",
            "| --- | --- | --- | --- | --- | --- |\n",
        ]

        for assignment, file_path in day_files:
            relative_link = f"days/{file_path.name}"
            due_today = due_items_by_iso.get(iso_date(assignment.date), [])
            due_cell = "<br>".join(due_today) if due_today else "None"
            lines.append(
                f"| {self.week_number(assignment.date)} | {format_date(assignment.date)} | {assignment.entry.title} | {assignment.entry.module} | {due_cell} | [Open agenda]({relative_link}) |\n"
            )

        milestones = self.milestone_due_dates()
        if milestones:
            lines.extend(
                [
                    "\n",
                    "## Milestone Due Dates\n",
                    "\n",
                    "| Week | Due Date | Milestone | Notes | Details |\n",
                    "| --- | --- | --- | --- | --- |\n",
                ]
            )
            files_by_id = {str(m.get("id", "")): p for m, p in milestone_files}
            for milestone in milestones:
                milestone_id = str(milestone.get("id", ""))
                file_path = files_by_id.get(milestone_id)
                detail = ""
                if file_path is not None:
                    detail = f"[Open milestone](milestones/{file_path.name})"
                lines.append(
                    f"| {milestone['week']} | {milestone['due_date']} | {milestone['title']} | {milestone['notes']} | {detail} |\n"
                )

        if due_items_by_iso:
            lines.extend(
                [
                    "\n",
                    "## Chronological Due List\n",
                    "\n",
                    "| Date | Week | Due Item |\n",
                    "| --- | --- | --- |\n",
                ]
            )

            for due_iso in sorted(due_items_by_iso.keys()):
                due_date = datetime.strptime(due_iso, "%Y-%m-%d")
                week = self.week_number(due_date)
                for item in due_items_by_iso[due_iso]:
                    lines.append(f"| {format_date(due_date)} | {week} | {item} |\n")

        schedule_path.parent.mkdir(parents=True, exist_ok=True)
        schedule_path.write_text("".join(lines), encoding="utf-8")

    def write_jekyll_output(self, root_dir: Path) -> None:
        schedule_dir = root_dir / "Schedule"
        data_dir = root_dir / "_data"
        layouts_dir = root_dir / "_layouts"
        guide_dir = root_dir / "Guide"
        schedule_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)
        layouts_dir.mkdir(parents=True, exist_ok=True)
        guide_dir.mkdir(parents=True, exist_ok=True)

        assignments = self.day_assignments()
        milestone_rows = self.milestone_due_dates()

        schedule_source_dir = self.calendar_path.parent.parent / "Schedule"
        calendar_schedule_events, schedule_warnings, source_files = self._build_calendar_first_schedule_events(
            schedule_source_dir
        )

        # Copy source schedule markdown files so generated preview links resolve.
        for source_file in source_files:
            target_file = schedule_dir / source_file.name
            if source_file.resolve() != target_file.resolve():
                shutil.copy2(source_file, target_file)

        milestone_slug_by_id: dict[str, str] = {}
        for milestone in milestone_rows:
            milestone_id = str(milestone.get("id", "M00"))
            title = str(milestone.get("title", "Milestone"))
            milestone_slug_by_id[milestone_id] = f"{milestone_id}_{slugify(title)}"

        day_slug_by_id: dict[str, str] = {}
        for assignment in assignments:
            day_slug_by_id[assignment.entry.day_id] = f"{assignment.entry.day_id}_{slugify(assignment.entry.title)}"

        due_records: list[dict[str, str | None]] = []
        schedule_events: list[dict[str, str | None]] = list(calendar_schedule_events)

        for milestone in milestone_rows:
            due_iso = str(milestone.get("due_iso", ""))
            if not due_iso:
                continue
            due_dt = datetime.strptime(due_iso, "%Y-%m-%d")
            milestone_id = str(milestone.get("id", ""))
            milestone_slug = milestone_slug_by_id.get(milestone_id)
            milestone_url = f"/Schedule/{milestone_slug}" if milestone_slug else None

            due_records.append(
                {
                    "date": due_iso,
                    "week_start": self._week_start_iso_for(due_dt),
                    "title": str(milestone.get("title", "Milestone")),
                    "event_type": "milestone",
                    "url": milestone_url,
                }
            )
            schedule_events.append(
                {
                    "date": due_iso,
                    "week_start": self._week_start_iso_for(due_dt),
                    "title": f"MILESTONE {milestone['title']}",
                    "url": milestone_url,
                    "event_type": "milestone",
                    "day_id": None,
                    "module": None,
                }
            )

        for homework in self.homework_due_dates():
            due_iso = str(homework.get("due_iso", ""))
            if not due_iso:
                continue
            due_dt = datetime.strptime(due_iso, "%Y-%m-%d")
            due_records.append(
                {
                    "date": due_iso,
                    "week_start": self._week_start_iso_for(due_dt),
                    "title": str(homework.get("title", "Homework due")),
                    "event_type": "homework",
                    "url": None,
                }
            )
            schedule_events.append(
                {
                    "date": due_iso,
                    "week_start": self._week_start_iso_for(due_dt),
                    "title": str(homework.get("title", "Homework due")),
                    "url": None,
                    "event_type": "homework",
                    "day_id": None,
                    "module": None,
                }
            )

        for repo in (self.content.get("assignment_repositories") or []):
            start_day = str(repo.get("start_day", ""))
            checkpoint = str(repo.get("checkpoint", "")).strip()
            repo_id = str(repo.get("id", "")).strip()
            repo_name = str(repo.get("name", "")).strip()
            assignment = next((a for a in assignments if a.entry.day_id == start_day), None)
            if assignment is None or assignment.date is None:
                continue

            label = f"Checkpoint: {checkpoint}" if checkpoint else "Assignment start"
            if repo_id:
                label = f"{label} ({repo_id})"
            if repo_name:
                label = f"{label} - {repo_name}"

            date_iso = iso_date(assignment.date)
            due_records.append(
                {
                    "date": date_iso,
                    "week_start": self._week_start_iso_for(assignment.date),
                    "title": label,
                    "event_type": "checkpoint",
                    "url": None,
                }
            )

        due_records.sort(key=lambda entry: (str(entry.get("date", "")), str(entry.get("title", ""))))
        schedule_events.sort(key=lambda entry: (str(entry.get("date", "")), str(entry.get("title", ""))))

        due_by_date: dict[str, list[dict[str, str | None]]] = {}
        for record in due_records:
            due_by_date.setdefault(str(record.get("date", "")), []).append(record)

        for assignment in assignments:
            day_slug = day_slug_by_id[assignment.entry.day_id]
            date_iso = iso_date(assignment.date)
            due_lines: list[str] = []
            for due_item in due_by_date.get(date_iso, []):
                title = str(due_item.get("title", ""))
                url = due_item.get("url")
                event_type = str(due_item.get("event_type", "due")).capitalize()
                if url:
                    due_lines.append(f"- {event_type}: [{title}]({url})")
                else:
                    due_lines.append(f"- {event_type}: {title}")
            due_section = "\n".join(due_lines) if due_lines else "- None"

            day_text = (
                "---\n"
                "layout: schedule\n"
                f"title: \"{assignment.entry.title}\"\n"
                f"order: {day_number(assignment.entry.day_id)}\n"
                "mode: \"schedule\"\n"
                f"day_id: \"{assignment.entry.day_id}\"\n"
                f"date: \"{jekyll_date(assignment.date)}\"\n"
                f"module: \"{assignment.entry.module}\"\n"
                "---\n\n"
                f"# {assignment.entry.title}\n\n"
                "## Session Metadata\n"
                f"- Day: {assignment.entry.day_id}\n"
                f"- Date: {format_date(assignment.date)}\n"
                f"- Module: {assignment.entry.module}\n"
                f"- Status: {assignment.status}\n\n"
                "## Due Today\n"
                f"{due_section}\n\n"
                "## Agenda Notes\n"
                "- TODO\n"
            )
            (schedule_dir / f"{day_slug}.md").write_text(day_text, encoding="utf-8")

        for milestone in milestone_rows:
            milestone_id = str(milestone.get("id", "M00"))
            milestone_slug = milestone_slug_by_id[milestone_id]
            milestone_text = (
                "---\n"
                "layout: schedule\n"
                f"title: \"{milestone['title']}\"\n"
                f"order: {900 + int(''.join(ch for ch in milestone_id if ch.isdigit()) or '0')}\n"
                "mode: \"schedule\"\n"
                f"date: \"{str(milestone.get('due_iso', ''))}\"\n"
                "---\n\n"
                f"# {milestone['title']}\n\n"
                "## Milestone Metadata\n"
                f"- Milestone ID: {milestone_id}\n"
                f"- Due date: {milestone['due_date']}\n"
                f"- Week: {milestone['week']}\n"
                f"- Focus: {milestone.get('focus', '')}\n"
                f"- Notes: {milestone['notes']}\n\n"
                "## Student Instructions\n"
                "1. Follow the semester assignment instructions for this milestone.\n"
                "2. Commit milestone work with clear messages.\n"
                "3. Submit evidence and reflection notes.\n"
            )
            (schedule_dir / f"{milestone_slug}.md").write_text(milestone_text, encoding="utf-8")

        (data_dir / "schedule.yml").write_text(
            yaml.safe_dump(schedule_events, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )
        (data_dir / "due_items.yml").write_text(
            yaml.safe_dump(due_records, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )
        (data_dir / "schedule_events.yml").write_text(
            yaml.safe_dump(schedule_events, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )

        if schedule_warnings:
            warning_lines = ["# Schedule Filename Warnings", ""]
            warning_lines.extend(f"- {warning}" for warning in schedule_warnings)
            (root_dir / "SCHEDULE_WARNINGS.md").write_text("\n".join(warning_lines) + "\n", encoding="utf-8")

        index_lines = [
            "---\n",
            "layout: schedule\n",
            f"title: \"{self.semester_name()} Schedule\"\n",
            "order: 0\n",
            "mode: \"schedule\"\n",
            "is_schedule: true\n",
            "---\n\n",
            f"# {self.semester_name()} Schedule\n\n",
            "This schedule is generated from course content plus semester calendar configuration.\n\n",
            "## Due Dates in Chronological Order\n\n",
            "| Date | Type | Due Item |\n",
            "| --- | --- | --- |\n",
        ]

        for record in due_records:
            due_dt = datetime.strptime(str(record.get("date", "")), "%Y-%m-%d")
            item_title = str(record.get("title", ""))
            item_url = record.get("url")
            item_type = str(record.get("event_type", "due")).capitalize()
            if item_url:
                item_cell = f"[{item_title}]({item_url})"
            else:
                item_cell = item_title
            index_lines.append(f"| {format_date(due_dt)} | {item_type} | {item_cell} |\n")

        (schedule_dir / "index.md").write_text("".join(index_lines), encoding="utf-8")

        root_index = (
            "---\n"
            "layout: default\n"
            f"title: \"{self.semester_name()} Course Site\"\n"
            "---\n\n"
            f"# {self.semester_name()} Course Site\n\n"
            "This Jekyll preview is generated from the same semester calendar and content configuration used by the primary site pipeline.\n\n"
            "- [Schedule](./Schedule/)\n"
            "- [Guide](./Guide/)\n"
        )
        (root_dir / "index.md").write_text(root_index, encoding="utf-8")

        guide_index = (
            "---\n"
            "layout: guide\n"
            "title: \"Course Guide\"\n"
            "order: 1\n"
            "mode: \"guide\"\n"
            "---\n\n"
            "# Course Guide\n\n"
            "This is a lightweight guide placeholder for the shared CMSE template prototype.\n\n"
            "Use this section for reusable policies, weekly routines, and project workflow guidance.\n"
        )
        (guide_dir / "index.md").write_text(guide_index, encoding="utf-8")

        config_text = (
            "title: \"CMSE Course Template Preview\"\n"
            "description: \"Generated from course content and semester calendar configuration\"\n"
            "theme: jekyll-theme-minimal\n"
            "baseurl: \"\"\n"
        )
        (root_dir / "_config.yml").write_text(config_text, encoding="utf-8")

        gemfile_text = (
            "source \"https://rubygems.org\"\n\n"
            "gem \"jekyll\", \"~> 4.3\"\n"
            "gem \"jekyll-theme-minimal\"\n"
        )
        (root_dir / "Gemfile").write_text(gemfile_text, encoding="utf-8")

        publish_notes = (
            "# Jekyll Preview Publish Notes\n\n"
            "This folder is generated and intended for GitHub Pages style publishing.\n\n"
            "## Typical publish flow\n\n"
            "1. Commit this folder to the branch you use for site publishing.\n"
            "2. In repository settings, enable GitHub Pages from that branch (root folder).\n"
            "3. Push updates after rerunning generation.\n\n"
            "## Optional docs-folder publish flow\n\n"
            "1. From the repository root, run:\n"
            "   `make jekyll-semester-docs SEMESTER=fall`\n"
            "2. Commit and push the generated `docs/` folder.\n"
            "3. In repository settings, enable GitHub Pages from your branch using `/docs`.\n\n"
            "## Regenerate command\n\n"
            "From the main repository root:\n\n"
            "```bash\n"
            "make jekyll-semester-schedule SEMESTER=fall\n"
            "```\n\n"
            "or\n\n"
            "```bash\n"
            "make jekyll-semester-schedule SEMESTER=spring\n"
            "```\n"
        )
        (root_dir / "README_PUBLISH.md").write_text(publish_notes, encoding="utf-8")

        default_layout = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>{{ page.title | default: site.title }}</title>
  <style>
    body { font-family: Georgia, serif; margin: 0; background: #f6f8f7; color: #1f2522; }
    header { background: #ffffff; border-bottom: 1px solid #cfd8d3; padding: 0.9rem 1.2rem; }
    header a { margin-right: 1rem; color: #1f5c45; text-decoration: none; font-weight: 600; }
    .layout { display: grid; grid-template-columns: 18rem 1fr; gap: 1rem; max-width: 1200px; margin: 1rem auto; padding: 0 1rem; }
    aside { background: #ffffff; border: 1px solid #cfd8d3; border-radius: 10px; padding: 0.8rem; max-height: calc(100vh - 3rem); overflow: auto; }
    main { background: #ffffff; border: 1px solid #cfd8d3; border-radius: 10px; padding: 1rem; }
    .week-title { font-family: Arial, sans-serif; margin: 0.9rem 0 0.35rem; font-size: 0.95rem; color: #446255; }
    .sched-item { margin: 0.25rem 0; font-size: 0.9rem; line-height: 1.35; }
    .sched-item a { color: #1f5c45; text-decoration: none; }
    .sched-item a.active { font-weight: 700; text-decoration: underline; }
    @media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <a href=\"{{ '/' | relative_url }}\">Home</a>
    <a href=\"{{ '/Schedule/' | relative_url }}\">Schedule</a>
    <a href=\"{{ '/Guide/' | relative_url }}\">Guide</a>
  </header>
  {{ content }}
</body>
</html>
"""
        (layouts_dir / "default.html").write_text(default_layout, encoding="utf-8")

        schedule_layout = """---
layout: default
---
{% assign schedule_items = site.data.schedule | sort: "date" %}
<div class=\"layout\">
  <aside>
    {% assign current_week = "" %}
    {% for item in schedule_items %}
      {% if item.week_start != current_week %}
        {% assign current_week = item.week_start %}
        <div class=\"week-title\">Week of {{ item.week_start | date: "%b %-d" }}</div>
      {% endif %}
      <div class=\"sched-item\">
        {{ item.date | date: "%a %m/%d" }}:
        {% if item.url and item.url != "" %}
          <a href=\"{{ item.url | relative_url }}\" {% if item.url == page.url %}class=\"active\"{% endif %}>{{ item.title }}</a>
        {% else %}
          {{ item.title }}
        {% endif %}
      </div>
    {% endfor %}
  </aside>
  <main>
    {{ content }}
  </main>
</div>
"""
        (layouts_dir / "schedule.html").write_text(schedule_layout, encoding="utf-8")

        guide_layout = """---
layout: default
---
<div class=\"layout\">
  <aside>
    <div class=\"week-title\">Guide</div>
    <div class=\"sched-item\"><a href=\"{{ '/Guide/' | relative_url }}\">Guide Home</a></div>
    <div class=\"sched-item\"><a href=\"{{ '/Schedule/' | relative_url }}\">Schedule</a></div>
  </aside>
  <main>
    {{ content }}
  </main>
</div>
"""
        (layouts_dir / "guide.html").write_text(guide_layout, encoding="utf-8")

    def write_semester_assignments_page(
        self,
        semester_assignments_path: Path,
        milestone_files: list[tuple[dict[str, str | list[str]], Path]],
    ) -> None:
        repos = self.content.get("assignment_repositories") or []

        lines = [
            "# Semester Assignments\n",
            "\n",
            "Use these repositories and milestones for multi-day semester project work.\n",
            "\n",
            "## Assignment Repositories\n",
            "\n",
            "| ID | Repository | Start Date | Primary Checkpoint | Notes |\n",
            "| --- | --- | --- | --- | --- |\n",
        ]

        by_day_id = {assignment.entry.day_id: assignment for assignment in self.day_assignments()}

        if repos:
            for repo in repos:
                repo_id = repo.get("id", "")
                repo_name = repo.get("name", "")
                repo_url = repo.get("url", "")
                start_day = repo.get("start_day", "")
                checkpoint = repo.get("checkpoint", "")
                notes = repo.get("notes", "")
                start_assignment = by_day_id.get(start_day)
                start_date = format_date(start_assignment.date) if start_assignment else "TBD"

                if repo_url:
                    repo_cell = f"[{repo_name}]({repo_url})"
                else:
                    repo_cell = repo_name or "TODO"

                lines.append(f"| {repo_id} | {repo_cell} | {start_date} | {checkpoint} | {notes} |\n")
        else:
            lines.extend(
                [
                    "| A01 | TODO repo link | TBD | Checkpoint 01 | TODO |\n",
                    "| A02 | TODO repo link | TBD | Checkpoint 02 | TODO |\n",
                    "| A03 | TODO repo link | TBD | Checkpoint 03 | TODO |\n",
                    "| A04 | TODO repo link | TBD | Checkpoint 04 | TODO |\n",
                    "| A05 | TODO repo link | TBD | Checkpoint 05 | TODO |\n",
                ]
            )

        lines.extend(
            [
                "\n",
                "## Milestones\n",
                "\n",
                "| Milestone | Due Date | Focus | Instructions |\n",
                "| --- | --- | --- | --- |\n",
            ]
        )

        for milestone, file_path in milestone_files:
            lines.append(
                f"| {milestone['title']} | {milestone['due_date']} | {milestone.get('focus', '')} | [Open milestone](milestones/{file_path.name}) |\n"
            )

        semester_assignments_path.parent.mkdir(parents=True, exist_ok=True)
        semester_assignments_path.write_text("".join(lines), encoding="utf-8")

    def write_toc(
        self,
        toc_path: Path,
        day_files: list[tuple[DayAssignment, Path]],
        milestone_files: list[tuple[dict[str, str | list[str]], Path]],
    ) -> None:
        schedule_sections: list[dict[str, str]] = []

        for assignment, file_path in day_files:
            date_short = format_short_date(assignment.date)
            safe_title = re.sub(r"\s+", " ", assignment.entry.title).strip()
            display_title = f"{date_short}"
            if safe_title:
                display_title = f"{display_title}: {safe_title}"

            schedule_sections.append(
                {
                    "file": f"course_schedule/days/{file_path.name}",
                    "title": display_title,
                }
            )

        milestone_sections: list[dict[str, str]] = []
        for milestone, file_path in milestone_files:
            title = f"{milestone['due_short']}: {milestone['title']}"
            milestone_sections.append(
                {
                    "file": f"course_schedule/milestones/{file_path.name}",
                    "title": title,
                }
            )

        toc_data = {
            "format": "jb-book",
            "root": "intro",
            "parts": [
                {
                    "caption": "Schedule",
                    "numbered": False,
                    "chapters": [
                        {
                            "file": "course_schedule/Schedule.md",
                            "title": "Semester Schedule",
                            "sections": schedule_sections,
                        },
                        {
                            "file": "course_schedule/Semester_Assignments.md",
                            "title": "Semester Assignments",
                            "sections": [
                                {
                                    "file": "course_schedule/Milestones.md",
                                    "title": "Milestones Index",
                                },
                                *milestone_sections,
                            ],
                        },
                    ],
                },
                {
                    "caption": "Course Info",
                    "numbered": False,
                    "chapters": [
                        {"file": "course_documents/Syllabus/syllabus.md", "title": "Syllabus"},
                        {"file": "course_documents/AIPolicy/AIPolicy.md", "title": "AI Policy"},
                        {
                            "file": "course_documents/SoftwareSetup/SoftwareSetupGuide.md",
                            "title": "Software Setup",
                        },
                    ],
                },
                {
                    "caption": "Reference",
                    "numbered": False,
                    "chapters": [
                        {"file": "schedule.md", "title": "Topic Roadmap (Reference)"},
                        {"file": "software_studios.md", "title": "Software Studios (Reference)"},
                        {
                            "file": "course_schedule/Calendar_Logistics.md",
                            "title": "Calendar and Logistics (Reference)",
                        },
                    ],
                },
            ],
        }

        toc_text = "# Table of contents\n\n" + yaml.safe_dump(toc_data, sort_keys=False, allow_unicode=False)
        toc_path.write_text(toc_text, encoding="utf-8")

    def run(
        self,
        days_dir: Path,
        schedule_path: Path,
        semester_assignments_path: Path,
        milestones_dir: Path,
        milestones_page_path: Path,
        toc_path: Path,
    ) -> None:
        assignments = self.day_assignments()
        day_files = self.write_day_files(days_dir, assignments)
        milestone_files = self.write_milestone_files(milestones_dir, self.milestone_due_dates())
        self.write_milestones_page(milestones_page_path, milestone_files)
        self.write_schedule_page(schedule_path, day_files, milestone_files)
        self.write_semester_assignments_page(semester_assignments_path, milestone_files)
        self.write_toc(toc_path, day_files, milestone_files)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate schedule-first course site pages.")
    parser.add_argument("--calendar", required=True, help="Path to semester calendar YAML")
    parser.add_argument("--content", required=True, help="Path to course content YAML")
    parser.add_argument(
        "--days-dir",
        default="course_schedule/days",
        help="Output directory for DayXX files",
    )
    parser.add_argument(
        "--schedule-page",
        default="course_schedule/Schedule.md",
        help="Output markdown path for schedule index",
    )
    parser.add_argument(
        "--semester-assignments-page",
        "--repos-page",
        dest="semester_assignments_page",
        default="course_schedule/Semester_Assignments.md",
        help="Output markdown path for semester assignments index",
    )
    parser.add_argument(
        "--milestones-dir",
        default="course_schedule/milestones",
        help="Output directory for milestone markdown files",
    )
    parser.add_argument(
        "--milestones-page",
        default="course_schedule/Milestones.md",
        help="Output markdown path for milestone index",
    )
    parser.add_argument(
        "--toc",
        default="_toc.yml",
        help="Path to output Jupyter Book TOC YAML",
    )
    parser.add_argument(
        "--output-format",
        choices=["jupyter-book", "jekyll"],
        default="jupyter-book",
        help="Output format to generate",
    )
    parser.add_argument(
        "--jekyll-root",
        default="jekyll_preview",
        help="Root folder for generated Jekyll output when --output-format=jekyll",
    )

    args = parser.parse_args()

    generator = ScheduleSiteGenerator(Path(args.calendar), Path(args.content))
    if args.output_format == "jekyll":
        generator.write_jekyll_output(Path(args.jekyll_root))
        print(f"Generated Jekyll schedule output under {args.jekyll_root}.")
    else:
        generator.run(
            days_dir=Path(args.days_dir),
            schedule_path=Path(args.schedule_page),
            semester_assignments_path=Path(args.semester_assignments_page),
            milestones_dir=Path(args.milestones_dir),
            milestones_page_path=Path(args.milestones_page),
            toc_path=Path(args.toc),
        )

        print("Generated day agenda files, schedule index, semester assignments, milestones, and TOC.")


if __name__ == "__main__":
    main()
