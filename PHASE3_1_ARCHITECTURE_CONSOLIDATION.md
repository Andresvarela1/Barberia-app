# Phase 3.1 - Architecture Consolidation

## Summary

This phase closes the incremental extraction work from stages `1.x` and `2.x` with a small consistency pass instead of opening new refactors.

The goal was to stabilize the current architecture by:

- keeping `app.py` as the final orchestrator;
- aligning the public surface of the extracted feature modules;
- removing cheap redundant wiring and unused module scaffolding;
- documenting the architecture that now exists in practice.

No visible behavior, routing, permissions, or business rules were changed in this phase.

## Current Architecture

### Session, auth, and routing shell

The base flow remains centered on:

- `app_core/auth.py`
  - login/logout/session preparation
  - authenticated session normalization
  - entry/view/render/dispatch resolution
- `app_core/tenancy.py`
  - session defaults
  - public vs authenticated context setup
  - barberia context helpers
- `app.py`
  - final orchestration
  - render group selection
  - shell/content dispatch

### Feature modules extracted so far

- `app_core/agenda/listing.py`
  - agenda listing tab for `ADMIN`
  - agenda listing tab for `SUPER_ADMIN`
  - direct helpers for filters, results, card actions, and calendar result rendering

- `app_core/features/services/rendering.py`
  - `render_services_section(...)`
  - feature-level render entry for the `Servicios` section

- `app_core/features/barberos/rendering.py`
  - `render_barberos_section(...)`
  - feature-level render entry for the `Barberos` section

- `app_core/features/dashboard/rendering.py`
  - `render_admin_dashboard_section(...)`
  - `render_super_admin_dashboard_section(...)`
  - feature-level dashboard render entries for the two administrative roles

## Interfaces and Boundaries

The extracted feature modules now follow a reasonably consistent boundary:

- `app.py` resolves role, active `barberia_id`, and high-level context;
- feature modules receive explicit arguments and render the concrete section;
- feature modules reuse existing DB/services/metrics helpers instead of re-owning business logic.

This means the current architecture is modular by feature at the UI/render boundary, not yet by full domain ownership.

## Small Cleanups Applied in 3.1

This consolidation intentionally kept the code changes small:

- removed unused `logging`/`logger` scaffolding from:
  - `app_core/features/services/rendering.py`
  - `app_core/features/barberos/rendering.py`
- removed an unused second layout binding in:
  - `app_core/agenda/listing.py`

These were safe, local consistency cleanups only.

## Why `app.py` Still Matters

Even after the extractions, `app.py` still owns the final application composition:

- authenticated shell orchestration;
- role-based content dispatch;
- section-level contextual wiring;
- integration points across extracted and non-extracted screens.

That is still a reasonable stopping point for the current stage. The file is no longer carrying all feature implementation directly, which was the main goal of stages `1.x` and `2.x`.

## Real Debt Left for a Later Stage

The remaining debt is now more selective:

1. Non-extracted authenticated sections still live in `app.py`.
2. Agenda is only partially modularized:
   - list tab is extracted,
   - other agenda tabs remain local to `app.py`.
3. Feature modules still depend on explicit callbacks or local integration helpers from `app.py`.
4. There is still some role-specific duplication between `ADMIN` and `SUPER_ADMIN` in non-extracted sections.
5. The current modular boundary is render-first, not full feature/domain ownership.

## Recommendation for a Future Stage

If there is a future stage, it should be chosen deliberately instead of continuing the old plan by inertia.

The next sensible options would be one of these:

1. Stop here and keep the current architecture as the stable baseline.
2. Extract one more operational section only if it has a clean feature boundary.
3. Deepen one already-extracted feature vertically:
   - reduce callback passing,
   - move more local integration logic closer to the feature module,
   - but only one feature at a time.

The main takeaway from `3.1` is that the architecture is now coherent enough to support selective future work without needing another broad refactor first.
