# TaRen Improvement Backlog

**Last Updated:** May 6, 2026
**Priority Levels:** Critical (must fix), High (important), Medium (nice to have), Low (cosmetic)

---

## Priority 1: Critical Issues

### None Currently Identified

The codebase has no critical issues. All operational safety concerns from previous analysis have been addressed:

- ✅ Preflight fail-fast implemented
- ✅ Empty name fallback guard implemented
- ✅ Logger idempotency implemented
- ✅ UTF-8 decode error handling implemented

---

## Priority 2: High Impact Improvements

### 2.1 Consolidate Debug Logging in TaRen.**init**

**File:** `taren/taren.py` (lines 81-92)
**Current State:** 12 consecutive logger.debug() calls
**Issue:** Verbose initialization logging takes up significant space

```python
# Current (verbose)
logger.debug("self._config [%s]", self._config)
logger.debug("self._collection [%s]", self._collection)
logger.debug("self._downloads [%s]", self._downloads)
# ... 9 more debug lines
```

**Recommendation:** Extract to helper method

```python
def _log_initialization(self) -> None:
    """Log configuration details during initialization."""
    logger.debug("Configuration initialized: collection=%s, pattern=%s, ...",
                 self._collection, self._pattern, ...)
```

**Effort:** 15 minutes
**Impact:** Reduced clutter, cleaner initialization
**Validation:** Existing debug tests should still pass

---

### 2.2 Complete Type Annotations in Helper Module

**File:** `taren/helper.py`
**Current State:** Some functions lack explicit return type hints
**Issue:** Reduces IDE support and self-documentation

```python
# Current
@staticmethod
def ensure_directory(dirname: str) -> bool:
    """Ensure directory exists and is writable."""
    # ...

@staticmethod
def delete_file(filename: str):  # ← Missing return type
    """Delete a file."""
    # ...
```

**Recommendation:** Add explicit `-> bool` return types to all public methods

**Effort:** 15 minutes
**Impact:** Better IDE autocomplete, clearer contracts
**Validation:** Run type checker: `python -m mypy taren/helper.py`

---

### 2.3 Standardize Path Handling with pathlib

**File:** Multiple (taren/taren.py, taren/trash.py, taren/websitecache.py)
**Current State:** Mix of string-based `os.path` operations
**Issue:** Error-prone, harder to test

```python
# Current (string-based)
self._downloads: str = os.path.join(self._collection, TarenDefines.FOLDER_DOWNLOADS)
new_fqn: str = os.path.join(self._seen, f"{current_download.episode}{self._extension}")

# Better (pathlib)
from pathlib import Path
self._downloads: Path = Path(self._collection) / TarenDefines.FOLDER_DOWNLOADS
new_fqn: Path = self._seen / f"{current_download.episode}{self._extension}"
```

**Effort:** 45 minutes (across 3-4 files)
**Impact:** Clearer intent, easier path manipulation, cross-platform compatibility
**Validation:** Full test suite runs green

---

## Priority 3: Medium Impact Improvements

### 3.1 Extract Magic Numbers to Constants

**File:** `taren/websitecache.py` (line 60)
**Current State:** `hexdigest()[:8]` is hardcoded
**Issue:** No explanation for why 8 characters

```python
# Current
url_hash: str = hashlib.md5(websiteurl.encode()).hexdigest()[:8]

# Better
# In TarenDefines:
URL_HASH_LENGTH: int = 8
```

**Effort:** 10 minutes
**Impact:** Self-documenting, easier to adjust globally
**Validation:** No behavior change

---

### 3.2 Logging Format Consistency

**File:** Multiple (`taren/taren.py`, `taren/episodelist.py`, `taren/websitecache.py`)
**Current State:** Mixed logging styles with context
**Issue:** Inconsistent formatting makes parsing harder

```python
# Mix of formats:
logger.debug("cache file [%s]", self._cachename)
logger.info("total number of downloads [%s]", len(files))
logger.error("Failed to ensure downloads directory [%s], abort", self._downloads)
```

**Recommendation:** Adopt consistent format: `"operation: key=value [status]"`

```python
logger.info("cache_lookup: file=%s age_days=%d status=miss", ...)
logger.error("directory_create: path=%s status=failed", ...)
```

**Effort:** 30 minutes
**Impact:** Easier log parsing, machine-readable format
**Validation:** Test log output format

---

### 3.3 Configuration Validation Enhancement

**File:** `taren/tarenconfig.py`
**Current State:** Validates presence and basic types
**Issue:** Could add range checks for numeric bounds

```python
# Current validates: key exists, is string/int
# Could also validate: bounds (http_timeout > 0, http_retries in range)

# Recommendation: Add bounds validation
if http_timeout <= 0:
    errors.append("http_timeout must be positive (received: {http_timeout})")
if not (1 <= http_retries <= 10):
    errors.append("http_retries must be 1-10 (received: {http_retries})")
```

**Effort:** 20 minutes
**Impact:** Prevents misconfiguration at startup
**Validation:** Add tests for bounds validation

---

## Priority 4: Low Priority Polish

### 4.1 Episode Parsing Error Recovery

**File:** `taren/episodelist.py` (line 110)
**Current State:** Episode.parse() can produce incomplete episode
**Issue:** Silently skips malformed rows; could log details

```python
# Current
if not current_episode.empty:
    episodes.append(current_episode)

# Better: Log why episode was rejected
if not current_episode.empty:
    episodes.append(current_episode)
else:
    logger.debug("episode_rejected: id=%s reason=parse_failed",
                 episode_data[0] if episode_data else "unknown")
```

**Effort:** 15 minutes
**Impact:** Better debugging for data issues
**Validation:** No behavior change, debug logs only

---

### 4.2 Cache Filename Collision Prevention Documentation

**File:** `taren/websitecache.py` (line 60)
**Current State:** Comment explains hash is for collision prevention
**Issue:** Logic is clear but lacks detail

```python
# Current comment
# Include URL hash in cache filename to prevent collisions

# Better: Explain what it prevents
# Use URL hash to prevent cache collisions when same cachename
# is used with different URLs (e.g., different seasons/shows)
```

**Effort:** 5 minutes
**Impact:** Better documentation
**Validation:** None needed

---

### 4.3 Test Coverage for Trash Retention Age

**File:** `tests/test_trash.py`
**Current State:** Trash cleanup logic has mocked filesystem
**Issue:** Could add real filesystem integration test (optional)

**Effort:** 30 minutes (optional)
**Impact:** Validates trash aging logic end-to-end
**Validation:** New test in test_trash.py

---

## Implementation Roadmap

### Phase 1: Quick Wins (45 minutes)

1. Consolidate debug logging in TaRen.**init** (15 min)
2. Add type hints to helper.py (15 min)
3. Extract magic numbers to TarenDefines (10 min)
4. Fix logging format consistency (30 min) - can overlap

### Phase 2: Architectural Improvements (1 hour)

5. Migrate to pathlib for path operations (45 min)
6. Configuration bounds validation (20 min)

### Phase 3: Polish (Optional - 1.5 hours)

7. Episode parsing error recovery logging (15 min)
8. Cache filename collision prevention docs (5 min)
9. Trash retention age integration test (30 min)

---

## Success Criteria

- All 113 existing tests continue to pass
- No regressions in error handling paths
- Type checker (mypy) clean for modified files
- Code style consistent (Black formatting respected)
- Commit messages clear and reference this backlog

---

## Notes

- Improvements in Phase 1 can be done incrementally without test changes
- Phase 2 improvements require careful refactoring (recommend branch-based approach)
- Phase 3 items are optional and prioritized lower
- No critical issues identified; all items are quality improvements
