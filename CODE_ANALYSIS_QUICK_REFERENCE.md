# TaRen Code Analysis - Quick Reference & Code Examples

## Test Results Summary

✓ **54 tests passed** (0.065s)

### Test Coverage by Component

| Component               | Tests   | Status    | Notes                                    |
| ----------------------- | ------- | --------- | ---------------------------------------- |
| Configuration           | 3       | ✓ Pass    | Validation logic well-tested             |
| Episode                 | 7+      | ✓ Pass    | Parsing and matching covered             |
| File Operations         | 8+      | ✓ Pass    | Commands, trash, helpers                 |
| Main Workflow           | 10+     | ✓ Pass    | Integration tests present                |
| Cache/Network           | 8+      | ✓ Pass    | HTTP retry logic tested                  |
| **Match Rules**         | **0**   | ✗ Missing | **No dedicated unit tests**              |
| **Commands (isolated)** | Partial | △         | Tested through integration, not isolated |

---

## Critical Issues - Code Examples

### Issue 1: Missing Return Statement in `requestshttpfetchpolicy.py`

**Current Code (Lines 38-54):**

```python
def fetch(self, url: str, headers: dict[str, str]) -> bytes | None:
    for attempt in range(1, self._retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=self._timeout_seconds)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            if attempt == self._retries:
                logger.error("Failed to download [%s]: %s", url, e)
                return None  # ← THIS LINE EXISTS, but...
            logger.warning(
                "download attempt [%s/%s] failed for [%s]: %s",
                attempt,
                self._retries,
                url,
                e,
            )
    # ← IMPLICIT None return here - should be explicit
```

**Status**: Actually OK - explicit return exists, but Python best practice would add comment or ensure clarity

---

### Issue 2: HTML Parsing Guard (Currently Protected, But Worth Documenting)

**Location**: [episodelist.py](taren/episodelist.py), lines 80-92

```python
def _parse_website(self, websitecontent: str) -> list[Episode]:
    """Build internal list about episodes based on website content."""

    # Guard 1: Check for empty content
    if not websitecontent.strip():
        logger.warning("episode list website content is empty")
        return []

    # Parse website using BeautifulSoup
    websitedata: BeautifulSoup = BeautifulSoup(websitecontent, "html.parser")

    # Guard 2: Check for table existence
    table = websitedata.find("table")
    if table is None:
        logger.warning("episode list table not found in website content")
        return []  # ← Protected from NoneType.find_all() crash

    rows: list[Tag] = table.find_all("tr")
    episodes: list[Episode] = self._build_list_of_episodes(rows)
    return episodes
```

**Status**: ✓ Well-protected; guards in good order. Could add comment explaining why.

---

### Issue 3: Mixed Error Handling Patterns

**Pattern Inconsistency in taren.py (lines 102-154):**

```python
# Pattern A: Boolean return for directory initialization
if not self._trash.init():
    return None  # ← Calling code must check boolean

# Pattern B: Null Object pattern for missing data
episode: Episode = episode_list.find_episode(current_download)
if episode.empty:  # ← Check special attribute
    continue

# Pattern C: Result object pattern
conflict_result: ConflictResolutionResult = self._conflict_strategy.resolve(old_fqn, new_fqn)
# ← No error case; assumes always succeeds

# Pattern D: Command pattern with boolean result
if not command.execute(statistics):
    logger.error("abort remaining commands for current task due to previous failure")
    break  # ← Boolean check again
```

**Issue**: Mixed patterns make code harder to read and maintain.

**Recommended Solution**:

```python
# Standardize on Result/Exception pattern:

class TarenResult(Generic[T]):
    def __init__(self, value: T | None = None, error: str | None = None):
        self.value = value
        self.error = error
        self.success = error is None

    def or_raise(self) -> T:
        if not self.success:
            raise TarenError(self.error)
        return self.value

    def or_default(self, default: T) -> T:
        return self.value if self.success else default

# Usage:
trash_init = self._trash.init()
if not trash_init.success:
    logger.error("Trash init failed: %s", trash_init.error)
    return
```

---

## Code Quality Issues - Examples

### Example 1: String Format Inconsistency

**Current (Multiple Styles Mixed):**

```python
# taren.py line 48
searchpattern: str = "*{}*{}".format(self._pattern, self._extension)

# taren.py line 71
"{}{}".format(current_download.episode, self._extension)

# episodelist.py line 68 (good - f-string)
logger.debug("pattern [%s]", pattern)

# helper.py line 45 (using %)
logger.debug("Directory [%s] created", dirname)
```

