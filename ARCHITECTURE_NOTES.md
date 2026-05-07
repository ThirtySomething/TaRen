# TaRen Architecture Notes

**Version:** Current (May 2026)
**Target Python:** 3.11
**Test Count:** 116 passing

---

## System Overview

TaRen is a specialized file renaming application that matches downloaded media files against Wikipedia episode data and renames them according to a template pattern.

### Main Components

```
program.py
  └─> TarenRuntimeBuilder
       ├─> TarenConfig (configuration loading + validation)
       ├─> logging setup (UTF-8 safe, idempotent)
       └─> TaRen (main orchestrator)
            └─> TaRen.rename_process()
                 ├─> _preflight() [fail-fast checks]
                 ├─> _load_episodes() [fetch + parse from web]
                 ├─> _collect_tasks() [match files to episodes]
                 ├─> _process_tasks() [execute renames/moves]
                 └─> _finalize() [cleanup, stats]
```

---

## Design Patterns Used

### 1. Strategy Pattern

**Use:** Conflict resolution when file already exists

```
ConflictResolutionStrategy (interface)
  └─> SizeBasedConflictStrategy (keeps larger file)
```

**Location:** `taren/sizebasedconflictstrategy.py`
**Test:** `tests/test_sizebasedconflictstrategy.py` (4 tests)

### 2. Command Pattern

**Use:** File operations (rename, move to trash) as encapsulated commands

```
FileMutationCommand (abstract)
  ├─> RenameFileCommand
  └─> MoveToTrashCommand
```

**Location:** `taren/*command.py`
**Test:** `tests/test_taren.py` (integration tests)

### 3. Chain of Responsibility

**Use:** Episode matching with short-circuit evaluation

```
Episode.matches(filename)
  └─> tries each rule in sequence:
       ├─> ExactRepresentationMatchRule
       ├─> LeadingNumberMatchRule
       ├─> DailymotionTokenMatchRule
       ├─> TatortPrefixMatchRule
       └─> EpisodeNameContainsRule (fallback, guards empty names)
```

**Location:** `taren/episode.py`, `taren/*matchrule.py`
**Test:** `tests/test_match_rules.py` (35 tests)

### 4. Adapter Pattern

**Use:** Wrap cache with HTTP fetch policy

```
EpisodeList
  └─> EpisodeSource (interface)
       └─> CachedHtmlEpisodeSource
            └─> WebSiteCache + HttpFetchPolicy
```

**Location:** `taren/cachedhtmlepisodesource.py`, `taren/websitecache.py`

### 5. Null Object Pattern

**Use:** Empty episode when no match found

```
Episode.empty_instance()  # Represents "no match"
  └─> has empty string values for all fields
```

**Location:** `taren/episode.py`

---

## Error Handling Architecture

### Exception Hierarchy

```
TarenError (base)
  ├─> NetworkError (HTTP failures)
  ├─> FileSystemError (disk operations)
  └─> ConfigurationError (invalid settings)
```

**Location:** `taren/tarendefines.py`

### Failure Paths

1. **Configuration Errors:** Fail-fast in `program.py` before runtime starts
2. **Preflight Errors:** Checked in `_preflight()` with explicit logging
3. **Runtime Errors:** Logged with context (path, URL, etc.) and graceful fallback
4. **Parse Errors:** Skipped with debug logging (malformed rows ignored)

### Error Signaling Styles

- **Exceptions:** Configuration, file system critical errors
- **Boolean Returns:** Directory creation, file deletion (success/failure)
- **Null Returns:** Episode matching (None = non-decisive)
- **Logging:** All error paths explicitly logged with context

---

## Data Flow

### Episode Matching Flow

```
1. Load episodes from Wikipedia
   └─> EpisodeList.get_episodes()
        ├─> fetch HTML (cached)
        ├─> parse with BeautifulSoup
        └─> extract episode data

2. For each downloaded file:
   └─> EpisodeList.find_episode(filename)
        ├─> Episode.matches(filename)
        │    └─> try each matching rule
        │         └─> return first decisive result
        └─> return Episode or Episode.empty_instance()

3. Build rename tasks
   └─> if episode found AND file exists
        ├─> check for conflicts (compare sizes)
        ├─> create mutation command
        └─> add to task list

4. Execute tasks
   └─> for each command:
        ├─> try rename
        ├─> on error: move to trash instead
        └─> update statistics
```

### Configuration Flow

```
1. Load from JSON file (TarenConfig)
2. Validate (bounds, presence)
3. Raise ConfigurationError if invalid
4. Pass to TaRen for runtime use
```

---

## Critical Invariants

1. **Episode Matching is Non-Exclusive:** Multiple rules can apply; first decisive match wins
2. **Fallback Matching Needs Guards:** Empty episode names must not match (regression prevention)
3. **Logger Setup is Idempotent:** Safe to call build_logger() multiple times
4. **Preflight Must Fail-Fast:** Directory creation failures abort immediately
5. **Trash Cleanup is Age-Based:** Files in trash older than threshold are removed
6. **Cache Expiry is Per-File:** Each cached file has independent age tracking

---

## Performance Characteristics

| Operation                    | Time          | Scaling                              |
| ---------------------------- | ------------- | ------------------------------------ |
| Load episodes from Wikipedia | ~1-3s         | O(1) per season (network bound)      |
| Cache lookup (disk)          | <100ms        | O(1) (file timestamp check)          |
| Episode matching             | <1ms per file | O(n) where n = number of episodes    |
| File rename                  | <100ms        | O(1) (filesystem bound)              |
| **Total for 100 files**      | ~30-50s       | Dominated by network (unless cached) |

