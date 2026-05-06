# TaRen Code Analysis - Fresh Snapshot (2026-05-05)

This report was rebuilt from scratch against the current workspace state.

## Current State

- Project diagnostics are clean for current source files under `taren/`.
- Team, teamlist, and grouping functionality have been removed from runtime flow and source.
- Test suite is in place and covers rename flow, parsing guards, cache fallback, helper/trash behavior, and config setup.

---

## Architecture Notes (As-Is)

- `program.py` is a thin composition root (config + logging + single call into `TaRen.rename_process()`).
- `taren/taren.py` is an orchestration service that coordinates parsing, file discovery, rename decisions, and trash lifecycle.
- Domain/entity-style classes exist (`Episode`, `Stats`) plus infrastructure services (`WebSiteCache`, `Trash`, `DownloadList`, `TarenConfig`).
- Data acquisition and parsing are currently coupled in `EpisodeList` (cache read + HTML parse + model construction).

---

## Applicable Design Patterns

### 1. Strategy Pattern - Rename Conflict Resolution (Implemented)

Implementation summary:

- `taren/taren.py` now defines a `ConflictResolutionStrategy` protocol and uses an injected strategy in `TaRen`.
- Default behavior is provided by `SizeBasedConflictStrategy` and preserves the previous size-based conflict semantics.
- `rename_process()` delegates collision decisions to the strategy and executes returned actions (`move_to_trash`, `skip_rename`).

Where it fits:

- The file-collision decision logic in `TaRen.rename_process()` currently uses inlined conditional branches based on file sizes.

Why applicable:

- Collision behavior is a policy decision that may evolve (keep newest, keep largest, checksum-first, timestamp-first, dry-run).

Adopted steps:

1. Introduced a `ConflictResolutionStrategy` protocol with `resolve(old_fqn, new_fqn) -> result`.
2. Moved prior inlined size-based logic into `SizeBasedConflictStrategy`.
3. Injected strategy into `TaRen` with default fallback to the size-based strategy.

Observed benefit:

- Isolates decision policy from orchestration and makes branch-heavy logic easier to test independently.

### 2. Template Method Pattern - Rename Workflow Pipeline

Where it fits:

- `rename_process()` has a fixed sequence: preflight, fetch metadata, scan downloads, compute actions, execute actions, summarize.

Why applicable:

- Workflow order is stable, but individual steps may vary (dry-run, alternate metadata source, additional validation).

How to apply incrementally:

1. Split `rename_process()` into protected step methods (`_preflight`, `_load_episodes`, `_collect_tasks`, `_process_tasks`, `_finalize`).
2. Keep behavior identical.
3. Optionally add a subclass for dry-run or simulation mode.

Expected benefit:

- Smaller units, clearer extension points, simpler test targeting for each step.

### 3. Command Pattern - File System Mutations

Where it fits:

- Rename/move/delete side effects are performed directly in control flow.

Why applicable:

- Mutations are discrete operations that could support audit logging, dry-run previews, batching, or rollback hooks.

How to apply incrementally:

1. Define command objects (`RenameFile`, `MoveToTrash`, `DeleteFile`) with `execute()`.
2. In planning phase, emit command list.
3. Execute commands with a central runner.

Expected benefit:

- Better observability of planned vs executed actions and safer extension toward preview mode.

### 4. Repository/Adapter Pattern - Episode Source Access

Where it fits:

- `EpisodeList` currently combines source retrieval and parsing concerns.

Why applicable:

- Episode metadata could later come from multiple sources (wiki HTML, local cache only, JSON export, test fixtures).

How to apply incrementally:

1. Introduce `EpisodeSource` interface (`fetch() -> str`).
2. Adapt current `WebSiteCache` usage into `CachedHtmlEpisodeSource`.
3. Keep parser in `EpisodeList` or move to dedicated parser class.

Expected benefit:

- Decouples source mechanics from parsing/model assembly; improves substitution in tests and future integrations.

### 5. Null Object Pattern (formalize existing behavior)

Where it fits:

- `Episode.empty` is already used as a sentinel instead of returning `None` from `find_episode()`.

Why applicable:

- Pattern already exists implicitly; formalizing reduces accidental partial object states.

How to apply incrementally:

1. Add explicit factory/classmethod for empty instances (`Episode.empty_instance()`).
2. Keep `find_episode()` return type unchanged.

Expected benefit:

- Clearer intent, safer construction path, better readability for sentinel usage.

---

## Suggested Implementation Order

1. Template-method style decomposition of `rename_process()`.
2. File operation commands for dry-run readiness.
3. Source adapter separation for episode retrieval/parsing.
4. Null object formalization for `Episode` sentinel behavior.

---

## Recommendation

Do not apply all remaining patterns at once. Continue with workflow decomposition in small commits, keeping behavior and tests unchanged after each step.
