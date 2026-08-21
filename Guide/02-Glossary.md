---
layout: guide
title: "Template Glossary"
order: 2
mode: "guide"
---
# Template Glossary

This page defines the core concepts used throughout the template so future instructors can adapt it without reading the code first.

## Guide

The `Guide/` folder is for stable reference material. Use it for policies, procedures, expectations, onboarding steps, and content that should not be tied to a specific date in the semester.

## Schedule

The `Schedule/` folder is for date-specific teaching content. Each file usually corresponds to a class meeting, a workshop, a lab, or a major instruction point in the semester.

## Calendar

The semester calendar is defined in files such as `config/fall_calendar.yml` or `config/spring_calendar.yml`. These files control the date structure used to build the schedule timeline.

## Schedule filename convention

Files in `Schedule/` should follow a naming pattern such as:

- `01-class-welcome.md`
- `02-same-lab-review.md`
- `03-plus-1-guest-speaker.md`
- `05-next-thu-worksheet.md`

The generator uses these conventions to determine where a page should appear in the semester timeline.

## `publish: false` and `published: false`

If a schedule page should exist in the repository but not appear as a clickable link in the generated website, add one of the following in the front matter:

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

When this is set, the generator still keeps the entry in the source files, but the URL is set to `null` so it is not clickable in the site navigation.

## Generated schedule data

The script `scripts/update_schedule.py` writes the generated schedule YAML into:

- `_data/schedule.yml`
- `_data/schedule_warnings.yml`
- `course_calendar.ics`

This generated data should be treated as derived output, not the canonical content source.

## `TBD` entries

If a schedule file is missing for a class day, the generator inserts a `TBD` item in the timeline rather than failing the build. This is helpful for early planning and keeps the structure visible before all class pages are prepared.

## Front matter

A schedule page often includes front matter such as:

```yaml
---
layout: schedule
date: 2026-09-01
---
```

The front matter makes the file compatible with Jekyll and allows the site to interpret the page as a schedule entry.

## Workflow artifact

The template is intentionally built so that a future instructor can view the site as a clear operating manual for the repository itself. The site is not meant to be hidden behind a complex custom build process; it is meant to be transparent and straightforward to maintain.
