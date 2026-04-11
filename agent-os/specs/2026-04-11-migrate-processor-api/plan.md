# Migrate Processor Off the Node-Based API

## Summary

Rewrite `processor.py` by subclassing `ProcessorService` from tstring-html and overriding
`_process_component` to add DI concerns: context threading, `Inject[T]` resolution via
`KeywordInjector`, and implementation overrides via `_get_implementation`. Use `contextvars`
to carry the DI container through processing. Drop the `config=` parameter — config is a service in the container.
