#!/usr/bin/env python3
"""Generate topic roadmap, software studios, and calendar logistics pages.

Single source of truth:
- config/topics_per_day.yml (course content)
- config/[semester]_calendar.yml (dates and semester adjustments)
"""

from __future__ import annotations

import argparse
import re
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
    """Extract a human-readable title from markdown content."""

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


class ScheduleUpdater:
    def __init__(self, calendar_path: str, content_path: str):
        with open(calendar_path, "r", encoding="utf-8") as handle:
            self.calendar = yaml.safe_load(handle) or {}
        with open(content_path, "r", encoding="utf-8") as handle:
            self.content = yaml.safe_load(handle) or {}

    def _semester_name(self) -> str:
        return self.calendar.get("semester_info", {}).get("name", "Semester")

    def _first_day(self) -> datetime:
        return datetime.strptime(self.calendar["semester_info"]["first_day"], "%Y-%m-%d")

    def _last_day(self) -> datetime:
        return datetime.strptime(self.calendar["semester_info"]["last_day"], "%Y-%m-%d")

    def _meeting_days(self) -> list[str]:
        semester_days = self.calendar.get("semester_info", {}).get("meeting_days")
        class_days = self.calendar.get("class_days")
        return list(semester_days or class_days or ["Tuesday", "Thursday"])

    def _break_ranges(self) -> list[tuple[datetime, datetime]]:
        break_ranges: list[tuple[datetime, datetime]] = []
        for info in (self.calendar.get("breaks") or {}).values():
            if "date" in info:
                day = datetime.strptime(info["date"], "%Y-%m-%d")
                break_ranges.append((day, day))
            elif "start" in info and "end" in info:
                start = datetime.strptime(info["start"], "%Y-%m-%d")
                end = datetime.strptime(info["end"], "%Y-%m-%d")
                break_ranges.append((start, end))

        for cancelled_class in self.calendar.get("schedule_adjustments", {}).get("cancelled_classes", []):
            cancelled_date = datetime.strptime(cancelled_class["date"], "%Y-%m-%d")
            break_ranges.append((cancelled_date, cancelled_date))

        return break_ranges

    def _is_break(self, day: datetime) -> bool:
        for start, end in self._break_ranges():
            if start <= day <= end:
                return True
        return False

    def _meeting_dates(self) -> list[datetime]:
        current_day = self._first_day()
        last_day = self._last_day()
        meeting_days = set(self._meeting_days())

        dates: list[datetime] = []
        while current_day <= last_day:
            if current_day.strftime("%A") in meeting_days and not self._is_break(current_day):
                dates.append(current_day)
            current_day += timedelta(days=1)
        return dates

    def _day_number(self, day_id: str) -> int:
        digits = "".join(ch for ch in day_id if ch.isdigit())
        return int(digits) if digits else 0

    def _ordered_day_entries(self) -> list[DayEntry]:
        entries: list[DayEntry] = []
        days = self.content.get("days") or {}
        for day_id in sorted(days, key=self._day_number):
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

    def _module_order(self) -> dict[str, int]:
        module_map = self.content.get("modules") or {}
        return {
            module_name: module_info.get("order", index)
            for index, (module_name, module_info) in enumerate(module_map.items(), start=1)
        }

    def _week_number(self, day: datetime) -> int:
        return ((day - self._first_day()).days // 7) + 1

    def _format_date(self, day: datetime) -> str:
        return f"{day.strftime('%A')}, {day.strftime('%B')} {day.day}, {day.year}"

    def _day_overrides(self) -> dict[str, dict[str, Any]]:
        return self.calendar.get("schedule_adjustments", {}).get("day_overrides", {}) or {}

    def _assignment_for_day(self, day_entry: DayEntry, automatic_dates: list[datetime]) -> DayAssignment:
        override = self._day_overrides().get(day_entry.day_id, {})
        status = override.get("status", day_entry.status)
        note = override.get("note", "")

        if override.get("date"):
            date = datetime.strptime(override["date"], "%Y-%m-%d")
            return DayAssignment(entry=day_entry, date=date, status=status, note=note)

        if automatic_dates:
            return DayAssignment(entry=day_entry, date=automatic_dates.pop(0), status=status, note=note)

        return DayAssignment(entry=day_entry, date=None, status=status, note=note)

    def _day_assignments(self) -> list[DayAssignment]:
        meeting_dates = self._meeting_dates()
        override_dates = {
            datetime.strptime(override["date"], "%Y-%m-%d")
            for override in self._day_overrides().values()
            if override.get("date")
        }
        automatic_dates = [day for day in meeting_dates if day not in override_dates]
        return [self._assignment_for_day(day_entry, automatic_dates) for day_entry in self._ordered_day_entries()]

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

    def _calendar_non_class_events(self) -> list[dict[str, str | None]]:
        events: list[dict[str, str | None]] = []

        for break_name, info in (self.calendar.get("breaks") or {}).items():
            description = str(info.get("description") or break_name.replace("_", " ").title())

            if "date" in info:
                day = datetime.strptime(info["date"], "%Y-%m-%d")
                events.append(
                    {
                        "date": day.strftime("%Y-%m-%d"),
                        "week_start": self._week_start_iso_for(day),
                        "title": description,
                        "url": None,
                        "event_type": "non_class",
                        "day_id": None,
                        "module": None,
                    }
                )
                continue

            if "start" in info and "end" in info:
                start = datetime.strptime(info["start"], "%Y-%m-%d")
                end = datetime.strptime(info["end"], "%Y-%m-%d")
                cursor = start
                while cursor <= end:
                    events.append(
                        {
                            "date": cursor.strftime("%Y-%m-%d"),
                            "week_start": self._week_start_iso_for(cursor),
                            "title": description,
                            "url": None,
                            "event_type": "non_class",
                            "day_id": None,
                            "module": None,
                        }
                    )
                    cursor += timedelta(days=1)

        return events

    def build_schedule_events_from_files(
        self,
        schedule_dir: Path,
    ) -> tuple[list[dict[str, str | None]], list[str]]:
        """Build timeline events from computed class slots plus Schedule filenames."""

        parsed_items, parse_warnings = parse_schedule_directory(schedule_dir)
        warnings: list[str] = [f"{w.file_path.name}: {w.message}" for w in parse_warnings]

        class_dates = self._meeting_dates()
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
                        "date": class_date.strftime("%Y-%m-%d"),
                        "week_start": self._week_start_iso_for(class_date),
                        "title": "TBD",
                        "url": None,
                        "event_type": "class",
                        "day_id": f"Day{index:02d}",
                        "module": None,
                    }
                )
            else:
                title = markdown_title_for_file(class_item.file_path)
                events.append(
                    {
                        "date": class_date.strftime("%Y-%m-%d"),
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
                    "date": target_date.strftime("%Y-%m-%d"),
                    "week_start": self._week_start_iso_for(target_date),
                    "title": title,
                    "url": f"/Schedule/{item.file_path.stem}",
                    "event_type": item.relation,
                    "day_id": f"Day{item.anchor_day:02d}",
                    "module": None,
                }
            )

        events.extend(self._calendar_non_class_events())
        events.sort(key=lambda entry: (str(entry.get("date", "")), str(entry.get("title", ""))))
        return events, warnings

    def _group_by_module(self) -> dict[str, list[DayAssignment]]:
        grouped: dict[str, list[DayAssignment]] = {}
        for assignment in self._day_assignments():
            grouped.setdefault(assignment.entry.module, []).append(assignment)
        return grouped

    def _week_window(self, assignments: list[DayAssignment]) -> str:
        week_numbers = sorted({self._week_number(a.date) for a in assignments if a.date is not None})
        if not week_numbers:
            return "TBD"
        if len(week_numbers) == 1:
            return f"Week {week_numbers[0]}"
        return f"Weeks {week_numbers[0]}-{week_numbers[-1]}"

    def _build_topic_roadmap_lines(self, calendar_path: str) -> list[str]:
        grouped = self._group_by_module()
        module_order = self._module_order()
        modules = self.content.get("modules") or {}
        threads = self.content.get("course_threads") or []

        lines = [
            f"# CMSE 802 Topic Roadmap - {self._semester_name()}\n",
            "\n",
            f"This page is generated from `config/topics_per_day.yml` and `{calendar_path}`.\n",
            "\n",
            "This is the primary planning page: topics and learning goals are the anchor, while dates are logistical context.\n",
            "\n",
            "## Course Threads\n",
            "\n",
        ]

        for thread in threads:
            lines.append(f"- {thread}\n")
        lines.append("\n")

        lines.extend([
            "## Module Overview\n",
            "\n",
            "| Module | Week Window | Focus | Flexibility | Planned Meetings |\n",
            "| --- | --- | --- | --- | --- |\n",
        ])

        for module_name in sorted(grouped, key=lambda name: module_order.get(name, 999)):
            module_info = modules.get(module_name, {})
            focus = module_info.get("focus", "")
            flexibility = module_info.get("flexibility", "")
            assignments = grouped[module_name]
            lines.append(
                f"| {module_name} | {self._week_window(assignments)} | {focus} | {flexibility} | {len(assignments)} |\n"
            )
        lines.append("\n")

        for module_name in sorted(grouped, key=lambda name: module_order.get(name, 999)):
            module_info = modules.get(module_name, {})
            goals = module_info.get("learning_goals", [])
            lines.append(f"## {module_name}\n")
            lines.append("\n")
            if module_info.get("focus"):
                lines.append(f"Focus: {module_info['focus']}\n")
                lines.append("\n")
            if goals:
                lines.append("Learning goals:\n")
                for goal in goals:
                    lines.append(f"- {goal}\n")
                lines.append("\n")

            lines.append("Planned sessions:\n")
            lines.append("\n")
            lines.append("| Day | Topic | Calendar Slot | Studio Anchor |\n")
            lines.append("| --- | --- | --- | --- |\n")
            for assignment in grouped[module_name]:
                slot = self._format_date(assignment.date) if assignment.date else "TBD"
                studio_label = assignment.entry.studio or ""
                lines.append(
                    f"| {assignment.entry.day_id} | {assignment.entry.title} | {slot} | {studio_label} |\n"
                )
            lines.append("\n")

        lines.extend([
            "## Flexibility Policy\n",
            "\n",
            "If calendar changes occur (closures, cancellations, pacing shifts), update only the calendar file or day overrides. Topic and module intent should remain stable unless there is an explicit curriculum decision to change it.\n",
        ])

        return lines

    def _build_studio_lines(self, calendar_path: str) -> list[str]:
        studios = self.content.get("studios") or {}
        assignments = self._day_assignments()

        studio_to_days: dict[str, list[DayAssignment]] = {}
        for assignment in assignments:
            if assignment.entry.studio:
                studio_to_days.setdefault(assignment.entry.studio, []).append(assignment)

        lines = [
            f"# Software Engineering Studios - {self._semester_name()}\n",
            "\n",
            f"This page is generated from `config/topics_per_day.yml` and `{calendar_path}`.\n",
            "\n",
            "Studios are short, project-integrated software engineering assignments that run alongside modeling content.\n",
            "\n",
            "| Studio | Title | Suggested Timing | Required Artifact | Optional Extension |\n",
            "| --- | --- | --- | --- | --- |\n",
        ]

        for studio_id in sorted(studios, key=self._day_number):
            studio = studios[studio_id] or {}
            anchored = studio_to_days.get(studio_id, [])
            if anchored:
                labels = []
                for assignment in anchored:
                    if assignment.date:
                        labels.append(f"{assignment.entry.day_id} ({self._format_date(assignment.date)})")
                    else:
                        labels.append(assignment.entry.day_id)
                timing = "; ".join(labels)
            else:
                timing = "TBD"

            lines.append(
                f"| {studio_id} | {studio.get('title', '')} | {timing} | {studio.get('required_artifact', '')} | {studio.get('optional_extension', '')} |\n"
            )

        lines.append("\n")

        for studio_id in sorted(studios, key=self._day_number):
            studio = studios[studio_id] or {}
            threads = studio.get("threads", [])
            lines.append(f"## {studio_id}: {studio.get('title', '')}\n")
            lines.append("\n")
            if threads:
                lines.append("Thread coverage:\n")
                for thread in threads:
                    lines.append(f"- {thread}\n")
                lines.append("\n")

        return lines

    def _build_calendar_lines(self, calendar_path: str) -> list[str]:
        assignments = self._day_assignments()

        lines = [
            f"# Calendar and Meeting Logistics - {self._semester_name()}\n",
            "\n",
            f"This page is generated from `config/topics_per_day.yml` and `{calendar_path}`.\n",
            "\n",
            "Use this page for dates and operational status. Use the Topic Roadmap page for instructional planning.\n",
            "\n",
            "| Week | Date | Day | Module | Topic | Studio | Status | Notes |\n",
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n",
        ]

        for assignment in assignments:
            if assignment.date is None:
                week = ""
                date_text = "TBD"
            else:
                week = str(self._week_number(assignment.date))
                date_text = self._format_date(assignment.date)

            lines.append(
                f"| {week} | {date_text} | {assignment.entry.day_id} | {assignment.entry.module} | {assignment.entry.title} | {assignment.entry.studio} | {assignment.status} | {assignment.note} |\n"
            )

        lines.append("\n")
        return lines

    def update_schedule(
        self,
        calendar_path: str,
        roadmap_path: str = "schedule.md",
        studios_path: str = "software_studios.md",
        calendar_logistics_path: str = "course_schedule/Calendar_Logistics.md",
        schedule_dir: str = "Schedule",
        schedule_data_path: str = "_data/schedule.yml",
        schedule_warnings_path: str = "_data/schedule_warnings.yml",
    ) -> None:
        Path(roadmap_path).write_text("".join(self._build_topic_roadmap_lines(calendar_path)), encoding="utf-8")
        Path(studios_path).write_text("".join(self._build_studio_lines(calendar_path)), encoding="utf-8")

        logistics_file = Path(calendar_logistics_path)
        logistics_file.parent.mkdir(parents=True, exist_ok=True)
        logistics_file.write_text("".join(self._build_calendar_lines(calendar_path)), encoding="utf-8")

        events, warnings = self.build_schedule_events_from_files(Path(schedule_dir))
        schedule_data_file = Path(schedule_data_path)
        schedule_data_file.parent.mkdir(parents=True, exist_ok=True)
        schedule_data_file.write_text(
            yaml.safe_dump(events, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )

        warning_rows = [{"warning": warning} for warning in warnings]
        warnings_file = Path(schedule_warnings_path)
        warnings_file.parent.mkdir(parents=True, exist_ok=True)
        warnings_file.write_text(
            yaml.safe_dump(warning_rows, sort_keys=False, allow_unicode=False),
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Update CMSE 802 planning pages from config")
    parser.add_argument("--calendar", required=True, help="Path to semester calendar YAML file")
    parser.add_argument("--content", required=True, help="Path to course content YAML file")
    parser.add_argument("--roadmap", default="schedule.md", help="Path to generated topic roadmap markdown file")
    parser.add_argument("--studios", default="software_studios.md", help="Path to generated studio plan markdown file")
    parser.add_argument(
        "--calendar-logistics",
        default="course_schedule/Calendar_Logistics.md",
        help="Path to generated calendar logistics markdown file",
    )
    parser.add_argument(
        "--schedule-dir",
        default="Schedule",
        help="Directory containing Schedule markdown files using NN-* filename convention",
    )
    parser.add_argument(
        "--schedule-data",
        default="_data/schedule.yml",
        help="Path to generated schedule YAML used by the website",
    )
    parser.add_argument(
        "--schedule-warnings",
        default="_data/schedule_warnings.yml",
        help="Path to generated warnings YAML for filename/schedule mismatches",
    )

    args = parser.parse_args()

    updater = ScheduleUpdater(args.calendar, args.content)
    updater.update_schedule(
        calendar_path=args.calendar,
        roadmap_path=args.roadmap,
        studios_path=args.studios,
        calendar_logistics_path=args.calendar_logistics,
        schedule_dir=args.schedule_dir,
        schedule_data_path=args.schedule_data,
        schedule_warnings_path=args.schedule_warnings,
    )

    print("Generated roadmap pages, calendar logistics, schedule data, and schedule warnings.")


if __name__ == "__main__":
    main()
