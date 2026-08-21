# Schedule Filename Convention

This document explains the naming rules that make the schedule system work. The schedule generator derives dates and links from the filenames in `Schedule/`, which keeps the semester timeline consistent without requiring every date to be entered manually.

## Core Rule

The leading two-digit number is the schedule anchor.

- `01` means the first instructional meeting
- `02` means the second instructional meeting
- `03` means the third instructional meeting

The actual calendar date for each item is computed from the selected `config/[semester]_calendar.yml` file. The website shows the real date, not the course-day number.

## Why this convention matters

The naming scheme lets an instructor look at the file list and immediately understand the instructional flow of the semester. It also allows the generator to build a timeline that includes class meetings, same-day assignments, later due dates, and weekday-based follow-ups.

## Instructor setup checklist

When starting a new course site from this template, the usual flow is:

1. Update `/_config.yml` with the course identity.
2. Set the semester dates in `config/fall_calendar.yml` or `config/spring_calendar.yml`.
3. Add schedule pages in `Schedule/`.
4. Add guide pages in `Guide/`.
5. Run the semester schedule generation command.
6. Review warnings and fix any filename or date mismatches.
7. Preview locally and publish.

## Calendar subscription file

This template generates `course_calendar.ics` from `_data/schedule.yml`.

- class events are exported as scheduled meetings
- non-class calendar entries are exported as all-day items
- a URL is included when a schedule item is published

Common commands:

- `make schedule-fall`
- `make schedule-spring`
- `make calendar-ics`

## What belongs in `Schedule`

Use `Schedule/` for course content that is tied to the pacing of the semester, such as:

- class meeting pages
- homework due dates
- workshop content
- project milestones
- reading or prep assignments tied to a date

## What belongs in `config/[semester]_calendar.yml`

Use the semester calendar file for dates that are about the institution or the semester itself, such as:

- first and last day of classes
- meeting days
- holidays
- breaks
- cancelled classes
- manual date overrides

## Filename grammar

Use lowercase, hyphen-separated filenames.

### 1. Class meetings

Pattern:

```text
NN-class-topic-slug.md
```

Examples:

```text
01-class-welcome.md
02-class-git-workflow.md
03-class-project-framing.md
```

Meaning:

- `NN` is the instructional meeting number
- `class` means the item is the primary page for that meeting

### 2. Same-day items

Pattern:

```text
NN-same-topic-slug.md
```

Examples:

```text
03-same-check-in.md
05-same-reading-quiz.md
```

Meaning:

- the item occurs on the same date as class day `NN`
- use this for due dates or activities attached to the same class day

### 3. Calendar-day offsets

Pattern:

```text
NN-plus-D-topic-slug.md
```

Examples:

```text
03-plus-2-project-checkpoint.md
12-plus-5-reflection.md
```

Meaning:

- start from class day `NN`
- move forward `D` calendar days
- useful for due dates that happen after class

### 4. Next weekday after a class day

Pattern:

```text
NN-next-WDAY-topic-slug.md
```

Where `WDAY` is one of:

```text
mon tue wed thu fri sat sun
```

Examples:

```text
03-next-sun-example.md
06-next-sun-homework-1.md
08-next-fri-lab-checkpoint.md
```

Meaning:

- start from class day `NN`
- find the first matching weekday strictly after that date
- useful when an assignment is intentionally due after a weekend or a specific weekday follow-up

### Example interpretation

A filename like `03-next-sun-example.md` means: "make this item land on the first Sunday after the third class meeting." That is a common pattern for short reflections, weekend check-ins, or peer-feedback tasks that should not be due on the same day as the class itself.

## Sorting behavior

These filenames are designed to sort cleanly in a directory list:

```text
01-class-welcome.md
01-same-syllabus-quiz.md
01-next-sun-homework-1.md
02-class-version-control.md
02-plus-2-reading-response.md
03-class-project-selection.md
```

This grouping makes it easy to review course flow by day.

## Recommended interpretation rules

The schedule-generation script interprets the filenames as follows:

1. `NN-class-*` maps to the calendar date of course day `NN`.
2. `NN-same-*` maps to the same calendar date as course day `NN`.
3. `NN-plus-D-*` maps to `D` calendar days after course day `NN`.
4. `NN-next-WDAY-*` maps to the first matching weekday after course day `NN`.

These generated entries are then merged with non-class events defined in the semester calendar file.

## Hidden or draft pages

If a page should remain in the repository but not be clickable in the public schedule, add either of these to the front matter:

```yaml
---
publish: false
---
```

or

```yaml
---
published: false
---
```

This is useful for draft pages, future lessons, and internal planning content.

## Missing Content and TBD Behavior

The schedule generator should always output all instructional class days computed from `config/[semester]_calendar.yml`, even when matching `Schedule` files do not exist yet.

If a class-day content file is missing:

- Include that date in `_data/schedule.yml`.
- Set a placeholder title such as `TBD`.
- Leave `url` empty or null.
- Keep the item visible on the website schedule.

When the instructor later adds the matching file and reruns the generator, the same schedule entry should automatically switch from `TBD` to the real title and link.

This supports a build-as-you-go workflow while preserving a complete semester calendar view for students.

## Mismatch Handling Rules

The generator should validate filename-to-calendar alignment and report warnings.

Recommended behavior:

1. Missing `NN-class-*` file for a computed class day:
	Generate a `TBD` class entry and warn.
2. Multiple `NN-class-*` files for the same anchor:
	Warn and use a deterministic tie-breaker (for example, lexical filename order) until resolved.
3. Anchor number larger than computed class-day count:
	Warn and skip, unless an explicit override is configured.
4. `NN-same-*`, `NN-plus-*`, or `NN-next-*` without a valid anchor day:
	Warn and skip.

Warnings should not fail the whole build by default; they should guide cleanup while still producing a usable website.

## Migration Workflow

The intended workflow for a new semester is:

1. Update `config/[semester]_calendar.yml`.
2. Reuse or adjust files in `Schedule`.
3. Run one schedule-generation command.
4. Regenerate `_data/schedule.yml` automatically.

This keeps instructional pacing in the `Schedule` folder while allowing semester dates to shift cleanly between terms.

## Repository and Publishing Structure Recommendation

For simplicity, keep a single source branch and publish from repository root:

1. Authoring source remains at repository root.
2. Generated schedule files remain in `_data/` and `course_calendar.ics`.
3. GitHub Pages is configured to publish from `main` branch, `root`.

Why this is the default recommendation:

- It keeps workflow simple for instructors using GitHub web edits.
- It avoids extra build-output folders and branch juggling.
- It aligns with this template's schedule-first generation flow.

## Notes

- Do not encode holidays or snow days as `Schedule` files unless they are actual course content items.
- Prefer filename-based pacing for instructor-authored content and calendar YAML for institutional constraints.