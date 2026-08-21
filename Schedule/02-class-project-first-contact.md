---
layout: schedule
date: '2026-09-03'
---

# Course Calendar and Schedule Setup

This page is a reminder that the schedule is driven by the semester calendar and the file naming pattern in `Schedule/`.

## Session goals

- confirm the course timeline
- connect calendar dates to schedule files
- verify that the generated schedule matches the source structure

## What to check

Review the following before generating the schedule:

- calendar start and end dates
- meeting-day pattern
- holiday or break entries
- any special schedule adjustments
- whether schedule filenames reflect the intended timing

## Practical workflow

1. Update `config/fall_calendar.yml` or `config/spring_calendar.yml`.
2. Add or rename markdown files in `Schedule/`.
3. Run `make schedule-fall` or `make schedule-spring`.
4. Inspect `_data/schedule_warnings.yml` for problems.

A useful rule of thumb is that the schedule files describe when course activities happen, while the semester calendar defines when the semester itself is running.

## Files to review after each update

Before publishing, check the generated outputs:

- `_data/schedule.yml`
- `_data/schedule_warnings.yml`
- `course_calendar.ics`

This gives you a quick sanity check that the file naming conventions and class-date logic still line up.

## Instructor reminder

The schedule is not a manually maintained spreadsheet. The template expects the calendar and the file names to remain coordinated. If a class page is missing, the generator will insert a `TBD` placeholder rather than stop the build, which is useful during early planning but should be cleaned up before publication.

## Before the next step

- ensure the naming convention is being followed
- verify there are no duplicate class anchors
- check whether any draft pages should be hidden with `publish: false`