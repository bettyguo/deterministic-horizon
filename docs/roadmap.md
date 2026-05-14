# Roadmap

This roadmap reflects the public backlog that ships with the repository as
[`.github/ISSUE_DRAFTS/`](../.github/ISSUE_DRAFTS/). Each draft is mapped to one
of the milestones below; the seed scripts in [`scripts/`](../scripts/) create
the milestones (with these due dates) and file the drafts as real GitHub
issues.

The dates are public commitments to the community — they exist so that
external contributors know which work is in scope at any given time and roughly
when a PR has a reasonable chance of being merged. They are intentionally
conservative: each milestone has slack for review, CI flakes, and revisions.

## Milestones

| Milestone | Due       | Theme                                | Drafts                |
|-----------|-----------|--------------------------------------|-----------------------|
| `v1.0.1`  | 2026-06-04 | Polish: docs, demo, snapshot tests, CLI fix | 001, 002, 003, 004 |
| `v1.1.0`  | 2026-07-09 | Coverage: new model adapters + UX    | 005, 006, 007, 008, 009 |
| `v1.2.0`  | 2026-08-20 | Scale: new tasks + async evaluation  | 010, 011, 012         |
| `v1.3.0`  | 2026-10-29 | Research: architecture studies       | 013, 014              |

### `v1.0.1` — Polish (due 2026-06-04)

Three-week window. Everything here is a finishing touch on the camera-ready
release: a demo GIF, a CLI stub that should be wired up, a snapshot test that
pins the paper's Table 3 to the code, and a docs site. No theory work, no new
adapters. Issues in this milestone are tagged `good-first-issue` where
appropriate — they are deliberately scoped so a new contributor can land a PR
in a weekend.

### `v1.1.0` — Coverage (due 2026-07-09)

Five-week window after v1.0.1 ships. The goal is to expand the matrix of
providers we evaluate (Gemini, Together) and remove friction from the standard
sweep (resumable evaluation, an interactive demo, a Chinese-language README so
the work is discoverable inside the largest non-English ML community). None of
these change the theory; they widen the audience that can use it.

### `v1.2.0` — Scale (due 2026-08-20)

Six-week window. This is where the package stops being a paper companion and
starts being a benchmark: SWE-Bench-State validates the horizon on real
software-engineering tickets, SQL-Multi adds a second naturalistic task family,
and async-batched evaluation makes the standard sweep fast enough that a
reviewer can re-run it in an afternoon. Expect issues here to take 1–2
person-weeks each.

### `v1.3.0` — Research (due 2026-10-29)

Ten-week window. The two open architecture questions from the paper's
discussion section: does the horizon scale with `d_state` on Mamba/SSM models,
and does MoE expert specialisation shift `d*`? Both are paper-grade
contributions with co-credit on the follow-up; both depend on the v1.1.0
adapter work landing first.

## How the schedule is enforced

- The seed scripts (`scripts/seed_issues.{sh,ps1}`) create the GitHub
  milestones with the due dates above and file every draft against its
  milestone. Re-running the script is idempotent.
- Issues that slip past their milestone are rolled to the next one during the
  monthly triage pass (first Monday of each month).
- "Help wanted" issues never block a milestone from closing — the milestone
  ships when the maintainer-owned issues in it are done, and the help-wanted
  ones are re-homed.

## How to engage

- Pick any issue with the `good-first-issue` label.
- Comment to claim it before starting (avoids duplicate work).
- Open a draft PR early; the CI suite is fast and the maintainers prefer a
  short feedback loop.
- For `research` issues, please coordinate via discussion thread first — these
  often have unpublished context that's faster to share than to write up.

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the full contribution guide.
