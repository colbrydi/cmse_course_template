---
layout: schedule
date: '2026-09-15'
---

# Publishing and Draft Content

This page documents how to keep some content in the repository without exposing it on the public website.

## When to hide a page

Use a hidden schedule page when:

- the content is a draft
- the class is planned but not ready yet
- you want a placeholder that remains in the repository
- you want a future page without a public link

## How to hide a page

Add one of these entries to the page front matter:

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

The generator respects this and removes the clickable URL while keeping the schedule entry available in the source.

## Recommended publishing practice

- keep draft material in the repo
- render only final public content in the site
- use hidden pages for future lessons or in-progress workshop notes
- review the generated schedule data before deployment

## Final reminder

The template is most effective when the public site is a clean, maintained guide for the current semester and the repository itself remains the source of truth for future work.

## Before publishing

- regenerate the schedule
- review warnings
- check hidden pages are not linked unexpectedly
- confirm the site reflects the final intended structure