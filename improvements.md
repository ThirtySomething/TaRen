# TaRen Code Analysis — Improvement Notes

## Bugs

### `taren/trash.py` — Double `os.path.join` in `move()`

The `dst` variable is built with `os.path.join(self._trashfolder, filename)` inside the if/else block and then unconditionally joined with `self._trashfolder` **again** on the next line, producing a broken path.

```python
# Bug: dst already contains the full path
dst: str = os.path.join(self._trashfolder, dst)
```

Fix: remove the duplicate join, or build only the filename in the if/else and join once at the end.

---

### `taren/team.py` — `_strip_invalid_characters` iteration bug

```python
for index, inspector in self.team_inspectors:   # wrong: unpacking a str
```

`self.team_inspectors` is `list[str]`; iterating it yields strings, not `(index, str)` pairs. Should be `enumerate(self.team_inspectors)`. This method is also **never called** from `parse()`, unlike the equivalent method in `Episode`.

---

### `taren/grouping.py` — Non-existent attribute access

`_buildDocument` references `self._config.taren_downloads`, but `TarenConfig` (MDO subclass) exposes configuration only through `value_get("taren", "downloads")`. This raises `AttributeError` at runtime.

---

### `taren/stats.py` — Division by zero in `__str__`

```python
100 / self.episodes_total * self.episodes_owned
```

Raises `ZeroDivisionError` when `episodes_total == 0` (e.g. when the web request fails). Add a guard: `(100 / self.episodes_total * self.episodes_owned) if self.episodes_total else 0.0`.

---

### `taren/taren.py` — Windows-only path separator in `_sanitize_path`

```python
path = "{}\\".format(path)   # hardcoded backslash
```

This breaks on Linux/macOS. Use `os.sep` or `os.path.join`.

---

### `taren/taren.py` — Inconsistent return type in `rename_process`

The method returns `None` on early exit (path does not exist) but returns `False` when `self._trash.init()` fails. The caller never uses the return value, but the inconsistency is confusing and the return type annotation is missing.

---

### `taren/websitecache.py` — No HTTP error handling in `_write_to_cache`

```python
websitecontent: bytes = requests.get(self._websiteurl, headers=headers).content
```

Network errors and non-2xx responses are silently ignored. Add `.raise_for_status()` and wrap in a `try/except requests.RequestException`.

---

## Redundancy / Design Issues

### `taren/taren.py` — `EpisodeList` and `DownloadList` fetched twice

Both objects are created once for the rename phase and then **created again** for the grouping/HTML phase later in `rename_process`. The second creation triggers duplicate web requests (or cache reads) and duplicate filesystem scans. Reuse the instances from the first pass.

---

### `taren/taren.py` — `downloads_to_process` uses anonymous two-element lists

```python
downloads_to_process.append([current_download, episode])
```

A `dataclasses.dataclass` or `typing.NamedTuple` would make access by name (`.filename`, `.episode`) safer than by index (`[0]`, `[1]`).

---

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
