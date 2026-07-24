# Schedule Filename Convention

This template uses the filenames in the `Schedule` folder to define course pacing.

The goal is that an instructor can run `ls Schedule` and immediately see the instructional flow of the semester in order, without needing to manually maintain schedule dates in a separate file.

## Core Rule

The leading two-digit number is the course-day anchor.

- `01` means the first instructional meeting.
- `02` means the second instructional meeting.
- `03` means the third instructional meeting.

The actual calendar date for each numbered course day is computed from the selected `config/[semester]_calendar.yml` file.

The website should show real dates, not the course-day number.

## What Goes in `Schedule`

Use the `Schedule` folder for course content that should stay attached to the instructional pacing of the course.

Examples:

- class meeting pages
- homework due dates
- project checkpoints
- quizzes
- readings tied to a class day

## What Stays in `config/[semester]_calendar.yml`

Use the semester calendar file for dates that are about the institution or the semester itself rather than course content.

Examples:

- first and last day of the semester
- meeting days such as Tuesday and Thursday
- holidays
- fall break or spring break
- cancelled classes
- snow days
- manual date overrides

## Filename Grammar

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

- `NN` is the instructional meeting number.
- `class` means the item lands on that class meeting date.

### 2. Same-day items

Pattern:

```text
NN-same-topic-slug.md
```

Examples:

```text
05-same-reading-quiz.md
10-same-project-checkpoint.md
```

Meaning:

- The item happens on the same calendar date as class day `NN`.
- Use this when an event is tied to the same day but is not the main class page.

### 3. Calendar-day offsets

Pattern:

```text
NN-plus-D-topic-slug.md
```

Examples:

```text
06-plus-2-homework-1.md
12-plus-5-reflection.md
```

Meaning:

- Start from class day `NN`.
- Move forward `D` calendar days.
- Use this for due dates such as "two days after Day 06."

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
06-next-sun-homework-1.md
08-next-fri-lab-checkpoint.md
```

Meaning:

- Start from class day `NN`.
- Find the first named weekday strictly after that class date.
- Use this for patterns such as "the following Sunday after class day 06."

## Sorting Behavior

These filenames are designed to sort cleanly in directory listings.

Examples:

```text
01-class-welcome.md
01-same-syllabus-quiz.md
01-next-sun-homework-1.md
02-class-version-control.md
02-plus-2-reading-response.md
03-class-project-selection.md
```

This keeps all items associated with course day `01` together, then all items associated with course day `02`, and so on.

## Recommended Interpretation Rules

The schedule-generation script should interpret filenames as follows:

1. `NN-class-*` maps to the calendar date of course day `NN`.
2. `NN-same-*` maps to the same calendar date as course day `NN`.
3. `NN-plus-D-*` maps to `D` calendar days after course day `NN`.
4. `NN-next-WDAY-*` maps to the first matching weekday after course day `NN`.

The generated `_data/schedule.yml` file should then merge these items with non-class events defined in the semester calendar file.

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

For simplicity, keep a single source branch and publish from the `docs/` folder:

1. Authoring source remains at repository root.
2. Build output is generated into `docs/`.
3. GitHub Pages is configured to publish from `main` branch, `docs/` folder.

Why this is the default recommendation:

- It keeps source and published artifacts separated.
- It avoids additional branch management overhead.
- It stays transparent for instructors who are not Git experts.

Alternative publishing models (separate branch or ghp-import) can be added later if the project needs stricter separation, but `main + docs/` is usually the best balance of portability and simplicity for course teams.

## Notes

- Do not encode holidays or snow days as `Schedule` files unless they are actual course content items.
- Prefer filename-based pacing for instructor-authored content and calendar YAML for institutional constraints.