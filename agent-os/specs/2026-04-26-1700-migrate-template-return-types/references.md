# References for Migrate Template Return Types

## Research

- `tdom-svcs/docs/research/port-tstring-html-integrations.md` — Stage 2 plan

## Key Source Files

- `tdom-svcs/src/tdom_svcs/processor.py` — unchanged; handles Template and str|Markup
- `themester/src/themester/layouts/types.py` — Layout protocol (return type changes)
- `themester/src/themester/views/__init__.py` — get_view() (adds html() call)
- `themester/src/themester/cli/layout_generate.py` — generated code update
- `tdom-svcs/tests/test_di_injection.py` — component definitions to migrate
- `themester/tests/views/test_registry.py` — view definitions to migrate
