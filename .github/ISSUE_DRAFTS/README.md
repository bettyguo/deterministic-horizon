# Issue drafts

This folder is a **seeded backlog** for the Deterministic Horizon project. Each file is one ready-to-file GitHub issue, with frontmatter that the seeding scripts read to set the title, labels, and milestone.

## How to use it

```bash
# One-shot: create the milestones, then file every draft as a real issue.
bash scripts/seed_issues.sh           # POSIX (Git-Bash / Linux / macOS)
pwsh scripts/seed_issues.ps1          # PowerShell (Windows)
```

The scripts:

1. Verify `gh auth status` is logged in.
2. Create the four milestones (`v1.0.1`, `v1.1.0`, `v1.2.0`, `v1.3.0`) with due dates if they don't already exist.
3. For each `*.md` file in this folder, parse the frontmatter and `gh issue create` it.

You can run the scripts repeatedly — they skip drafts whose title already exists as an open issue.

## Manual filing

If you prefer to file by hand, open each draft and copy:

- the `title:` field → issue title
- the `labels:` list → labels (chip-pickers)
- the `milestone:` value → milestone dropdown
- everything below the closing `---` → issue body

## Where the milestones come from

See [`docs/roadmap.md`](../../docs/roadmap.md) for the milestone narrative and the dates.

## Adding new drafts

Match the existing front-matter schema:

```markdown
---
title: "[area] short imperative description"
labels:
  - help-wanted
  - enhancement
milestone: "v1.1.0"
---

## Context
...

## Acceptance criteria
- [ ] ...

## Hints
- ...
```

The `area` prefix is a convention, not enforced. Pick from `feat`, `bug`, `docs`, `test`, `perf`, `research`.
