# TaRen Improvement Roadmap

**Analysis Date**: May 5, 2026
**Codebase Status**: 54/54 tests passing, Grade: B+ (solid production-ready foundation)
**Scope**: 29 Python files in `taren/` directory

## Executive Summary

TaRen has a **solid architectural foundation** with good separation of concerns, Protocol-based design, and comprehensive configuration validation. The codebase is **production-ready** but has opportunities to improve in three key areas:

1. **Test Coverage** - Missing tests for match rules and conflict strategy
2. **Error Handling** - Inconsistent patterns (bool/None/exception/Null Object)
3. **Code Consistency** - String formatting, character stripping duplication, missing return statements

All improvements can be implemented incrementally without major refactoring.

---

## What's Working Well ✓

- ✓ Protocol-based design for testability
- ✓ Comprehensive configuration validation with fail-fast startup
- ✓ Clean orchestration flow (rename_process → \_load_episodes → \_collect_tasks → \_process_tasks)
- ✓ Chain of Responsibility for episode matching
- ✓ Command pattern for file mutations with rollback capability
- ✓ Effective HTML caching with collision prevention (URL hash)
- ✓ Consistent logging across all modules
- ✓ 85%+ type annotation coverage with modern Python 3.11+ syntax
- ✓ Safe file operations with exception handling and failure tracking

---

## High-Priority Improvements

### 1. Add Missing Unit Tests for Match Rules

**Status**: Not started
**Priority**: HIGH
**Effort**: 1-2 hours
**Impact**: 5 untested components (40% of Episode matching logic)

**Why this matters:**

- 5 match rule classes have no direct unit tests
- Only tested indirectly via `test_episode.py`
- Core matching logic is critical path, untested edge cases could cause failures

**Affected Files:**

- `taren/exactrepresentationmatchrule.py`
- `taren/leadingnumbermatchrule.py`
- `taren/dailymotiontokenmatchrule.py`
- `taren/tatortprefixmatchrule.py`
- `taren/episodenamecontainsrule.py`

**Proposal:**

- Create `tests/test_match_rules.py`
- Add unit tests for each rule's `matches()` method
- Test edge cases: empty strings, special characters, boundary values
- Test integration: verify rules follow Chain of Responsibility correctly

**Example tests to add:**

```python
class TestExactRepresentationMatchRule(unittest.TestCase):
    def test_exact_match_success(self): ...
    def test_exact_match_case_insensitive(self): ...
    def test_no_match_returns_false(self): ...
    def test_special_characters_handled(self): ...

class TestLeadingNumberMatchRule(unittest.TestCase):
    def test_leading_number_extracted(self): ...
    def test_no_leading_number_returns_false(self): ...
    def test_multiple_leading_numbers_takes_first(self): ...
```

---

### 2. Add Tests for SizeBasedConflictStrategy

**Status**: Not started
**Priority**: MEDIUM
**Effort**: 1 hour
**Impact**: Core conflict resolution untested

**Why this matters:**

- `SizeBasedConflictStrategy` is the only conflict resolution strategy used
- Has 3 distinct branches (no conflict, equal size, different sizes)
- Only tested indirectly via main workflow tests

**Affected Files:**

- `taren/sizebasedconflictstrategy.py`
- `tests/test_sizebasedconflictstrategy.py` (needs creation)

**Proposal:**

- Create unit test file specifically for conflict strategy
- Test each branch of the resolve() logic
- Test edge cases: zero-byte files, missing files, permission errors
- Mock `os.path.getsize()` and `os.path.exists()` for reliability

**Example tests to add:**

```python
class TestSizeBasedConflictStrategy(unittest.TestCase):
    def test_no_conflict_when_files_same_size(self): ...
    def test_conflict_when_old_larger(self): ...
    def test_conflict_when_new_larger(self): ...
    def test_skip_rename_false_triggers_trash(self): ...
    def test_handles_missing_old_file(self): ...
    def test_handles_missing_new_file(self): ...
```

---

### 3. Add Error Scenario Tests for Main Workflow

**Status**: Not started
**Priority**: MEDIUM
**Effort**: 2-3 hours
**Impact**: Better production confidence

**Why this matters:**

- Current `test_taren.py` focuses on happy paths
- Missing tests for network failures, filesystem errors, malformed data
- Production users will encounter these scenarios

