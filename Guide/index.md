---
layout: guide
title: "Template Guide Overview"
order: 0
mode: "guide"
---
# Template Guide Overview

This Guide is meant to tell future instructors how to use this course-website template rather than to model a specific course. It is a working reference for the structure, conventions, and maintenance steps used by this repository.

The template is designed to stay simple: the course calendar determines the semester timeline, the `Schedule/` directory holds date-specific content, and the `Guide/` directory holds more stable reference material.

## How to Use This Guide

Start here when you want to understand the template as a system.

- Use the Quick Start page to set up a new course site.
- Use the Glossary page to understand the naming and publishing conventions.
- Use the workflow pages to decide how to structure the semester and keep the site maintainable.
- Use the schedule pages as examples of how class-day pages are written and linked into the course timeline.

## Core Design

This template separates content by purpose:

- `index.md` is the landing page for the course.
- `Guide/` contains static reference material such as policies, procedures, and workflow notes.
- `Schedule/` contains date-based class meeting pages.
- `config/` defines the semester calendar.
- `scripts/update_schedule.py` generates the schedule metadata automatically.

That separation keeps the website easier to maintain and reduces the chance that instructors will hand-edit generated output.

## Best Practices for New Instructors

- Keep the course landing page brief and action-oriented.
- Put stable policy and process information in the Guide.
- Put weekly/class-specific content in the Schedule.
- Change the calendar and schedule files before generating site data.
- Review warnings from the schedule generator before publishing.

## Template Philosophy

The structure intentionally favors clarity over complexity. A course site should help students and instructors quickly find what they need without requiring a large maintenance burden. The template is therefore built around a small set of conventions rather than a large amount of custom logic.

Use this guide as the reference manual for the repository itself, not as an example class page.
