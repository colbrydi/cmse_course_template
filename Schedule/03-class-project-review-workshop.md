---
layout: schedule
date: '2026-09-08'
---

# Schedule File Conventions

This page documents the core file conventions that make the generated schedule work correctly.

## Core rule

Every file in `Schedule/` should match the naming pattern expected by the generator. That pattern allows the tool to infer the class day relationship and place the page correctly in the calendar.

## Common naming patterns

- `NN-class-name.md` for a primary class session
- `NN-same-name.md` for a page tied to the same class date
- `NN-plus-D-name.md` for an offset relative to the anchor date
- `NN-next-wed-name.md` for a date relative to the next weekday occurrence

## Recommended practice

Use names that clearly describe the session content and keep them stable across semesters. Avoid vague filenames such as `notes.md` or `review.md` if they will be used in the course timeline.

## Why this matters

The schedule generator reads the file names and builds the timeline automatically. If the names are inconsistent, the generator may insert `TBD` entries or produce warnings that are easy to miss.

## Instructor actions

- keep filenames consistent
- make sure each file has front matter with a valid `date`
- verify the schedule after renaming or moving files
- check the warning output before publishing

## Next step

Once the naming pattern is consistent, generate the schedule data and verify the rendered timeline visually.