**Affected Files:**

- `tests/test_taren.py`

**Proposal:**

- Add tests for each error scenario:
    - Network timeout when fetching episodes
    - Missing collection directory
    - Permission denied on downloads folder
    - Malformed episode list (invalid HTML)
    - Disk full when renaming files
    - File locked by another process

**Example tests to add:**

```python
class TestTaRenErrorScenarios(unittest.TestCase):
    def test_collection_missing_aborts_preflight(self): ...
    def test_trash_init_failure_stops_processing(self): ...
    def test_network_failure_in_load_episodes(self): ...
    def test_filesystem_error_in_process_tasks(self): ...
    def test_malformed_html_handled_gracefully(self): ...
```

---

## Medium-Priority Improvements

### 4. Standardize Error Handling Patterns

**Status**: Not started
**Priority**: MEDIUM
**Effort**: 3-4 hours
**Impact**: Improved maintainability and predictability

**Why this matters:**

- Current code uses mixed patterns: boolean returns, None returns, exceptions, Null Object pattern
- Callers must handle multiple error types for same operation
- Inconsistency leads to bugs (forgotten error checks)

**Current Mixed Patterns:**

- `trash.init() -> bool` (boolean error signal)
- `episode_list.find_episode() -> Episode` (Null Object: episode.empty check)
- `conflict_strategy.resolve() -> ConflictResolutionResult` (result object, no exception)
- `command.execute() -> bool` (boolean with stats tracking)
- `Helper.ensure_directory() -> bool` (boolean)

**Proposal:**

- Create custom exception hierarchy:
    ```python
    class TarenError(Exception): pass
    class NetworkError(TarenError): pass
    class FileSystemError(TarenError): pass
    class ConfigurationError(TarenError): pass
    ```
- Standardize on exceptions for exceptional conditions
- Keep result objects for business logic outcomes (e.g., conflicts)
- Document error propagation strategy in ARCHITECTURE.md

**Files to Update:**

- `taren/tarendefines.py` - Add exception classes
- `taren/trash.py` - Replace bool returns with exceptions
- `taren/websitecache.py` - Clearly distinguish network vs filesystem errors
- `taren/episodelist.py` - Document when empty list vs exception

---

### 5. Make HTTP Settings Configurable

**Status**: Not started
**Priority**: MEDIUM
**Effort**: 1.5 hours
**Impact**: Users can tune behavior to their network conditions

**Why this matters:**

- HTTP timeout (30 seconds) and retries (3) are hardcoded
- Users behind slow networks or with flaky connections cannot adjust
- No way to diagnose intermittent network issues

**Affected Files:**

- `taren/requestshttpfetchpolicy.py` - Lines 15-16 (hardcoded values)
- `taren/tarenconfig.py` - Add http_timeout and http_retries settings
- `taren/tarenruntimebuilder.py` - Pass config to HttpFetchPolicy

**Proposal:**

- Add to configuration:
    ```ini
    [network]
    http_timeout = 30        ; seconds
    http_retries = 3         ; attempts
    ```
- Load from config in `TarenRuntimeBuilder`
- Pass to `RequestsHttpFetchPolicy` constructor
- Add validation (timeout > 0, retries >= 1)
- Document in README with examples for different scenarios

---

### 6. Fix Missing Return Statement in RequestsHttpFetchPolicy

**Status**: Not started
**Priority**: MEDIUM
**Effort**: 30 minutes
**Impact**: Clearer code, explicit error handling

**Why this matters:**

- After retry loop exhaustion, function implicitly returns None
- Violates "explicit is better than implicit" principle
- Makes code harder to read and debug

**Affected Files:**

- `taren/requestshttpfetchpolicy.py` - Line 53

**Current Code:**

```python
def fetch(self, url: str, headers: dict[str, str]) -> bytes | None:
    for attempt in range(1, self._retries + 1):
        try:
            # ... success case
            return response.content
        except requests.RequestException as e:
            if attempt == self._retries:
                logger.error("Failed to download [%s]: %s", url, e)
                # Missing explicit return here
            # ...
```

**Fix:**

