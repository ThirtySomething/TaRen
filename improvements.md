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

### Implemented Baseline Patterns

1. Strategy Pattern - Rename Conflict Resolution
2. Template Method Pattern - Rename Workflow Pipeline
3. Command Pattern - File System Mutations
4. Repository/Adapter Pattern - Episode Source Access
5. Null Object Pattern - Episode Sentinel

The five baseline patterns above are implemented and stable.

---

## Fresh Proposals (From-Scratch Pass)

### 1. Chain of Responsibility - Episode Filename Matching

Status:

- Implemented.

Implementation summary:

- `taren/episode.py` now defines an `EpisodeMatchRule` protocol and rule handlers for each matching strategy.
- `Episode.matches()` now executes an ordered rule chain and returns on first decisive rule result.
- Existing matching behavior is preserved while making rule order explicit and extensible.

Where it fits:

- `Episode.matches()` currently runs a hardcoded sequence of matching checks (exact, numeric prefixes, dailymotion token, normalized title).

Why applicable:

- Matching rules are likely to evolve by source/provider and are currently tightly coupled to method order.

Adopted steps:

1. Introduced `EpisodeMatchRule` protocol with `try_match(filename, episode) -> bool | None`.
2. Moved each existing match branch into one rule object.
3. Execute rules in order until one returns `True` or `False`.

Observed benefit:

- Cleaner extension for new providers without growing a single method into a large conditional chain.

### 2. Builder Pattern - Runtime Assembly in Composition Root

Status:

- Implemented.

Implementation summary:

- `program.py` now defines `TarenRuntimeBuilder` with explicit steps for config, logger, and runner creation.
- Builder returns a `TarenRuntime` object containing assembled startup/runtime components.
- Entry point now uses `main()` + builder instead of module-level assembly side effects.

Where it fits:

- `program.py` currently performs config setup, logging setup, and runtime object creation inline.

Why applicable:

- Startup concerns (config, logging, runner creation) are cohesive but currently scattered in top-level script code.

Adopted steps:

1. Added `TarenRuntimeBuilder` with steps for config and logging creation.
2. Build `TaRen` instance and return `TarenRuntime` (`runner`, `config`, `logger`).
3. Keep `program.py` as a thin `main()` calling the builder.

Observed benefit:

- Easier testing of startup wiring and cleaner command-line or alternate entrypoint support.

### 3. Policy/Strategy Pattern - HTTP Retrieval Behavior

Status:

- Implemented.

Implementation summary:

- `taren/websitecache.py` now defines `HttpFetchPolicy` and default `RequestsHttpFetchPolicy`.
- `RequestsHttpFetchPolicy` encapsulates timeout/retry behavior for HTTP fetches.
- `WebSiteCache` now accepts an injected fetch policy and delegates network retrieval through it.
- `CachedHtmlEpisodeSource` / `EpisodeList` accept optional fetch-policy injection and pass it through to cache retrieval.

Where it fits:

- `WebSiteCache._write_to_cache()` has fixed request behavior (single call, no retry/backoff policy, no timeout configuration path).

Why applicable:

- Network access rules vary by runtime constraints and should be configurable without changing cache internals.

Adopted steps:

1. Introduced `HttpFetchPolicy` (`fetch(url, headers) -> bytes | None`).
2. Added `RequestsHttpFetchPolicy` with timeout + retry behavior.
3. Injected policy into `WebSiteCache` and through `CachedHtmlEpisodeSource` / `EpisodeList`.

Observed benefit:

- Better resilience and clearer control over network behavior in unstable environments.

### 4. Factory Method - File Mutation Command Creation

Status:

- Implemented.

Implementation summary:

- `taren/taren.py` now provides `_build_commands_for_task(...)` as explicit factory method for file-mutation commands.
- `_process_tasks()` now delegates command object construction to that method.
- Command creation policy is now isolated from task orchestration logic.

Where it fits:

- `TaRen._process_tasks()` still directly constructs concrete command objects.

Why applicable:

- Command creation logic is now centralized enough to extract and support variants (dry-run commands, audit commands, rollback-capable commands).

Adopted steps:

1. Added `_build_commands_for_task(...) -> list[FileMutationCommand]` in `TaRen`.
2. Moved direct `MoveToTrashCommand` / `RenameFileCommand` construction into that method.
3. Added unit coverage for command factory variants.

Observed benefit:

- Keeps `_process_tasks()` focused on orchestration and prepares cleaner dry-run extensions.

---

## Priority Order for Proposed Patterns

All proposed patterns in this report are now implemented.

---

## Recommendation

Continue making incremental improvements in small, test-backed commits.

---

## Structural Convention Update

- Completed: each class/protocol/helper now resides in its own lowercase-named file across source and tests.
- Runtime startup classes were split out of `program.py` into dedicated modules (`tarenruntime.py`, `tarenruntimebuilder.py`).
- Cache HTTP abstractions were split so `WebSiteCache` is now the only class in `taren/websitecache.py`.
- Test helper doubles were moved into dedicated files under `tests/` and reused via imports.
