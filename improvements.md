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

Status: Completed (2026-05-05)

Why this matters:

- Rename/delete/move operations can fail (permissions, locked files, missing paths).
- Current flow can crash mid-run or produce partial processing.

Proposal:

- Wrap filesystem operations in `try/except` and log meaningful context.
- Let command execution return success/failure or raise controlled domain errors.
- Track failures in `Stats` and include them in summary output.

Implemented:

- `FileMutationCommand.execute(...)` now returns `bool` success/failure.
- Rename and trash move operations are wrapped in guarded filesystem handling.
- Per-task command execution now aborts remaining commands after the first failure.
- `Stats` includes `downloads_failed` and summary output includes this metric.

Files:

- `taren/renamefilecommand.py`
- `taren/movetotrashcommand.py`
- `taren/trash.py`
- `taren/taren.py`

### 2. Add explicit configuration validation at startup

Status: Completed (2026-05-05)

Why this matters:

- Invalid values (negative cache age, non-integer age values, empty URL, bad paths) are not validated early.
- Runtime failures appear later and are harder to diagnose.

Proposal:

- Add validation step after loading config and before running rename flow.
- Validate required keys and types (especially integer fields and URL/path fields).
- Fail fast with one clear error report.

Implemented:

- Added `TarenConfig.validate()` with checks for required string values.
- Added numeric bounds/type checks for `taren.maxcache` and `taren.trashage`.
- Added URL validation for `taren.wiki` and level validation for `logging.loglevel`.
- Startup now aborts early via `TarenRuntimeBuilder.validate_config(...)` before logger/runner creation.
- `program.main()` now exits with status code 1 on invalid configuration.

Files:

- `taren/tarenconfig.py`
- `taren/tarenruntimebuilder.py`
- `taren/taren.py`

### 3. Prevent silent mismatch between configured and actual outcomes

Status: Completed (2026-05-05)

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

Status: Completed (2026-05-05)

Why this matters:

- Current `logging.info/debug/error` calls are global and harder to control per module.
- Module loggers improve filtering, testing, and future extensibility.

Proposal:

- In each module, define `logger = logging.getLogger(__name__)`.
- Replace direct `logging.*` calls with `logger.*`.

Implemented:

- Migrated `taren` modules with direct log calls to module-level `logger` usage.
- Updated affected test patch target from `taren.taren.logging.error` to `taren.taren.logger.error`.

Files:

- Most files under `taren/`, especially:
- `taren/taren.py`
- `taren/episodelist.py`
- `taren/websitecache.py`
- `taren/trash.py`

## Medium-Priority Improvements

### 5. Tighten type hints for task and config data

Status: Completed (2026-05-05)

Why this matters:

- `DownloadTask.episode` is typed as `object`, reducing static checks and IDE support.

Proposal:

- Type `episode` as `Episode`.
- Review related APIs for stricter typing consistency.

Implemented:

- Added import of `Episode` to `taren/downloadtask.py`.
- Changed `DownloadTask.episode` type from `object` to `Episode`.
- Updated corresponding test to use the proper type.

Files:

- `taren/downloadtask.py`
- `tests/test_helper.py` (updated alias usage in test)

### 6. Remove duplicate legacy alias in helper utility

Status: Completed (2026-05-05)

Why this matters:

- `ensureDirectory` duplicates `ensure_directory` and keeps mixed naming style.

Proposal:

- Remove `ensureDirectory` alias if no external compatibility requirement exists.

Implemented:

- Removed `ensureDirectory()` static method from `taren/helper.py`.
- Updated test in `tests/test_helper.py` to call `ensure_directory` directly.
- Verified no other code depends on the camelCase alias.

Files:

- `taren/helper.py`

### 7. Make cache filename more collision-safe

Status: Completed (2026-05-05)

Why this matters:

- Cache filename uses only pattern (`{pattern}.html`).
- Different URLs with same pattern can collide.

Proposal:

- Include a URL hash in cache filename (for example: `<pattern>_<hash>.html`).
- Optionally persist metadata alongside cache.

Implemented:

- Added `import hashlib` to `taren/websitecache.py`.
- Modified cache filename generation in `__init__`: now uses `{pattern}_{url_hash}.html` format.
- URL hash is first 8 chars of MD5(websiteurl), ensuring different URLs produce different cache files.
- Example: `pattern_c45f8974.html` (where c45f8974 is hash of the URL).
- All existing tests pass without modification; collision-safety is now transparent.

Files:

- `taren/websitecache.py`

### 8. Improve readability/parsability of summary stats

Status: Completed (2026-05-05)

Why this matters:

- Current multi-line `__str__` formatting is human-readable but less structured.

Proposal:

- Use deterministic key-value style output.
- Consider adding `to_dict()` for future JSON output.

Implemented:

- Restructured `__str__()` to use deterministic key-value format (one stat per line).
- Example output: `episodes_total: 10`, `episodes_owned: 5 (50.00%)`
- Added `to_dict()` method that returns dict of all stats for JSON serialization.
- Returns: episodes_total, episodes_owned, episodes_owned_percent, downloads_total, downloads_renamed, downloads_moved, downloads_deleted, downloads_failed, downloads_trash
- Updated test assertion to match new format.

Files:

- `taren/stats.py`
- `tests/test_stats.py`

## Test Coverage Gaps

### 9. Add failure-path tests for file operations

Status: Completed (2026-05-05)

Why this matters:

- Current tests mostly validate successful flows.
- The highest-risk behavior is around filesystem failure handling.

Proposal:

- Add tests simulating `OSError`/`PermissionError` in:
    - rename command
    - move-to-trash command
    - trash cleanup/listing
- Verify `Stats` and logs reflect failures correctly.

Implemented:

- Added tests for rename command failure accounting.
- Added tests for move-to-trash command failure accounting.
- Added test ensuring command execution stops after the first failure.
- Added trash move failure-path test.

Files:

- `tests/test_taren.py`
- `tests/test_trash.py`
- new test files for command classes if needed

### 10. Add config validation tests

Status: Completed (2026-05-05)

Why this matters:

- Validation logic should be stable and explicit.

Proposal:

- Add tests for invalid values (non-int cache/trash age, empty wiki URL, invalid collection path).
- Ensure startup fails early with clear diagnostics.

Implemented:

- Added `TarenConfig.validate()` tests for valid and invalid value scenarios.
- Added runtime-builder fail-fast test when validation fails.
- Added entrypoint test asserting startup exits non-zero on invalid configuration.

Files:

- `tests/test_tarenconfig.py`
- `tests/test_program.py`

## Suggested Implementation Order

1. File operation hardening and failure accounting (`Stats` + command behavior). Status: Completed (2026-05-05)
2. Config validation and startup fail-fast path. Status: Completed (2026-05-05)
3. Failure-path tests for filesystem and config validation. Status: Completed (2026-05-05)
4. Module logger migration. Status: Completed (2026-05-05)
5. Typing cleanup and helper alias removal. Status: Completed (2026-05-05)
6. Cache filename collision improvements. Status: Completed (2026-05-05)
7. Stats output restructuring. Status: Completed (2026-05-05)

## Practical Outcome

Applying the first three items will deliver the largest reliability gain with the lowest architectural risk. The remaining items are quality improvements that will reduce maintenance cost and improve confidence over time.
