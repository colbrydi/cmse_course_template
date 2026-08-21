---
layout: guide
title: "Recommended Instructor Workflow"
order: 30
mode: "guide"
---
# Recommended Instructor Workflow

This template is best used with a repeatable workflow so that each semester starts from a known structure.

## 1. Start from the calendar

Before editing the site content itself, define the semester dates in the appropriate calendar file. This is the anchor for all schedule generation.

## 2. Draft the site structure

Decide what belongs in the Guide and what belongs in the Schedule:

- Guide: policies, checklists, logistics, references
- Schedule: class meetings, labs, assignments, announcements

This split makes the site easier to navigate for students and easier to maintain for instructors.

## 3. Add the schedule pages

Create or rename markdown files in `Schedule/` using the naming conventions defined by the template. The file names drive the date-relationship logic used by the generator. The naming pattern should be descriptive enough to make the timeline readable without opening the file.

For example:

- `03-same-reflection.md`
- `03-plus-2-project-checkpoint.md`
- `03-next-sun-example.md`

These examples show how a due date can be attached to class day 03 while still landing on the right calendar day.

## 4. Generate the outputs

Run the semester-specific schedule command after updating the calendar and page structure. Review the generated warnings before publishing.

## 5. Check the site locally

Preview with `make serve` or build with `make build-site`. This is the best place to confirm the timeline, links, and page structure before publishing.

## 6. Publish intentionally

Commit the source changes and generated schedule artifacts together so the live site reflects the same schedule state as the repository.

## Keeping the Template Maintainable

A template is easiest to maintain when the structure is visible and predictable. Keep these principles in mind:

- do not duplicate information between the Guide and the Schedule
- keep the landing page simple
- prefer generated outputs over manual editing
- regenerate after any schedule/date changes
- keep page names and dates aligned with the semester calendar

This workflow gives future instructors a stable, understandable starting point instead of a custom one-off site.

