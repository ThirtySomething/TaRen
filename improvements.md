# TaRen Code Analysis — Improvement Notes

## Fixed

- `taren/trash.py` — Double `os.path.join` in `move()` ✓
- `taren/stats.py` — Division by zero in `__str__` ✓
- `taren/taren.py` — Windows-only path separator in `_sanitize_path` ✓
- `taren/taren.py` — Inconsistent return type in `rename_process` ✓
- `taren/websitecache.py` — No HTTP error handling in `_write_to_cache` ✓
- `taren/team.py` — `_strip_invalid_characters` iteration bug + never called from `parse()` ✓
- `taren/grouping.py` — Non-existent attribute `taren_downloads` in `_buildDocument` ✓
- `taren/taren.py` — `EpisodeList` and `DownloadList` fetched twice ✓
- `taren/websitecache.py` — `get_website_from_cache` reads cache even after failed download ✓
- `taren/taren.py` — `downloads_to_process` uses anonymous two-element lists ✓

---

## Redundancy / Design Issues

### `taren/downloadlist.py` — Duplicate extension sanitization

`TaRen.__init__` calls `_sanitize_extension` before passing the extension to `DownloadList`, and `DownloadList.__init__` sanitizes it again. Pick one location.

---

### `taren/grouping.py` — `process()` is incomplete

The method iterates downloads, finds episodes and teams, logs them — but **never calls `_buildDocument`** and never builds the `documentData` dict. The method produces no output.

---

## Code Style / Minor Issues

### Yoda conditions throughout

Non-Pythonic comparisons like `0 == len(dstVariants)`, `None == team_period_raw.group(1)` are used instead of `len(dstVariants) == 0` / `team_period_raw.group(1) is None`.

### `self: object` annotation on every method

Annotating `self` as `object` is unconventional in Python and adds visual noise. The standard is an unannotated `self`.

### `__gt__` raises generic `Exception`

Both `Episode.__gt__` and `Team.__gt__` raise `Exception("Cannot compare …")`. Python convention is to raise `TypeError` (or return `NotImplemented`) for type mismatches in comparison operators.

### Inconsistent logging format strings

Some log calls use `.format()`, some use `%`-style (`logging.info("msg: [%s]", value)`). Pick one style. The `%`-style is preferred for `logging` because arguments are only formatted if the message is actually emitted.

### Wrong type annotations for BeautifulSoup objects

In `episodelist.py` and `teamlist.py`:

```python
table: str = websitedata.find("table")   # actually bs4.Tag
rows: list[str] = table.find_all("tr")   # actually list[bs4.Tag]
```

### Commented-out dead code

Multiple blocks of commented-out code exist across several files (e.g. alternative inspector-stripping regex in `episode.py`, disabled `grouping.process()` calls in `taren.py` and `program.py`). These should either be restored or removed.

### `helper.py` — `ensureDirectory` violates PEP 8 naming

`ensureDirectory` should be `ensure_directory`. All other methods in the project use `snake_case`.

### `helper.py` — `delete_file` silently propagates `OSError`

No error handling; callers assume the file was deleted. At minimum the exception should be logged before propagating.
