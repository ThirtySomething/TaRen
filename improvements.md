# TaRen Improvement Notes

Updated: 2026-05-06

## Goal

Track practical, high-value improvements identified in the current full code analysis.

## Current Baseline

- Compile check: clean
- Unit/integration tests (`unittest discover`): 113 passed
- Architecture: solid and modular
- Main risk area: operational edge-case handling

## Priority Backlog

### Priority 1

1. [x] Fail-fast preflight when `downloads/` or `seen/` cannot be created.
2. [x] Prevent fallback matches on empty episode names.
3. [x] Ensure runtime logger configuration is idempotent.
4. [x] Handle UTF-8 decode failures in website cache writes with explicit error logging.

### Priority 2

1. [x] Add tests for invalid UTF-8 responses.
2. [x] Add tests for concrete preflight directory creation failures.
3. [x] Add tests for repeated runtime build logger behavior.

### Priority 3

1. [x] Fix minor helper typo in logs.
2. [x] Normalize formatting style in touched files.
3. [x] Reduce small duplication in stats percentage calculation.

## Definition Of Done For Priority 1

- Behavior is deterministic on failure paths.
- No silent false positives in fallback matching.
- Repeated runtime construction does not duplicate handlers.
- Decode failures are explicit and diagnosable in logs.
- Test suite remains green.
