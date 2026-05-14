---
title: "[docs] Publish `docs/` to GitHub Pages via MkDocs"
labels:
  - documentation
  - help-wanted
milestone: "v1.0.1"
---

## Context

We have a reasonable `docs/` tree now (`when-to-delegate`, `theorem-cheatsheet`, `architecture`, `reproducing`, `faq`), but it only renders on github.com. A real docs site at e.g. `deterministic-horizon.github.io/deterministic-horizon` would:

- Be linkable from the paper without showing raw `.md`.
- Get search built-in.
- Let us version-pin docs to releases.

## What needs to happen

1. Add `mkdocs.yml` at the repo root with the `material` theme.
2. Wire `docs/` as the source.
3. Add a `gh-pages` deploy workflow at `.github/workflows/docs-deploy.yml` that runs on tag pushes (`v*`) and on manual dispatch.
4. Add a "Docs" badge to the README that points at the deployed site.

## Acceptance criteria

- [ ] `mkdocs serve` works locally.
- [ ] The deploy workflow publishes successfully on a tag push to a test branch.
- [ ] Docs index page mirrors `docs/README.md`.
- [ ] All cross-links between docs pages still resolve in the rendered site.
- [ ] README "Docs" badge added.

## Hints

- `mkdocs-material` is the standard choice; pin the version in `pyproject.toml` under a new `docs` extra.
- The `gh-pages` action ([`peaceiris/actions-gh-pages`](https://github.com/peaceiris/actions-gh-pages)) is well-tested.
- Keep the navigation order matching the table in `docs/README.md`.
