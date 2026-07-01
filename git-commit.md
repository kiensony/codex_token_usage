# Git Branch and Commit Standard

Use this standard for every branch name and commit message in this repository.

## Branch Naming

Use lowercase, hyphen-separated descriptions after the prefix.

- `feat/<short-description>` for new features.
- `fix/<short-description>` for bug fixes.
- `docs/<short-description>` for documentation-only changes.
- `test/<short-description>` for test-only changes.
- `refactor/<short-description>` for behavior-preserving code cleanup.
- `perf/<short-description>` for performance improvements.
- `ci/<short-description>` for CI or workflow changes.
- `chore/<short-description>` for maintenance that does not change runtime behavior.
- `hotfix/<short-description>` for urgent production fixes.
- `v<major>.<minor>.<patch>` for release/version branches or tags.

Examples:

```text
feat/tps-rps-overview
fix/filter-escape-clear
docs/git-commit-standard
test/tui-key-interactions
v1.4.0
```

## Commit Messages

Use Conventional Commit style:

```text
<type>(optional-scope): <short imperative summary>
```

Allowed types:

- `feat` for a new feature.
- `fix` for a bug fix.
- `docs` for documentation.
- `test` for tests.
- `refactor` for behavior-preserving code changes.
- `perf` for performance improvements.
- `ci` for CI or workflow updates.
- `chore` for maintenance.
- `build` for packaging or build-system changes.
- `release` for version release commits.

Examples:

```text
feat(tui): add tps and rps overview indicators
fix(tui): preserve filter state on cancel
docs: add git branch and commit standard
test(tui): cover alternate overlay close keys
release: v1.4.0
```

## Commit Checklist

Before committing:

1. Run `git status --short`.
2. Stage only files related to the current change.
3. Run focused tests for code changes.
4. Run the full suite when the change can affect shared behavior.
5. Use one logical change per commit.

For this project, the default full test command is:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
