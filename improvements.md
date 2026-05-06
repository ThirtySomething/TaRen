# TaRen Python Analysis - Fresh Snapshot (2026-05-05)

This report was rebuilt from scratch against the current workspace state.

## Verified Fixed

- `taren/trash.py` - Removed duplicate `os.path.join` in `move()`.
- `taren/stats.py` - Guarded division-by-zero in `__str__()`.
- `taren/taren.py` - Replaced Windows-only path separator logic in `_sanitize_path()`.
- `taren/taren.py` - Unified early returns in `rename_process()` to match `-> None`.
- `taren/websitecache.py` - Added HTTP error handling in `_write_to_cache()`.
- `taren/team.py` - Fixed `_strip_invalid_characters()` iteration and call path.
- `taren/grouping.py` - Replaced invalid config attribute access in `_buildDocument()`.
- `taren/taren.py` - Removed duplicate `EpisodeList` object creation in rename flow.
- `taren/websitecache.py` - Added post-download cache existence guard in `get_website_from_cache()`.
- `taren/taren.py` - Replaced anonymous two-item lists with named task structure.
- `taren/downloadlist.py` - Removed duplicate extension sanitization.
- Project-wide - Replaced `self: object` with idiomatic `self`.
- `taren/team.py`, `taren/trash.py` - Removed Yoda conditions.
- Project-wide - Standardized active logging calls to lazy `%s`/`%d` style.
- `taren/episodelist.py`, `taren/teamlist.py` - Added guards for empty cache content and missing table before parsing.
- `taren/episode.py`, `taren/team.py` - Updated `__gt__` to return `NotImplemented` for unsupported types.
- `taren/helper.py` - Added `ensure_directory()` and made `delete_file()` honor bool return contract with logging.

---

## Open Bugs / Risks

### Critical

### `taren/episode.py` - parse can crash on short or malformed row data

- `parse()` only checks `len(data_row) == 0`, but later reads indices `0..5` unconditionally.
- `re.search(...).group(1)` is called without checking that the match exists.
- Result: `IndexError` or `AttributeError` on malformed wiki row content.

### `taren/team.py` - parse can crash on short or malformed row data

- Same failure shape as episode parsing: direct indexing (`0..5`) and unchecked `re.search(...).group(...)` access.
- Result: `IndexError` or `AttributeError` during team extraction.

### High

### `taren/taren.py` - existing-file collision branch can move same target twice

In the `if os.path.exists(new_fqn)` block, the size checks are three standalone `if` statements.

- `size_old == size_new` moves `new_fqn` to trash.
- Then `size_old > size_new` is checked in a separate `if` and can execute independently in future edits.

Current numeric logic means equality does not satisfy `>`, but this structure is fragile and easy to regress. Converting to `if / elif / else` removes ambiguity and prevents accidental double-move logic.

### Medium

### `taren/grouping.py` - process is functionally incomplete

`process()` resolves episode/team matches and only logs them. It does not build `documentData` and does not call `_buildDocument()`, so no output grouping artifact is produced.

### `taren/episodelist.py`, `taren/teamlist.py` - row content is not validated before parse

Empty or header-only rows produce empty `td` lists, but parsers still call `parse()`.

- Current behavior relies on downstream parse methods, which currently assume at least 6 fields.
- Add `len(table_cells) < 6: continue` in list builders for local robustness.

### `taren/tarenconfig.py` - setup return contract mismatch

`setup()` is annotated `-> bool` but returns no value on any path.

### `taren/tarenconfig.py` - fragile import bootstrapping

Config currently mutates `sys.path` to load `MDO` from a relative vendor directory. This is brittle across entrypoints and packaging contexts.

### Low

### `taren/trash.py`, `taren/websitecache.py`, `taren/episode.py`, `taren/team.py` - typing/annotation quality gaps

Current diagnostics show multiple type issues (module-as-type annotations, unchecked `Match | None`, and mismatched inferred types). These are mostly maintainability concerns but can hide real defects.

---

## Suggested Next Fix Order

1. Harden `Episode.parse()` and `Team.parse()` against short rows and missing regex matches.
2. Rewrite size-comparison branch in `rename_process()` to explicit `if / elif / else`.
3. Complete `Grouping.process()` or remove/disable feature path until implemented.
4. Fix `TarenConfig.setup()` return type/behavior and reduce `sys.path` mutation.
5. Clean remaining typing issues to improve static analysis signal quality.
