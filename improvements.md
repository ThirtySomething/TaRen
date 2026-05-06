# TaRen Code Analysis — Improvement Notes

## Verified Fixed

- `taren/trash.py` — Removed duplicate `os.path.join` in `move()`.
- `taren/stats.py` — Guarded division-by-zero in `__str__()`.
- `taren/taren.py` — Replaced Windows-only path separator logic in `_sanitize_path()`.
- `taren/taren.py` — Unified early returns in `rename_process()` to match `-> None`.
- `taren/websitecache.py` — Added HTTP error handling in `_write_to_cache()`.
- `taren/team.py` — Fixed `_strip_invalid_characters()` iteration and call path.
- `taren/grouping.py` — Replaced invalid config attribute access in `_buildDocument()`.
- `taren/taren.py` — Removed duplicate `EpisodeList` object creation in rename flow.
- `taren/websitecache.py` — Added post-download cache existence guard in `get_website_from_cache()`.
- `taren/taren.py` — Replaced anonymous two-item lists with named task structure.
- `taren/downloadlist.py` — Removed duplicate extension sanitization.
- Project-wide — Replaced `self: object` with idiomatic `self`.
- `taren/team.py`, `taren/trash.py` — Removed Yoda conditions.
- Project-wide — Standardized active logging calls to lazy `%s`/`%d` style.

---

## Open Bugs / Risks

### `taren/grouping.py` — `process()` is incomplete

`process()` only logs team/episode matches and never builds `documentData` or calls `_buildDocument()`, so no output artifact is produced.

### `taren/episodelist.py` and `taren/teamlist.py` — fragile parse path on empty/failed cache

If website download fails, cache methods can return an empty string. Both parsers then do:

```python
table = websitedata.find("table")
rows = table.find_all("tr")
```

When `table` is `None`, this raises `AttributeError` and aborts processing.

---

## Design / Maintainability Issues

### `taren/episode.py` and `taren/team.py` — `__gt__` raises generic `Exception`

Comparison methods should return `NotImplemented` or raise `TypeError` for unsupported types.

### `taren/episodelist.py` and `taren/teamlist.py` — incorrect BeautifulSoup annotations

`table: str` and `rows: list[str]` are incorrect; these are BeautifulSoup tag objects/lists.

### `taren/helper.py` — naming and error contract

- `ensureDirectory` is non-PEP8 in a snake_case codebase.
- `delete_file()` is annotated as returning `bool` but returns nothing and does not log failures.

### Commented-out code blocks still present

Multiple modules keep disabled code paths (e.g., grouping execution in `program.py` and `taren.py`, alternative regex logic in `episode.py`).
