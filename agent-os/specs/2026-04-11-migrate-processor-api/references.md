# References for Migrate Processor Off the Node-Based API

## ProcessorService (upstream)

- **Location:** `tstring-html/tdom/processor.py`
- **Key methods:**
  - `ProcessorService` (lines 512–532) — frozen dataclass, fields: parser_api + escape callbacks
  - `process_template()` (lines 527–538) — entry point, calls `_process_tnode`
  - `_process_component()` (lines 681–739) — method to override; invokes components
  - `_prep_component_kwargs()` (lines 386–414) — module-level function, builds kwargs from attrs + children
  - `extract_embedded_template()` (lines 911+) — extracts children Template from parent template
  - `CachedParserService` (lines 501–508) — use for instantiation

## Upstream Context Commits

- `4af611f` — "Experimental system context implementation" (Feb 22 2026): Added `system: dict` to `ProcessContext`, threaded via `system_kwargs` to components. This is the approach we studied.
- `f92d5ca` — "Drop system support" (Apr 10 2026): Removed `system` entirely. tdom explicitly does not want framework context in the processor.

## tdom-svcs DI Infrastructure

- `src/tdom_svcs/processor.py` — current stub (delegating to tdom.html)
- `src/tdom_svcs/types.py` — `DIContainer` protocol, `is_di_container()` TypeGuard
- `svcs_hopscotch.injectors.KeywordInjector` — injects Inject[T] fields; for classes returns instance, for functions calls and returns result
- `svcs_di.auto.get_field_infos` — detects Inject[T] / Resource[] fields on callables