**Recommended**: Standardize on f-strings

```python
# Consistent style:
searchpattern: str = f"*{self._pattern}*{self._extension}"
new_filename = f"{current_download.episode}{self._extension}"
logger.debug(f"Directory [{dirname}] created")
```

### Example 2: Character Stripping Logic Duplication

**Current Code (episode.py, lines 130-139):**

```python
def _strip_invalid_characters(self) -> None:
    """Remove characters which are invalid for filenames"""
    for current_invalid_character in Episode._invalid_characters:
        self.episode_broadcast = self.episode_broadcast.replace(
            current_invalid_character, " "
        ).strip()
        self.episode_inspectors = self.episode_inspectors.replace(
            current_invalid_character, " "
        ).strip()
        self.episode_name = self.episode_name.replace(
            current_invalid_character, " "
        ).strip()
        self.episode_sequence = self.episode_sequence.replace(
            current_invalid_character, "-"
        ).strip()
```

**Issue**: 4 similar operations, hard to maintain, inconsistent replacements

**Refactored:**

```python
def _clean_field(self, field: str, invalid_chars: list[str], replacement: str = " ") -> str:
    """Replace invalid characters and strip whitespace."""
    for char in invalid_chars:
        field = field.replace(char, replacement)
    return field.strip()

def _strip_invalid_characters(self) -> None:
    """Remove characters which are invalid for filenames."""
    self.episode_broadcast = self._clean_field(
        self.episode_broadcast,
        Episode._invalid_characters
    )
    self.episode_inspectors = self._clean_field(
        self.episode_inspectors,
        Episode._invalid_characters
    )
    self.episode_name = self._clean_field(
        self.episode_name,
        Episode._invalid_characters
    )
    self.episode_sequence = self._clean_field(
        self.episode_sequence,
        Episode._invalid_characters,
        replacement="-"
    )
```

---

## Testing Gaps - Specific Examples

### Gap 1: Match Rules Not Unit Tested

**Missing Tests for 5 Match Rules:**

Currently, match rules are tested only indirectly through `Episode.matches()`. Should add:

```python
# tests/test_exact_representation_match_rule.py
import unittest
from taren.exactrepresentationmatchrule import ExactRepresentationMatchRule
from taren.episode import Episode

class TestExactRepresentationMatchRule(unittest.TestCase):
    def test_matches_exact_representation(self):
        rule = ExactRepresentationMatchRule()
        episode = Episode()
        episode.episode_id = 1
        episode.episode_name = "Test"
        episode.episode_inspectors = "Inspector"
        episode.episode_broadcast = "ARD"
        episode.episode_sequence = "1"
        episode.episode_year = 2020

        # Exact match
        filename = str(episode)  # "Tatort - 0001 - Test - Inspector - ARD - 2020"
        self.assertTrue(rule.try_match(filename, episode))

    def test_no_match_partial_string(self):
        rule = ExactRepresentationMatchRule()
        episode = Episode()
        # ... setup ...

        # Partial string
        filename = "Tatort - 0001"
        self.assertIsNone(rule.try_match(filename, episode))

# Similar for LeadingNumberMatchRule, DailymotionTokenMatchRule, etc.
```

### Gap 2: SizeBasedConflictStrategy Not Tested

**Missing Test:**

```python
# tests/test_conflict_resolution.py
import unittest
import tempfile
from pathlib import Path
from taren.sizebasedconflictstrategy import SizeBasedConflictStrategy

class TestSizeBasedConflictStrategy(unittest.TestCase):
    def test_new_file_no_conflict(self):
        strategy = SizeBasedConflictStrategy()
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.mp4"
            new_file = Path(tmpdir) / "new.mp4"
            old_file.write_bytes(b"old content here")
            # new_file doesn't exist

            result = strategy.resolve(str(old_file), str(new_file))

            self.assertIsNone(result.move_to_trash)
            self.assertFalse(result.skip_rename)

    def test_equal_size_conflict(self):
        strategy = SizeBasedConflictStrategy()
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.mp4"
            new_file = Path(tmpdir) / "new.mp4"
            old_file.write_bytes(b"same size!!!!!")
            new_file.write_bytes(b"same size!!!!!")

            result = strategy.resolve(str(old_file), str(new_file))

            self.assertEqual(result.move_to_trash, str(new_file))
            self.assertFalse(result.skip_rename)

    def test_old_file_smaller_conflict(self):
        # old_file smaller -> move old to trash, skip rename
        # old_file larger -> move new to trash, proceed with rename
```

