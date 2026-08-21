---
layout: guide
title: "Template Maintenance and Publishing"
order: 34
mode: "guide"
---
# Template Maintenance and Publishing

This page explains how to keep the template healthy once it is in use.

## Regenerating the schedule

Whenever the semester calendar or the schedule pages change, regenerate the derived site data:

```bash
make schedule-fall
```

or

```bash
make schedule-spring
```

This step updates the generated YAML files that feed the schedule and calendar widgets.

## What belongs where

Keep the semester structure clear by separating date-sensitive content from institutional calendar settings:

- Put teaching content in `Schedule/`: class meetings, labs, readings, homework, workshop notes, project milestones, and due dates tied to a specific class cycle.
- Put semester-wide dates in `config/fall_calendar.yml` or `config/spring_calendar.yml`: first and last day of classes, meeting days, holidays, breaks, cancellations, and any other institution-level timing information.

This separation keeps the calendar editable without rewriting each page manually, and it makes future adjustments easier to reason about.

## What to review before publishing

Check the generated outputs before you publish the site:

- `_data/schedule.yml`
- `_data/schedule_warnings.yml`
- `course_calendar.ics`

Warnings should be reviewed carefully. Missing or invalid files often indicate a naming mismatch or a calendar inconsistency rather than a problem with the site layout.

Good default commands are:

```bash
make schedule-fall
make schedule-spring
make calendar-ics
```

## Missing content and `TBD` behavior

The generator is designed to keep the semester visible even before every class page is complete.

If a class-day page is missing, the builder will still include that scheduled day in the generated timeline and use a placeholder such as `TBD` rather than fail the build. This is especially helpful in early planning when the course structure is known but the final content is still being drafted.

Review the warning file after each generation cycle to catch:

- missing `NN-class-*` files
- duplicate class anchors
- out-of-range anchor numbers
- filenames that do not match the expected convention

## Publishing workflow

A good default publishing pattern is:

1. update the calendar
2. update the schedule markdown files
3. regenerate the schedule data
4. preview the site locally
5. commit the source and generated files together
6. publish to GitHub Pages or your static host

## Hiding content without deleting it

If you want a page to remain in the repo but not show up as a clickable link in the schedule, add `publish: false` or `published: false` in the front matter:

```yaml
---
publish: false
---
```

This is especially useful for draft materials, future classes, or course planning pages that should stay in the repository but not appear in the public site.

## Site upkeep tips

- keep the home page brief and orientation-focused
- maintain a clear separation between Guide and Schedule pages
- keep filenames predictable and descriptive
- update the calendar and schedule together
- avoid editing generated files by hand unless you intentionally want to override the builder output
- keep the repository source as the canonical record and treat generated output as derived data

## Repository and publishing structure recommendation

For most instructors, the simplest setup is to keep a single branch and publish from the repository root:

1. source content stays in the repository root
2. generated output remains in `_data/` and `course_calendar.ics`
3. GitHub Pages publishes from the main branch at the root

This keeps the workflow straightforward, reduces branching complexity, and makes it easier for future instructors to understand how the site is built.

## Long-term goal

The goal of this template is not to build a course-specific site for one semester. It is to provide a durable, reusable structure that other instructors can understand, adapt, and maintain with minimal friction.

