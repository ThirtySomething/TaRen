# TaRen Improvement Proposal (Fresh Analysis)

Date: 2026-05-05
Scope: Entire codebase reviewed from current workspace state.

## What Is Working Well

- Clear orchestration flow in `TaRen.rename_process()` with dedicated private steps.
- Good use of extension points (match rules, conflict strategy, HTTP fetch policy).
- Useful test suite covering many happy-path scenarios.
- Null-object style handling for "no episode found" via `Episode.empty_instance()`.

## High-Priority Improvements

### 1. Harden file operations against runtime failures

Why this matters:
- Rename/delete/move operations can fail (permissions, locked files, missing paths).
- Current flow can crash mid-run or produce partial processing.

Proposal:
- Wrap filesystem operations in `try/except` and log meaningful context.
- Let command execution return success/failure or raise controlled domain errors.
- Track failures in `Stats` and include them in summary output.

Files:
- `taren/renamefilecommand.py`
- `taren/movetotrashcommand.py`
- `taren/trash.py`
- `taren/taren.py`

### 2. Add explicit configuration validation at startup

Why this matters:
- Invalid values (negative cache age, non-integer age values, empty URL, bad paths) are not validated early.
- Runtime failures appear later and are harder to diagnose.

Proposal:
- Add validation step after loading config and before running rename flow.
- Validate required keys and types (especially integer fields and URL/path fields).
- Fail fast with one clear error report.

Files:
- `taren/tarenconfig.py`
- `taren/tarenruntimebuilder.py`
- `taren/taren.py`

### 3. Prevent silent mismatch between configured and actual outcomes

Why this matters:
- `Stats` increments after commands execute, but command exceptions are not controlled.
- Result summaries can become misleading if one command fails after previous state changes.

Proposal:
- Introduce command result object or boolean return.
- Process commands with per-command error handling and deterministic policy:
  - stop on first failure, or
  - continue and aggregate errors.
- Include `downloads_failed` (or similar) in `Stats`.

Files:
- `taren/filemutationcommand.py`
- `taren/taren.py`
- `taren/stats.py`

### 4. Move from root/global logging calls to module loggers

Why this matters:
- Current `logging.info/debug/error` calls are global and harder to control per module.
- Module loggers improve filtering, testing, and future extensibility.

Proposal:
- In each module, define `logger = logging.getLogger(__name__)`.
- Replace direct `logging.*` calls with `logger.*`.

Files:
- Most files under `taren/`, especially:
- `taren/taren.py`
- `taren/episodelist.py`
- `taren/websitecache.py`
- `taren/trash.py`

## Medium-Priority Improvements

### 5. Tighten type hints for task and config data

Why this matters:
- `DownloadTask.episode` is typed as `object`, reducing static checks and IDE support.

Proposal:
- Type `episode` as `Episode`.
- Review related APIs for stricter typing consistency.

Files:
- `taren/downloadtask.py`
- `taren/taren.py`

### 6. Remove duplicate legacy alias in helper utility

Why this matters:
- `ensureDirectory` duplicates `ensure_directory` and keeps mixed naming style.

Proposal:
- Remove `ensureDirectory` alias if no external compatibility requirement exists.

Files:
- `taren/helper.py`

### 7. Make cache filename more collision-safe

Why this matters:
- Cache filename uses only pattern (`{pattern}.html`).
- Different URLs with same pattern can collide.

Proposal:
- Include a URL hash in cache filename (for example: `<pattern>_<hash>.html`).
- Optionally persist metadata alongside cache.

Files:
- `taren/websitecache.py`
- `taren/cachedhtmlepisodesource.py`

### 8. Improve readability/parsability of summary stats

Why this matters:
- Current multi-line `__str__` formatting is human-readable but less structured.

Proposal:
- Use deterministic key-value style output.
- Consider adding `to_dict()` for future JSON output.

Files:
- `taren/stats.py`

## Test Coverage Gaps

### 9. Add failure-path tests for file operations

Why this matters:
- Current tests mostly validate successful flows.
- The highest-risk behavior is around filesystem failure handling.

Proposal:
- Add tests simulating `OSError`/`PermissionError` in:
  - rename command
  - move-to-trash command
  - trash cleanup/listing
- Verify `Stats` and logs reflect failures correctly.

Files:
- `tests/test_taren.py`
- `tests/test_trash.py`
- new test files for command classes if needed

### 10. Add config validation tests

Why this matters:
- Validation logic should be stable and explicit.

Proposal:
- Add tests for invalid values (non-int cache/trash age, empty wiki URL, invalid collection path).
- Ensure startup fails early with clear diagnostics.

Files:
- `tests/test_tarenconfig.py`
- `tests/test_program.py`

## Suggested Implementation Order

1. File operation hardening and failure accounting (`Stats` + command behavior).
2. Config validation and startup fail-fast path.
3. Failure-path tests for filesystem and config validation.
4. Module logger migration.
5. Typing cleanup and helper alias removal.
6. Cache filename collision improvements.
7. Stats output restructuring.

## Practical Outcome

Applying the first three items will deliver the largest reliability gain with the lowest architectural risk. The remaining items are quality improvements that will reduce maintenance cost and improve confidence over time.