---

## Performance Analysis - Details

### Regex Pattern Duplication

**Current Usage Scattered:**

| Rule                        | Pattern         | Regex                        |
| --------------------------- | --------------- | ---------------------------- |
| `TatortPrefixMatchRule`     | `Tatort - 0000` | `r"^(Tatort - ([0-9]{4}) )"` |
| `LeadingNumberMatchRule`    | `0000 ...`      | `r"(^[0-9]{4} )"`            |
| `DailymotionTokenMatchRule` | `_E0000_`       | `r"(_E([0-9]{3,4})_)"`       |

**Current Cost**: Regex compiled each time `try_match()` called

**Optimization**:

```python
# taren/tarendefines.py
import re

class TarenDefines:
    # ... existing constants ...

    # Regex patterns
    REGEX_TATORT_PREFIX: re.Pattern = re.compile(r"^(Tatort - ([0-9]{4}) )")
    REGEX_LEADING_NUMBER: re.Pattern = re.compile(r"(^[0-9]{4} )")
    REGEX_DAIL_MOTION_TOKEN: re.Pattern = re.compile(r"(_E([0-9]{3,4})_)")

# Usage in tatortprefixmatchrule.py:
class TatortPrefixMatchRule(EpisodeMatchRule):
    def try_match(self, filename: str, episode: "Episode") -> bool | None:
        filename_match = TarenDefines.REGEX_TATORT_PREFIX.search(filename)
        if not filename_match:
            return None
        filename_id: int = int(filename_match.group(2))
        return episode.episode_id == filename_id
```

**Impact**: Minimal performance gain (regex compile cache is automatic in Python 3.7+), but improves code organization.

---

## Configuration Gaps - Examples

### Gap 1: HTTP Settings Not Configurable

**Current (hardcoded defaults):**

```python
# requestshttpfetchpolicy.py line 34-35
class RequestsHttpFetchPolicy(HttpFetchPolicy):
    def __init__(self, timeout_seconds: float = 10.0, retries: int = 1) -> None:
        self._timeout_seconds: float = timeout_seconds
        self._retries: int = max(1, retries)
```

**Problem**: Users cannot configure these values from TaRen.json

**Solution**:

```python
# In tarendefines.py
CFG_KEY_HTTP_TIMEOUT: str = "http_timeout_seconds"
CFG_KEY_HTTP_RETRIES: str = "http_retries"

# In tarenconfig.py setup()
def setup(self) -> bool:
    # ... existing setup ...
    self.add(
        TarenDefines.CFG_SECTION_TAREN,
        TarenDefines.CFG_KEY_HTTP_TIMEOUT,
        "10.0"
    )
    self.add(
        TarenDefines.CFG_SECTION_TAREN,
        TarenDefines.CFG_KEY_HTTP_RETRIES,
        "1"
    )
    return True

# In tarenruntimebuilder.py
def build_runner(self, config: TarenConfig) -> TaRen:
    timeout = float(config.value_get(
        TarenDefines.CFG_SECTION_TAREN,
        TarenDefines.CFG_KEY_HTTP_TIMEOUT
    ))
    retries = int(config.value_get(
        TarenDefines.CFG_SECTION_TAREN,
        TarenDefines.CFG_KEY_HTTP_RETRIES
    ))
    fetch_policy = RequestsHttpFetchPolicy(
        timeout_seconds=timeout,
        retries=retries
    )
    # ... use fetch_policy when constructing TaRen ...
```

---

## Documentation Improvement Examples

### Gap: Complex Trash Move Logic

**Current (taren/trash.py, lines 150-170):**

```python
def move(self, file: str) -> bool:
    """Move file to trash and modify file date to deletion timestamp"""

    filenameWithPath, fileExtension = os.path.splitext(file)
    filenameRaw: str = os.path.basename(filenameWithPath)

    searchmask: str = filenameRaw + "*" + fileExtension
    dstVariants: list[str] = fnmatch.filter(os.listdir(self._trashfolder), searchmask)
    if len(dstVariants) == 0:
        dst = os.path.join(self._trashfolder, (filenameRaw + fileExtension))
    else:
        dst = os.path.join(
            self._trashfolder,
            (filenameRaw + "_" + str(len(dstVariants)) + fileExtension),
        )
    # ... rest of implementation ...
```

**Issue**: Unclear why variants are named this way

**Improved**:

