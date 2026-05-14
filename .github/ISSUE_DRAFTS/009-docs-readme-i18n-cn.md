---
title: "[docs] Chinese (Simplified) translation of the README"
labels:
  - documentation
  - good-first-issue
  - i18n
milestone: "v1.1.0"
---

## Context

A non-trivial slice of the agentic-systems community works primarily in Chinese; a `README.zh-CN.md` substantially expands the project's reach. The same is potentially true for ja/ko/de/ru, but Chinese gets us most of the immediate value.

## What needs to happen

1. Add `README.zh-CN.md` with a faithful translation of `README.md`.
2. Add a language switcher at the top of both files:
   ```markdown
   <p align="right">
     <a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a>
   </p>
   ```
3. Keep code blocks, tables, and equations untranslated — only translate prose.
4. Where the original has links to `docs/*.md`, link to the same English page (the docs themselves are not translated in this issue; that's follow-up work).

## Acceptance criteria

- [ ] `README.zh-CN.md` exists and renders cleanly on GitHub.
- [ ] Both README files have the language switcher.
- [ ] The links work from both directions.
- [ ] No translation of code, equations, citation BibTeX, or model identifiers.

## Hints

- This is a "translate the prose, keep the structure" task — the easiest way is to walk paragraph by paragraph.
- Native or near-native zh-CN speakers preferred. Reviewer should be a different native speaker than the translator.