### Optimization Opportunities

- Parallel file processing (implemented with bounded thread pool)
- Episode list pagination for large seasons
- Batch Wikipedia requests (if API available)

---

## Testing Strategy

### Test Scope

- **Unit tests:** Individual components in isolation (mocked dependencies)
- **Integration tests:** Multi-component flows with mocked file system
- **Edge cases:** Empty values, decode errors, missing files

### Fake Objects (Test Doubles)

- `FakeConfig`: Configurable mock for TarenConfig
- `FakeEpisode`: Pre-configured episode fixtures
- `FakeEpisodeSource`: Returns preset episode lists
- `FakePolicy`: Configurable HTTP response mock
- `FakeTrash`: In-memory trash for testing
- `SpyConflictStrategy`: Records method calls

### Test Organization

- `test_taren.py`: Main orchestrator (24 tests)
- `test_match_rules.py`: Episode matching (35 tests)
- `test_episodelist.py`: Episode parsing (14 tests)
- `test_websitecache.py`: Caching + UTF-8 (9 tests)
- `test_sizebasedconflictstrategy.py`: Conflict resolution (4 tests)
- `test_program.py`: Runtime builder (6 tests)
- `test_*`: Other components (21 tests)

---

## Code Organization

### Modules by Responsibility

**Configuration & Runtime**

- `program.py`: Entry point
- `tarenconfig.py`: Settings loading + validation
- `tarenruntimebuilder.py`: Assembly (config + logger + runner)
- `tarenruntime.py`: Immutable runtime context
- `tarendefines.py`: Constants + exception hierarchy

**Core Orchestration**

- `taren.py`: Main rename process (5-phase pipeline)

**Episode Management**

- `episode.py`: Single episode object + matching logic
- `episodelist.py`: List of episodes + parsing
- `episodesource.py`: Interface for episode providers
- `cachedhtmlepisodesource.py`: Wikipedia adapter

**Episode Matching**

- `episodematchrule.py`: Matching rule interface
- `exactrepresentationmatchrule.py`: Exact episode ID match
- `leadingnumbermatchrule.py`: Episode number prefix
- `dailymotiontokenmatchrule.py`: Dailymotion platform ID
- `tatortprefixmatchrule.py`: "Tatort" TV series prefix
- `episodenamecontainsrule.py`: Fallback substring match (guards empty names)

**File Operations**

- `downloadlist.py`: Find files matching pattern
- `downloadtask.py`: Rename task descriptor
- `filemutationcommand.py`: Abstract file operation
- `renamefilecommand.py`: Rename implementation
- `movetotrashcommand.py`: Trash move implementation
- `helper.py`: File system utilities (mkdir, delete)
- `trash.py`: Trash folder management + cleanup

**Network & Caching**

- `httpfetchpolicy.py`: HTTP fetch interface
- `requestshttpfetchpolicy.py`: Requests library implementation
- `websitecache.py`: Cache with age-based expiry + UTF-8 handling

**Conflict Resolution**

- `conflictresolutionstrategy.py`: Strategy interface
- `sizebasedconflictstrategy.py`: Size comparison strategy

**Utilities**

- `stats.py`: Rename statistics + reporting
- `conflictresolutionresult.py`: Result descriptor

---

## Dependencies

### External

- `requests`: HTTP client with retry policy
- `beautifulsoup4`: HTML parsing
- `MDO` (vendored): Configuration management

### Standard Library

- `logging`: UTF-8 safe logger
- `os.path`: File system operations
- `hashlib`: URL hash for cache naming
- `datetime`: Cache age tracking
- `json`: Configuration file format

### Internal

- `tarendefines.py`: Constants + exceptions (imported everywhere)
- `helper.py`: File system utilities (imported by multiple modules)

---

## Configuration Parameters

**Logging Section**

- `loglevel`: Debug, Info, Warning, Error
- `logfile`: Path to log file (UTF-8 encoded)
- `logstring`: Logger format template

**Taren Section**

- `collection`: Root directory for downloads/seen
- `extension`: File type (e.g., "mp4")
- `maxcache`: Cache age threshold (days)
- `pattern`: TV series pattern (e.g., "Tatort")
- `trashage`: Trash cleanup age threshold (days)
- `trashignore`: Ignore list file in trash
- `wiki`: Wikipedia URL for episode data
- `wiki_useragent`: User-Agent header value
- `http_timeout`: Request timeout (seconds)
- `http_retries`: Retry attempts on network failure

---

## Future Enhancements

### Considered (Not Implemented)

- Batch Wikipedia API requests
- SQLite episode cache (currently filesystem-based)
- Web UI for configuration
- Episode metadata enrichment (broadcast date, cast)

### Likely Candidates

1. Pathlib migration (cleaner path ops)
2. Debug logging consolidation
3. Configuration bounds validation
4. Type annotation completion

---

## Maintenance Notes

- **Code Freeze Period:** All changes should go through review + test validation
- **Test First Approach:** New features should add tests before implementation
- **Version Target:** Python 3.11+ (see pyproject.toml)
- **Code Style:** Black (line-length 88), f-strings, type hints preferred
- **Performance:** Main bottleneck is network (Wikipedia fetch) - consider caching improvements
