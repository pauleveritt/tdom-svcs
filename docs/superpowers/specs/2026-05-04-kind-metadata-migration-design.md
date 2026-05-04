# tdom-svcs Kind Metadata Migration Design

Date: 2026-05-04

## Summary

tdom-svcs re-exports Hopscotch middleware decorators and helpers. Now that Hopscotch records framework roles as single-valued `kind` metadata, tdom-svcs should describe and test `middleware` and `hookable` as kinds instead of role categories.

## Current Shape

`svcs_hopscotch.middleware.middleware` sets `kind = "middleware"`, `hookable` sets `kind = "hookable"`, and `get_middleware_types()` already queries `registry.get_by_kind("middleware")`. tdom-svcs imports and re-exports those names.

The remaining tdom-svcs work is in tests, examples, and docs that still expect `metadata["categories"]` to include role names or query `registry.get_by_category("middleware")` and `registry.get_by_category("hookable")`.

## Design

Middleware and hookable discovery is kind-based:

- `@middleware` stores `metadata["kind"] == "middleware"` and leaves `metadata["categories"]` as `None` unless the caller supplies user categories.
- `@hookable` stores `metadata["kind"] == "hookable"` and leaves role categories out of `metadata["categories"]`.
- Scanning discovers both decorators through Hopscotch injectable metadata.
- Role queries use `registry.get_by_kind("middleware")` and `registry.get_by_kind("hookable")`.
- User facets such as `security`, `auth`, `page`, and `settings` remain categories and continue to use `registry.get_by_category(...)`.

## Scope

In scope:

- Update tdom-svcs tests for kind metadata and user-only categories.
- Update examples that query all middleware or all hookables.
- Update current docs that teach role-category discovery.
- Run `just test` and `just quality`.

Out of scope:

- Changing svcs-hopscotch middleware implementation.
- Adding compatibility category aliases.
- Broad type or documentation cleanup unrelated to middleware/hookable role discovery.