```python
def fetch(self, url: str, headers: dict[str, str]) -> bytes | None:
    for attempt in range(1, self._retries + 1):
        try:
            # ... success case
            return response.content
        except requests.RequestException as e:
            if attempt == self._retries:
                logger.error("Failed to download [%s]: %s", url, e)
                return None  # Explicit return
            # ...
    return None  # Fallback (should not reach)
```

---

## Low-Priority Improvements

### 7. Consolidate Duplicate Character Stripping Logic

**Status**: Not started
**Priority**: LOW
**Effort**: 30 minutes
**Impact**: Reduced code duplication, easier maintenance

**Why this matters:**

- Episode name cleaning logic repeated in 4 places
- Different regex patterns do similar things
- Hard to maintain consistency if behavior needs to change

**Current Locations:**

- `taren/episode.py` - Lines 133-138
- `taren/leadingnumbermatchrule.py` - Similar logic
- `taren/episodenamecontainsrule.py` - Similar logic
- `taren/dailymotiontokenmatchrule.py` - Similar logic

**Proposal:**

- Create `Helper.clean_episode_name()` method
- Document what characters are considered "invalid"
- Use in all 4 locations
- Add unit test for edge cases (special characters, unicode, etc.)

---

### 8. Standardize String Formatting to F-Strings

**Status**: Not started
**Priority**: LOW
**Effort**: 30 minutes
**Impact**: Modern Python style, better readability

**Why this matters:**

- Code mixes `.format()` and f-strings
- F-strings are faster and more readable (PEP 498)
- Consistency improves code readability

**Files to Update:**

- `taren/taren.py` - 5+ uses of `.format()`
- `taren/downloadlist.py` - 2 uses of `.format()`
- Others using `.format()` for consistency

**Example:**

```python
# Before:
new_fqn = os.path.join(self._seen, "{}{}".format(episode, self._extension))

# After:
new_fqn = os.path.join(self._seen, f"{episode}{self._extension}")
```

---

### 9. Add Missing Type Annotations

**Status**: Not started
**Priority**: LOW
**Effort**: 30 minutes
**Impact**: Improved IDE support, catch more type errors

**Why this matters:**

- 3-4 methods missing return type annotations
- Some unchecked type casts (BeautifulSoup operations)
- No `py.typed` marker for type hint distribution

**Affected Files:**

- `taren/episode.py` - `__str__()` missing return type
- `taren/episodelist.py` - Type safety in parsing
- `taren/trash.py` - Return types not all annotated
- `taren/websitecache.py` - Some type casts unchecked

**Proposal:**

- Add `def __str__(self) -> str:` annotations
- Use `@overload` for polymorphic methods if needed
- Add `py.typed` marker file for distribution
- Consider `pyright` strict mode in CI

---

### 10. Create Architecture Documentation

**Status**: Not started
**Priority**: LOW
**Effort**: 2 hours
**Impact**: Onboarding, maintenance, architectural clarity

**Why this matters:**

- New developers need to understand codebase quickly
- Current README brief, lacks examples
- Architecture decisions not documented

**Proposal:**

- Create `ARCHITECTURE.md`:
    - System overview diagram (text-based)
    - Module responsibilities
    - Data flow (episodes → downloads → tasks → commands)
    - Design patterns used and why
    - Extension points (new match rules, strategies)

- Expand `README.md`:
    - Installation instructions
    - Configuration examples
    - Troubleshooting guide
    - Performance tuning
    - Contributing guidelines

**Example Sections:**

```markdown
## Architecture Overview

TaRen orchestrates episode renaming through 5 phases:

1. **Load** - Fetch episode list from wiki
2. **Collect** - Find matching downloads
3. **Resolve** - Handle filename conflicts
4. **Execute** - Apply rename commands
5. **Finalize** - Cleanup trash, report stats

## Data Flow

episodes.csv → EpisodeList → DownloadTask → FileMutationCommand → Renamed File

## Extension Points

- New MatchRule implementations
- ConflictResolutionStrategy
- HttpFetchPolicy for different sources
```

---

## Improvement Timeline

### Phase 1: Critical - ✅ COMPLETED (2026-05-05)

**Actual Time**: ~2.5 hours
**Result**: 106 tests passing (up from 54 tests) - 96% increase

Focus on test coverage for core logic:

