---
layout: schedule
title: "Course Website Template Guide"
order: 66
mode: "schedule"
---
# Course Website Template Guide

{% include schedule_widgets.html part="progress" %}

This repository is a template for building a schedule-driven course website. The goal is to help instructors create a website that is easy to maintain, easy to update, and consistent across semesters.

Use this site as a working guide for adapting the template to your own course. The sections below explain the core workflow, the required files, and the practical steps for making the template your own.

## What This Template Gives You

- a schedule-first course structure
- calendar-driven class dates from your semester configuration
- a generated course calendar in `.ics` format
- automatic schedule metadata generation from markdown files in `Schedule/`
- a guide structure for course policies, procedures, and instructor notes

## Recommended First Steps

1. Update site metadata in `_config.yml`.
2. Replace the example content in `Guide/` and `Schedule/`.
3. Edit the appropriate semester calendar in `config/`.
4. Run `make schedule-fall` or `make schedule-spring`.
5. Preview locally with `make serve` and then publish.

## Where to Make Changes

- Homepage: `index.md`
- Guide pages: `Guide/*.md`
- Schedule pages: `Schedule/*.md`
- Calendar config: `config/fall_calendar.yml` and `config/spring_calendar.yml`
- Template logic: `scripts/update_schedule.py`
- Local site workflow: `makefile`

## Instructor Workflow

The site is designed so that you can work in the same flow each semester:

- set the calendar dates
- add or rename markdown pages in `Schedule/`
- update guide content as needed
- regenerate the schedule data
- review warnings and fix mismatches
- publish the generated site

## Using the Guide and the Schedule

The Guide should hold instructional content that is stable across the semester, such as policies, support information, references, and descriptions of workflows.

The Schedule should hold the date-specific content for class meetings: agenda, activities, reading, assignments, and preparation notes. These pages are generated into the site timeline using naming conventions and front matter.

## Important Template Notes

- Do not edit generated YAML by hand unless you are intentionally regenerating it.
- Use the filename convention in `Instructors/Schedule_Filename_Convention.md`.
- Hidden schedule items can be suppressed with `publish: false` or `published: false` in front matter.
- Run the generator after any schedule change so `_data/schedule.yml` and `course_calendar.ics` stay current.

{% include schedule_widgets.html part="calendar" calendar_title="Course Calendar" class_time="TBD" class_location="TBD" subscription_path="/course_calendar.ics" %}
{% include schedule_widgets.html part="assets" class_time="TBD" class_location="TBD" %}
