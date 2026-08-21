---
layout: guide
title: "Instructor Quick Start"
order: 1
mode: "guide"
---
# Instructor Quick Start

This page is the fastest way to get a new course website launched from this template.

## 1. Customize the site metadata

Edit `_config.yml` first. Update the site title, description, base URL, and any other metadata that should reflect your course or unit.

## 2. Replace the landing page

Edit `index.md` so it reflects your course rather than the template placeholder. Keep the homepage short and useful: course description, links to the guide, and a current calendar preview.

## 3. Replace the guide pages

The `Guide/` directory is meant for instructions that do not change every week. Replace the template files with your course's syllabus, policies, logistics, and references.

The default files are placeholders and can be fully replaced with course-specific content.

## 4. Replace the schedule pages

The `Schedule/` directory holds date-specific class pages. These pages are the place for agendas, reading, in-class activities, assignments, and preparation notes.

Each schedule file should have a meaningful filename and a front-matter date that matches the generated semester calendar.

## 5. Set the calendar dates

Update one of:

- `config/fall_calendar.yml`
- `config/spring_calendar.yml`

Use these files to set the semester start/end dates, class meeting pattern, and any special schedule adjustments.

## 6. Generate the schedule data

From the repository root, run:

```bash
make schedule-fall
```

or

```bash
make schedule-spring
```

This generates:

- `_data/schedule.yml`
- `_data/schedule_warnings.yml`
- `course_calendar.ics`

## 7. Preview locally

Use the local preview workflow before publishing:

```bash
make serve
```

or build directly:

```bash
make build-site
```

## 8. Publish

Once the content looks correct, commit the files and publish the repository using your normal GitHub Pages or static-hosting process.

## Recommended Workflow for Future Semesters

1. Update the calendar.
2. Add or rename `Schedule/` files.
3. Refresh the guide.
4. Regenerate schedule output.
5. Review warnings.
6. Publish.

This flow keeps the site data consistent with the course calendar and reduces manual maintenance.

## Example naming patterns

A few examples make the pattern easier to understand when you are first setting up a term:

- `03-same-reflection.md` for a short activity on the same day as class 03
- `03-plus-2-project-checkpoint.md` for a due date two days after class 03
- `03-next-sun-example.md` for a due date that falls on the first Sunday after class 03

The key idea is that the file name tells the generator when the item belongs in the semester timeline without requiring you to hand-enter every date.


