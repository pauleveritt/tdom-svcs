# Rebaseline tdom-svcs Against Merged tdom Main

## Goal

Update `tdom-svcs` to target the processor extension API that landed in
`t-strings/tdom` PR #118 (`Component Process API Remix`, squash commit `b2287f1`,
merged 2026-05-03). This replaces the current local dependency on Ian Wilson's
`ian/integrations` branch at `6fb4227`.

The rebaseline should be direct: no compatibility shim for the old local branch.
`tdom` main is the source of truth.

## Background

`tdom-svcs` currently plugs into a local `tdom` checkout whose processor API still has:

- `DefaultAppState`
- generic `IComponentProcessor[T]` and `TemplateProcessor[T]`
- an `app_state` argument threaded through `TemplateProcessor.process()` and
  `ComponentProcessor.process()`
- a `ComponentProcessor.process()` return value of
  `(Template, ComponentObject | None)`

PR #118 made a final simplification pass after the local `6fb4227` commit. The merged
API removes `app_state`, `DefaultAppState`, generic processor parameters, and
component-object capture. The extension point remains `ComponentProcessor.process()`,
but its contract is now:

```python
def process(
    self,
    template: Template,
    last_ctx: ProcessContext,
    component_callable: object,
    attrs: tuple[TAttribute, ...],
    component_template: Template,
    provided_attrs: tuple[Attribute, ...] = (),
) -> Template:
    ...
```

The useful subclassing surface from `6fb4227` survived:

- `_prep_component_kwargs()` accepts `raise_on_missing` and
  `raise_on_requires_positional`.
- `provided_attrs` remains a fallback channel.
- `_resolve_t_attrs()` and `get_callable_info()` are still available.

## Decisions

1. **No backwards compatibility.** The code will target merged `tdom` main only.
2. **Preserve Option C.** `tdom-svcs` will continue to resolve DI through
   Hopscotch, compute a `di_fill` fallback tuple, and delegate invocation to
   `super().process()`.
3. **Keep the container-as-field architecture.** `DIComponentProcessor` keeps
   `container: svcs.Container | None` as a frozen field. `html()` keeps resolving or
   lazily registering a per-container `TemplateProcessor`.
4. **Remove component-object capture as a contract.** Factory components still
   render because upstream invokes callable component objects internally, but
   `tdom-svcs` no longer observes or promises access to constructed instances.
5. **Refresh docs in the same item.** Stale research notes should be marked as
   superseded by PR #118 where they discuss removed API shapes.

## Architecture

`tdom_svcs.processor.html()` remains the public entry point:

```python
def html(template: Template, *, container: svcs.Container | None = None) -> str:
    if container is None:
        return tdom.html(template)

    try:
        tp = container.get(TemplateProcessor)
    except svcs.exceptions.ServiceNotFoundError:
        tp = _make_processor(container)
        container.register_local_value(TemplateProcessor, tp)

    return tp.process(template, ProcessContext())
```

`_make_processor()` continues to create a `TemplateProcessor` with
`DIComponentProcessor(container=container)`, `slash_void=True`, and
`uppercase_doctype=True`.

`DIComponentProcessor.process()` changes to the merged PR #118 signature and returns
`Template`:

```python
@dataclass(frozen=True)
class DIComponentProcessor(ComponentProcessor):
    container: svcs.Container | None = None

    def process(
        self,
        template: Template,
        last_ctx: ProcessContext,
        component_callable: object,
        attrs: tuple[TAttribute, ...],
        component_template: Template,
        provided_attrs: tuple[Attribute, ...] = (),
    ) -> Template:
        ...
```

The internal flow remains:

1. If `container is None`, delegate directly to `super().process(...)`.
2. If `component_callable` is a type, resolve component-level Protocol to
   implementation with `_get_implementation(container, component_callable)`.
3. If the callable has no Hopscotch DI fields, delegate directly to
   `super().process(...)`.
4. Pre-prep partial kwargs using upstream's helpers:

   ```python
   partial_kwargs = _prep_component_kwargs(
       get_callable_info(component_callable),
       _resolve_t_attrs(attrs, template.interpolations),
       children=component_template,
       provided_attrs=provided_attrs,
       raise_on_missing=False,
       raise_on_requires_positional=False,
   )
   ```

5. Resolve full Hopscotch kwargs with `build_resolved_kwargs()` and
   `HopscotchInjector(container)._resolve_field_value_sync`.