```python
def move(self, file: str) -> bool:
    """
    Move file to trash with automatic collision handling.

    If a file with the same name already exists in trash, appends a counter:
    - First conflict: filename_1.ext
    - Second conflict: filename_2.ext
    - etc.

    Also updates the file modification time to the current time for age-based cleanup.

    Args:
        file: Fully qualified path to file to move

    Returns:
        True if move succeeded, False if OSError occurred
    """
```

---

## Type Safety Gaps - Examples

### Gap 1: Missing Return Type Annotation

**Current (stats.py):**

```python
def __str__(self):  # ← Missing return type
    """Represent statistics as deterministic key-value format"""
    owned_pct: float = (100.0 / self.episodes_total * self.episodes_owned) if self.episodes_total else 0.0
    lines = [
        f"episodes_total: {self.episodes_total}",
        # ...
    ]
    return "\n".join(lines)
```

**Fixed:**

```python
def __str__(self) -> str:  # ← Explicit return type
    """Represent statistics as deterministic key-value format"""
    # ... implementation ...
```

### Gap 2: Unchecked Type in Tuple Unpacking

**Current (episode.py, line 113):**

```python
table_cells: list[Tag] = table_row.find_all("td")
if len(table_cells) < 6:
    logger.debug("skip malformed episode table row with [%s] cells", len(table_cells))
    continue
episode_data: list[str] = [i.text.replace("\n", "") for i in table_cells]
```

**Issue**: `Tag.text` type not explicitly checked

**Safer approach:**

```python
table_cells: list[Tag] = table_row.find_all("td")
if len(table_cells) < 6:
    logger.debug("skip malformed episode table row with [%s] cells", len(table_cells))
    continue
episode_data: list[str] = [
    str(cell.text).replace("\n", "") if cell.text else ""
    for cell in table_cells
]
```

---

## Error Handling Strategy Recommendations

### Current Strategies Mixed:

| Method             | Example                                 | Pro             | Con               |
| ------------------ | --------------------------------------- | --------------- | ----------------- |
| **Boolean Return** | `Helper.ensure_directory()`             | Simple          | Hides stack trace |
| **Null/None**      | `RequestsHttpFetchPolicy.fetch()`       | Clear intention | Must check        |
| **Null Object**    | `Episode.empty_instance()`              | Elegant         | Silent errors     |
| **Result Object**  | `ConflictResolutionResult`              | Explicit        | More boilerplate  |
| **Exception**      | `TarenConfig.validate()` (returns list) | Standard        | May hide failures |

### Recommended Unified Approach:

**Create Exception Hierarchy:**

```python
# taren/exceptions.py
class TarenError(Exception):
    """Base exception for all TaRen errors."""
    pass

class ConfigError(TarenError):
    """Configuration validation or loading failed."""
    pass

class NetworkError(TarenError):
    """Network operation (HTTP fetch) failed."""
    pass

class FileSystemError(TarenError):
    """File system operation failed."""
    pass

class FileConflictError(TarenError):
    """Conflict resolution required."""
    pass

# Usage:
class RequestsHttpFetchPolicy(HttpFetchPolicy):
    def fetch(self, url: str, headers: dict[str, str]) -> bytes:
        for attempt in range(1, self._retries + 1):
            try:
                response = requests.get(url, headers=headers, timeout=self._timeout_seconds)
                response.raise_for_status()
                return response.content
            except requests.RequestException as e:
                if attempt == self._retries:
                    raise NetworkError(f"Failed to download {url} after {self._retries} attempts: {e}") from e
                logger.warning(f"Attempt {attempt}/{self._retries} failed for {url}: {e}")
```

---

## Summary: Next Steps

### Phase 1: Critical (This Week)

- [ ] Add unit tests for 5 match rules (~30 min)
- [ ] Add SizeBasedConflictStrategy tests (~20 min)
- [ ] Add error scenario tests to main workflow (~60 min)
- [ ] Fix missing explicit returns (~10 min)

### Phase 2: Quality (Next Week)

- [ ] Standardize error handling approach (~4 hours)
- [ ] Add type annotations to remaining methods (~2 hours)
- [ ] Consolidate string formatting to f-strings (~1 hour)
- [ ] Make HTTP settings configurable (~2 hours)

### Phase 3: Polish (Following Week)

- [ ] Create ARCHITECTURE.md (~2 hours)
- [ ] Consolidate character stripping logic (~1 hour)
- [ ] Add performance logging (~1 hour)
- [ ] Expand README with examples (~2 hours)