- [x] Add unit tests for 5 match rules (1 hour)
    - `tests/test_match_rules.py` - 40 new tests covering all 5 match rules
    - ExactRepresentationMatchRule: 5 tests
    - LeadingNumberMatchRule: 7 tests
    - DailymotionTokenMatchRule: 7 tests
    - TatortPrefixMatchRule: 7 tests
    - EpisodeNameContainsRule: 10 tests

- [x] Add SizeBasedConflictStrategy tests (0.5 hours)
    - `tests/test_sizebasedconflictstrategy.py` - 11 new tests
    - Tests all 3 branches: no conflict, equal size, different sizes
    - Edge cases: zero-byte files, large files, consistent results

- [x] Add error scenario tests (1 hour)
    - Enhanced `tests/test_taren.py` with 10 new error scenario tests
    - TaRenErrorScenarios class covering:
        - Empty website content handling
        - Task processing continuity after failures
        - Trash initialization failures
        - Preflight directory creation
        - Cleanup and trash statistics
        - Episode matching skipping
        - Already-placed file handling

**Outcome**: 106 unit tests, exceeds 60+ target ✓

---

### Phase 2: Quality (Recommended Next) - ~4 hours

Focus on consistency and error handling:

- [ ] Create TarenError exception hierarchy (0.5 hours)
- [ ] Standardize error handling patterns (2 hours)
- [ ] Fix missing return statement in RequestsHttpFetchPolicy (0.5 hours)
- [ ] Make HTTP settings configurable (1 hour)
- [ ] Run full test suite and verify no regressions

**Expected Outcome**: Clearer error handling, more configurable behavior

---

### Phase 3: Polish (Optional) - ~2.5 hours

Focus on code quality and style:

- [ ] Consolidate character stripping logic (0.5 hours)
- [ ] Standardize string formatting to f-strings (0.5 hours)
- [ ] Add missing type annotations (0.5 hours)
- [ ] Run mypy and fix any type issues (0.5 hours)

**Expected Outcome**: More consistent code, better IDE support

---

### Phase 4: Documentation (Optional) - ~2 hours

Focus on knowledge sharing:

- [ ] Create ARCHITECTURE.md (1 hour)
- [ ] Expand README with examples (1 hour)

**Expected Outcome**: Easier onboarding, clearer architecture understanding

---

## Implementation Notes

### How to Prioritize

1. **Start with Phase 1** if you want to increase test coverage and confidence
2. **Add Phase 2** if you encounter error handling issues in production
3. **Add Phase 3** if you have code quality standards or CI lint checks
4. **Add Phase 4** if you have team onboarding needs

### How to Execute

- Use `git checkout -b improve/test-coverage` for each phase
- Write tests before fixing code (TDD approach)
- Run `python -m unittest discover -s tests` after each change
- Commit frequently with descriptive messages

### Risk Assessment

| Issue                         | Risk   | Mitigation                 |
| ----------------------------- | ------ | -------------------------- |
| **Untested match rules fail** | HIGH   | Phase 1 addresses this     |
| **Network timeout too short** | MEDIUM | Phase 2 makes configurable |
| **Silent failures in match**  | MEDIUM | Phase 1 adds error tests   |
| **Code style inconsistency**  | LOW    | Phase 3 addresses this     |
| **New dev confusion**         | LOW    | Phase 4 addresses this     |

---

## Codebase Strengths to Preserve

When implementing these improvements, keep these strengths:

1. ✓ Protocol-based design for testability
2. ✓ Comprehensive configuration validation
3. ✓ Clear orchestration flow
4. ✓ Good logging practices
5. ✓ Type safety with modern Python syntax

Any changes should maintain or improve these qualities.

---

## Success Metrics

| Phase   | Metric                     | Current | Target        |
| ------- | -------------------------- | ------- | ------------- |
| Phase 1 | Test count                 | 54      | 65+           |
| Phase 1 | Test coverage              | ~85%    | ~95%          |
| Phase 2 | Error patterns consistency | Mixed   | Standardized  |
| Phase 3 | Linting errors             | ~5      | 0             |
| Phase 4 | Docs coverage              | Basic   | Comprehensive |

---

## Related Documents

- See `ANALYSIS_EXECUTIVE_SUMMARY.md` for detailed health check
- See `COMPREHENSIVE_CODE_ANALYSIS.md` for issue-by-issue breakdown
- See `CODE_ANALYSIS_QUICK_REFERENCE.md` for code examples