6. Compute `di_fill` from resolved values not already present in `partial_kwargs`.
7. Delegate invocation to `super().process(..., provided_attrs=di_fill +
   provided_attrs)`.

This keeps the existing precedence rule:

1. Template attrs
2. Existing `provided_attrs`
3. DI-resolved fallback values
4. Dataclass or callable defaults

## Code Changes

Update `src/tdom_svcs/processor.py`:

- Remove imports of `DefaultAppState` and `ComponentObject`.
- Update `DIComponentProcessor.process()` to the new argument list.
- Return `Template` instead of `(Template, ComponentObject | None)`.
- Remove all `app_state` parameters from `super().process()` calls.
- Change `html()` to call `tp.process(template, ProcessContext())`.
- Update comments that mention component-object capture.

Update type-level references:

- Replace `IComponentProcessor[None]` with `IComponentProcessor`.
- Remove any local type aliases or comments that assume `TemplateProcessor[T]`.

## Tests

Keep behavior coverage for the Hopscotch resolution surface:

- `Inject[T]`
- `Resource[T]`
- `Get[T, Attr]`
- `Inject[svcs.Container]`
- locator-aware `Inject[Protocol]`
- component-level Protocol to implementation override
- required DI fields without template attrs
- no-DI fast path

Rewrite the component-object capture test. The replacement should use a dataclass
factory component with an injected service and assert rendered output, not captured
instance identity.

Example intent:

```python
@dataclass
class FactoryComponent:
    svc: Inject[Service]

    def __call__(self) -> Template:
        return t"<p>{self.svc.value}</p>"

result = html(t"<{FactoryComponent} />", container=container)
assert result == "<p>test_value</p>"
```

Update protocol-satisfaction coverage:

```python
_: IComponentProcessor = DIComponentProcessor()
```

## Documentation

Refresh docs as part of the same item:

- `docs/research/port-tstring-html-integrations-revisited.md`: add a clear note that
  PR #118 supersedes the `app_state`, `DefaultAppState`, generic processor, and
  component-object capture sections. Keep the historical analysis intact.
- `docs/research/di-context-threading.md`: keep the container-as-field and
  per-container `TemplateProcessor` decision, but update final snippets to remove
  `app_state=None`.
- `docs/superpowers/roadmap.md`: keep Phase 8 as history and item 37 as the
  authoritative next step.
- `src/tdom_svcs/processor.py` module docstring and comments: describe the current
  container-as-field / per-container processor architecture only.

The backlog upstream asks remain valid with adjusted rationale:

- Publicizing `_prep_component_kwargs()` and `_resolve_t_attrs()` is useful because
  they are practical subclassing surfaces for DI, not because they preserve
  component-object capture.
- A `ComponentProcessor.prep_partial_kwargs()` helper is still optional and
  nice-to-have.

## Verification

Run in `tdom-svcs`:

```bash
just quality
just test
uv run sphinx-build -W -b html docs docs/_build/html
```

Run targeted downstream smoke checks in `themester` after the workspace `tdom`
member moves to merged main.

Run grep checks to confirm executable code no longer references removed API:

```bash
rg "DefaultAppState|IComponentProcessor\\[|app_state=|ComponentObject" src tests examples
```

Documentation may still mention removed terms when marking them as historical or
superseded.

## Non-Goals

- No compatibility with local `ian/integrations`.
- No new middleware API.
- No attempt to recover component-object capture.
- No broad refactor of Hopscotch resolution beyond the signature rebaseline.
- No rename from `tdom` to `tstring-html`; roadmap item 21 covers that separately.

## Risks

- **Private helper dependence:** `tdom-svcs` still imports underscore-prefixed
  helpers from `tdom.processor`. This is already true today. Mitigation: keep the
  imports concentrated in `processor.py` and preserve the backlog upstream ask to
  make the helper surface explicit.
- **Docs drift:** Phase 8 research is detailed and now partly historical.
  Mitigation: add supersession notes instead of rewriting history.
- **Downstream breakage:** `themester` may have code paths that call
  `TemplateProcessor.process(..., app_state=None)` directly. Mitigation: run targeted
  smoke checks and grep for removed API in affected workspace members.

## Success Criteria

- `tdom-svcs` imports and tests against merged `tdom` main.
- `html(template, *, container=None)` public behavior is unchanged.
- Hopscotch DI behavior remains covered by tests.
- Factory components render correctly under DI, without component-object capture.
- Research docs and roadmap make clear that PR #118 supersedes the old local branch
  API assumptions.
