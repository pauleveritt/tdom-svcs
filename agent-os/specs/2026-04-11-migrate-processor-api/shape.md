# Migrate Processor Off the Node-Based API — Shaping Notes

## Scope

Roadmap item 20. Rewrite `processor.py` so `html()` returns `str | Markup` via a
`DIProcessorService` subclass of upstream `ProcessorService`, restoring the 48 tests
that were stubbed in item 18.

## Decisions

- **Drop `config=`** — single `context=` parameter. Config is a service in the container.
- **`contextvars` for DI context** — store container in a ContextVar during processing.
  Thread-safe, no changes to upstream API needed.
- **Subclass `ProcessorService`** — override `_process_component` only. Other processing
  methods (elements, text, comments) delegate to base class.
- **Pre-render children** — render children template to `Markup` before passing to
  components. Component tests that iterated over children tuple need updating.
- **Handle `str | Markup` returns** — existing tdom-svcs components return `str | Markup`
  from `__call__`, not `Template`. Our override accepts these directly.
- **`_prep_component_kwargs` is module-level** — must replicate its attr/children logic
  in our override (can't override it by subclassing).

## Upstream Context Analysis

tstring-html removed context-passing three times (Jun 2025, Sep 2025, Feb 2026). The
most recent `system: dict` on `ProcessContext` was added Feb 22 and removed Apr 10
(yesterday). README recommends `contextvars` for framework-level context. No extension
points exist in current tstring-html.

## Context

- **Visuals:** None
- **References:** `tstring-html/tdom/processor.py` (ProcessorService, _process_component,
  _prep_component_kwargs, extract_embedded_template)
- **Product alignment:** Phase 6 item 20 — prerequisite for any future work on item 21+
