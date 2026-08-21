# Course Website Template

This repository is a schedule-first course website template designed for instructors who want a maintainable, reproducible course site without hand-maintaining the semester timeline.

## Purpose of this template

The template exists to help instructors:

- keep the course calendar and page content aligned
- generate schedule data automatically from markdown files
- create a simple guide and schedule structure for students
- publish a course website without custom build complexity

## First-time instructor checklist

1. Update site metadata in `_config.yml`.
   - set the site title, description, and base URL
   - confirm the course branding or logo path
2. Replace the template landing page in `index.md`.
3. Update the guide pages in `Guide/`.
4. Update the schedule files in `Schedule/`.
5. Set the semester dates in `config/fall_calendar.yml` or `config/spring_calendar.yml`.
6. Run the generator and review warnings before publishing.

## Quick start

1. Open the semester calendar file:
   - `config/fall_calendar.yml`
   - or `config/spring_calendar.yml`
2. Add or rename schedule files in `Schedule/` using the naming patterns described in `Instructors/Schedule_Filename_Convention.md`.
3. Generate the site data:

```bash
make schedule-fall
```

or

```bash
make schedule-spring
```

4. Preview locally:

```bash
make serve
```

5. Publish when the site is ready.

## What the generator produces

Running a schedule target executes `scripts/update_schedule.py` and creates:

- `_data/schedule.yml`
- `_data/schedule_warnings.yml`
- `course_calendar.ics`

This is the generated output that the site uses for timeline rendering and calendar export.

## Core workflow

The template is intentionally simple:

- the calendar defines semester dates
- the schedule folder defines class-by-class content
- the guide folder holds stable reference material
- the generator assembles the public schedule and calendar data

## Local development

Create or update the environment:

```bash
make envs
```

Install the Ruby dependencies:

```bash
make bundle-install
```

Serve locally:

```bash
make serve
```

Build static output:

```bash
make build-site
```

## Optional pre-push check

This template can also run a reminder check before push:

```bash
make install-hooks
```

This helps ensure generated files are kept in sync before a publish.

## Recommended publishing workflow

1. update the semester calendar
2. update class files in `Schedule/`
3. regenerate schedule data
4. review warnings
5. preview locally
6. commit the source and generated files together
7. publish the site

## Notes for template authors and instructors

- Use `Guide/` for stable pages such as policies, logistics, and reference material.
- Use `Schedule/` for date-specific course content.
- Keep generated output in sync with source content.
- Treat `TBD` as a placeholder when a class file is not yet ready.
- Use `publish: false` or `published: false` to keep a page in the repo without making it clickable.

## Dependencies

- Python 3
- Conda or an equivalent environment manager
- Ruby/Bundler for Jekyll
- Jekyll via the repository's `Gemfile`
- `pyyaml` and related Python tooling for schedule generation

