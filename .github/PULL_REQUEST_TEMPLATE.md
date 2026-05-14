<!--
Thanks for contributing! A short PR description goes a long way.
See CONTRIBUTING.md for the full checklist.
-->

## What does this change?

<!-- One-paragraph summary. Bullets fine. -->

## Why?

<!-- Link the motivating issue or paper section. -->

Closes #

## Testing

- [ ] `pytest -q -m "not slow and not api"` passes locally
- [ ] `ruff check src tests` is clean
- [ ] `black --check src tests` is clean
- [ ] If this changes numbers in the paper, I re-ran `make paper-tables` and the diff is intentional

## Type of change

- [ ] Bug fix (non-breaking)
- [ ] New task / model adapter / metric
- [ ] Refactor (no user-visible change)
- [ ] Docs only
- [ ] Breaking change (please describe migration below)

## Notes for reviewers

<!-- Anything non-obvious about the change? Tricky tradeoffs you considered? -->
