# Port tdom-svcs to `tstring-html` `ian/integrations` — Revisited

*Date: 2026-04-26 (revision)*

**Superseded API note (2026-05-04):** tdom PR #118 merged after this analysis
and removed `app_state`, `DefaultAppState`, generic `IComponentProcessor[T]`, and
component-object capture from the current processor extension API. The Option C
Hopscotch resolution strategy remains the chosen tdom-svcs approach, but current
implementation must target PR #118's non-generic `ComponentProcessor.process()`
signature and `Template` return value.

*Supersedes: `port-tstring-html-integrations.md`*

## Why this revision

Ian's comments on today's port work and the commits he pushed in response have driven
the architecture through three distinct positions over the course of the day. This
revision tracks the final state.

His four prompts across three messages:

> *"Is there a reason you can't use a ContextVar instead of app_state here?"*
>
> *"Why is it not possible to just resolve the component_callable and resolve the extra
> kwargs without have to pass off the entire invocation to the DI system?"*
>
> *"We try to 'capture' the component_object to return and its not clear if that is
> possible in your gist."*
>
> *"I wonder if its possible to just replicate the call to `_prep_component_kwargs` in
> your component processor when needed, but use these new flags, `raise_on_missing=False`,
> and then continue to hopscotch. I don't know how to handle the 'capturing' part."*

His three worked examples in `tstring-html/tdom/processor_integration_test.py` and his
two architectural commits (`7561617 _invoke_component`, then later replaced by
`6fb4227 Add exceptional flags`) lay out the alternatives. This revision evaluates them
against the post-`6fb4227` upstream state and revises the recommendation.

**Two headline architectural changes are warranted:**

1. **Move the container from `app_state` → ContextVar.** `app_state` is for
   user-defined state, not framework infrastructure.
2. **Resolve DI fields through `HopscotchInjector`'s full pipeline, then hand the
   resolved values to `super().process()` as `provided_attrs`.** This preserves all
   of Hopscotch's resolution semantics — `Get[T, Attr]` operators, locator-aware
   `Inject[Protocol]`, `Inject[svcs.Container]` self-injection, adapter fallback,
   defaults — *and* preserves component_object capture via upstream's factory branch.

The original `_invoke_component` upstream hook is no longer in `ian/integrations`. It
was replaced by flags + a merge-order change in `_prep_component_kwargs`. The local
`pauleveritt/invoke-component-hook` branch was deleted (workspace `tstring-html/` now
sits directly on `ian/integrations`).

`Get[T, Attr]` is a load-bearing feature for the user (it replaces the dataclass
`__post_init__` pattern). The architecture below is designed to keep it working — and
to inherit any future Hopscotch resolution features automatically.

## What changed in `ian/integrations` today

These commits in `tstring-html` directly affect the port plan, in chronological order:

| Commit | Author | What it does | Impact on plan |
|---|---|---|---|
| `9adc788` | Ian | Internalize 2nd call for factory components | Subclasses no longer handle factory dance |
| `4a45a5d` | Ian | Rewrite app state test to be more likely usage | Establishes `app_state` as user-defined, not framework |
| `28ce2cd` | Ian | Factor integration tests into separate module | Demonstration patterns isolated |
| `be62f37` | Ian | Add example with well defined `AppState` | Pattern 3 below |
| `27d2cc6` | Ian | Add precedence demo | Proves template attrs override `provided_attrs` |
| `f09fd8e` | Ian | Add cvar+callback example | Pattern 2 below |
| `a877d46` | Ian | `DefaultAppState = None`; simplify `html()` | App state is now genuinely optional |
| `9a5c37c` | Ian | Bring back `assume_ctx` as optional param | Caller can override parser context |
| ~~`7561617`~~ | Paul | ~~Add `_invoke_component` hook~~ | **Reset; Ian preferred a different path** |
| `6fb4227` | Ian | Add `raise_on_missing` / `raise_on_requires_positional` flags + reorder merge in `_prep_component_kwargs` | **The current upstream surface for DI subclassing** |

Two non-obvious changes in `6fb4227` that drive the architecture:

1. **Two flags on `_prep_component_kwargs`**: `raise_on_missing=False` lets a subclass
   ask for partial kwargs without the missing-required check firing. `raise_on_requires_positional=False`
   does the analogous thing for components with positional params.
2. **Merge order reversed in `_prep_component_kwargs`**: previously, `provided_attrs`
   were written first and then template `attrs` overwrote. Now template `attrs` are
   written first and `provided_attrs` *fill gaps* (only set if `pattr_name not in
   kwargs`). The effective precedence is unchanged (template still wins), but the
   semantics are now "provided_attrs are a fallback" rather than "provided_attrs are
   defaults that templates override". This matters for DI: required fields filled via
   `provided_attrs` survive into kwargs, satisfying the missing-required check by the
   time it runs.

Net: upstream now exposes a *kwargs-prep-level* DI extension surface, not a
*call-level* one. The supported pattern is "subclass calls `_prep_component_kwargs`
itself with flags, or feeds `provided_attrs` to a delegated `super().process()`,"
not "subclass overrides the bare invocation."

## The three integration patterns Ian demonstrates

`processor_integration_test.py` now contains three distinct demo classes. They are not
alternatives in the test sense — they are **three composable strategies** an integrator can
pick from. tdom-svcs needs to choose (or combine) one of them.

### Pattern 1 — ContextVar transports system state, custom processor delegates

`TestContextVarIntegration` (`processor_integration_test.py:34-177`):

```python
SystemCtx: ContextVar[SystemState | None] = ContextVar("SystemCtx", default=None)

@dataclass
class SystemComponentProcessor[T](IComponentProcessor[T]):
    default_component_processor_api: IComponentProcessor[T] = field(
        default_factory=ComponentProcessor[T]
    )

    def process(self, ..., component_callable, ..., provided_attrs=()):
        system_ctx = SystemCtx.get()
        if system_ctx is not None and isclass(component_callable) \
                and t.is_protocol(component_callable) \
                and component_callable in system_ctx.components:
            component_callable = system_ctx.components[component_callable]

        if system_ctx is not None:
            provided_attrs = provided_attrs + (("request", system_ctx.request),)

        return self.default_component_processor_api.process(
            ..., component_callable=component_callable,
            provided_attrs=provided_attrs,
        )
```

Key properties:
- `app_state=None` throughout. ContextVar carries everything.
- The processor reads its own cvar, mutates `component_callable` (Protocol → impl) and
  appends to `provided_attrs`, then **delegates** to the default ComponentProcessor.
- The default processor returns the `(Template, ComponentObject | None)` tuple unchanged
  — the component_object is preserved automatically.
- No `_invoke_component` override needed. No "wrap the whole call" issue.

This is a near-perfect template for what tdom-svcs *could* look like with `svcs.Container`
in a cvar instead of `SystemState`.

### Pattern 2 — Pure cvar + `:callback` modifier, no custom processor at all

`TestSimpleContextVarIntegration` (`processor_integration_test.py:203-230`):

```python
AppLoggedInCtx = ContextVar("AppLoggedInCtx", default=False)

def get_app_logged_in() -> bool:
    return AppLoggedInCtx.get()

# In a template, anywhere:
test_t = t"<div><{AuthStatus} app_logged_in={get_app_logged_in:callback} /></div>"

with AppLoggedInCtx.set(True):
    assert html(test_t) == '<div><span class="auth-display">Logged In</span></div>'
```

Key properties:
- Default `TemplateProcessor()`. No subclass.
- The `:callback` template modifier defers evaluation to render time.
- The callable closes over a ContextVar.

Doesn't fully cover DI's needs (no Protocol→impl resolution; consumer has to wire each value
into each template) but valuable as a reminder: ContextVar + callback covers many "I just
need a value at render time" cases without any framework plumbing.

### Pattern 3 — Typed `app_state` parameter, custom processor reads it

`TestTypedAppStateIntegration` (`processor_integration_test.py:292-363`):

```python
@dataclass
class AppState:
    logged_in: bool = False

@dataclass
class TypedAppStateComponentProcessor(IComponentProcessor[AppState]):
    default_component_processor_api: IComponentProcessor[AppState] = field(
        default_factory=ComponentProcessor[AppState]
    )

    def process(self, ..., app_state: AppState, ..., provided_attrs=()):
        provided_attrs = provided_attrs + (("app_logged_in", app_state.logged_in),)
        return self.default_component_processor_api.process(..., provided_attrs=provided_attrs)

tp = TemplateProcessor(component_processor_api=TypedAppStateComponentProcessor())
res = tp.process(t"<div><{AuthStatus} /></div>", ProcessContext(), AppState(logged_in=True))
```

Key properties:
- `app_state` is a user-defined frozen dataclass, threaded as a parameter.
- The custom processor reads it and adds *every potentially-relevant value* to
  `provided_attrs`. The default processor's kwarg-prep filters to fields the callable
  actually accepts.
- **`test_local_precedence` proves**: when both `app_state.logged_in` and a template-level
  `app_logged_in` are set, the template-level value wins. Because `_prep_component_kwargs`
  writes `provided_attrs` first, then `attrs` overwrite (lines 404-412 of `processor.py`).

This is the architecture the original research doc locked in (with `svcs.Container` in
place of `AppState`). It works. It also has the "throw away DI work" property Ian flagged.

## Ian's questions, mapped to design choices

### Q1: ContextVar vs `app_state` for the container?

The original doc's argument for `app_state` was: "the container is per-request-render, so
explicit threading is cleaner than ambient cvar state." Patterns 1 and 3 show both work.
The deeper question is *what is `app_state` for*?

After `a877d46`, upstream's signal is clear. `DefaultAppState = None` and the param
defaults to `None` everywhere. `app_state` is for **user-defined application state values**
the integrator wants to inject (logged_in flag, current user, request ID). It is not a
hidden slot for framework infrastructure.

A `svcs.Container` is framework infrastructure. Putting it in `app_state` parameterizes
`TemplateProcessor[svcs.Container | None]` for tdom-svcs — meaning a downstream user who
wants to use *both* tdom-svcs DI *and* their own app_state (a `User` object, say) has no
clean way to do it. The `app_state` slot is taken.

ContextVar transport keeps `app_state` free for the integrator. tdom-svcs sets the cvar at
the entry point of `html()`, the custom processor reads it. `TemplateProcessor[T]` stays
generic in `T`.

**Recommendation: container in ContextVar, `app_state` left for downstream users.**

### Q2: How to inject DI fields, given the post-`6fb4227` upstream surface?

`_invoke_component` is gone. Three subclassing patterns are available; the user's
intent to use `Get[T, Attr]` heavily eliminates the simplest one.

**Option A — Minimal `provided_attrs` (rejected: misses Hopscotch features)**.

A small custom resolution loop handling only `is_injectable` and `is_resource`,
prepending to `provided_attrs`, delegating to `super().process()`. Captures
component_object. But the loop doesn't see `info.operator` (`Get[T, Attr]`),
`Inject[svcs.Container]`, or locator-aware Inject — those would need to be
hand-mirrored from `HopscotchInjector._resolve_field_value_sync`. Every time
Hopscotch evolves (a new tier, a new operator, an adapter improvement), tdom-svcs
has to mirror. Drift coupling to our own injector is fine in principle, but it's
unnecessary when Hopscotch already exposes the resolution function.

**Option B — Hand-rolled `process()` with `HopscotchInjector(...)` at the call
(rejected: loses component_object)**.

Override `process()` end-to-end, call `HopscotchInjector(container)(callable_,
**partial_kwargs)` to resolve+invoke, then build the tuple ourselves. Full Hopscotch
pipeline, no throw-away work. **But**: bypasses `super().process()`, so the factory
branch (lines 573–589 of upstream `processor.py`) has to be hand-rolled. Ian
acknowledged this directly: *"I don't know how to handle the 'capturing' part."* The
factory branch is small and stable, but reimplementing it forfeits the extension
point that the `(Template, ComponentObject | None)` tuple represents.

**Option C — Resolve through Hopscotch, delegate the call to `super().process()`
(recommended)**.

The cleanest pattern: use Hopscotch's `_resolve_field_value_sync` to compute
resolved kwargs *without* invoking, then pass the resolved-but-not-already-present
values as `provided_attrs` to `super().process()`. The factory branch in upstream
runs the actual call and captures component_object.

```python
def process(self, ..., component_callable, attrs, component_template, provided_attrs=()):
    container = _di_context.get()
    if container is None:
        return super().process(...)

    # Component-level locator override (Protocol → impl).
    if isinstance(component_callable, type):
        component_callable = _get_implementation(container, component_callable)

    if not needs_dependency_injection(component_callable):
        return super().process(..., component_callable=component_callable, ...)

    # Phase 1: pre-prep partial kwargs as upstream would (without raising on missing).
    callable_info = get_callable_info(component_callable)
    partial_kwargs = _prep_component_kwargs(
        callable_info,
        _resolve_t_attrs(attrs, template.interpolations),
        children=component_template,
        provided_attrs=provided_attrs,
        raise_on_missing=False,
    )
    # Phase 2: full Hopscotch resolution (Get[T, Attr], locator, adapters, defaults).
    injector = HopscotchInjector(container=container)
    field_infos = hopscotch_get_field_infos(component_callable)
    resolved = build_resolved_kwargs(
        field_infos, injector._resolve_field_value_sync, partial_kwargs,
    )
    # Phase 3: di_fill is the delta — fields Hopscotch resolved that weren't already in kwargs.
    di_fill = tuple((k, v) for k, v in resolved.items() if k not in partial_kwargs)

    # Phase 4: delegate; super().process() runs _prep_component_kwargs again with di_fill in
    # provided_attrs, hits the factory branch, returns (Template, instance) for factory components.
    return super().process(
        template, last_ctx, app_state, component_callable,
        attrs, component_template, di_fill + provided_attrs,
    )
```

**Trace-throughs (these are blueprints for the Stage 3 regression tests and for
worked examples in tdom-svcs docs)**:

Trace-through with `Get[T, Attr]` (component has `site_title: Get[Settings, "site_title"]`):

- **Template doesn't provide `site_title`**: Phase 1's `partial_kwargs` doesn't have
  it. Phase 2's resolver hits the `info.operator is not None` branch → calls
  `container.get(Settings).site_title`. Phase 3 includes `("site_title", "My Site")` in
  `di_fill`. Phase 4: super() runs `_prep_component_kwargs`, template attrs (none here),
  children, then provided_attrs fill `site_title`. ✅
- **Template provides `site_title="Override"`**: Phase 1's `partial_kwargs` has it.
  Phase 2's resolver returns from tier-1 kwargs (no `Get` resolution runs — no
  throw-away work). Phase 3: `site_title` is already in `partial_kwargs`, so it's not
  in `di_fill`. Phase 4: super() runs with template attr → `site_title="Override"`. ✅

Trace-through with `Inject[svcs.Container]`:

- Phase 2's resolver hits the special-case `field_info.inner_type is svcs.Container`
  branch → returns the container itself. Phase 3 includes the container in `di_fill`.
  Phase 4: super() fills the kwarg. ✅

Trace-through with locator-aware `Inject[IProtocol]` (multiple impls registered with
resource/location selectors):

- Phase 2's resolver hits `_try_resolve_from_locator_sync`, which uses
  `container.resource` and `container.location` to pick the right impl. ✅

#### Precedence chain

Template-provided values always win, exactly the same way they do in upstream's
`test_local_precedence`. The full precedence chain (highest → lowest priority):

1. **Template attrs** — `t"<{Header} title='...'>"`
2. **Existing `provided_attrs`** — from outer processors or callers wrapping tdom-svcs
3. **DI-resolved values** — `Get[T, Attr]`, `Inject[T]`, `Resource[T]`,
   `Inject[svcs.Container]`, locator-aware `Inject[Protocol]`, adapters
4. **Field defaults** — `field(default=...)` on the component

This matches `HopscotchInjector._resolve_field_value_sync`'s tier ordering. Two
mechanisms enforce it:

- **Phase 2's tier-1 short-circuit**: when Hopscotch sees a key already in
  `partial_kwargs` (which is template + provided + children), it returns from
  `resolve_from_kwargs` and skips the DI lookup. No throw-away work.
- **Phase 3's `di_fill` filter**: only fields that Hopscotch *resolved* and weren't
  already in `partial_kwargs` are forwarded as `provided_attrs`. So template/provided
  values flow through normal upstream channels in Phase 4, never via `provided_attrs`.

Trace with `t"<{Header} title='Override'>"` where `title: Inject[str]`:

- Phase 1: `partial_kwargs = {"title": "Override", "children": body}`
- Phase 2: resolver sees `"title"` in kwargs → returns `"Override"` without DI. No
  `container.get(str)` call.
- Phase 3: `"title"` is in `partial_kwargs` → excluded from `di_fill`.
- Phase 4: super's `_prep_component_kwargs` writes template attrs first →
  `kwargs["title"] = "Override"`. Component invoked with `title="Override"`.

Result: template wins. `Inject[str]` is never resolved.

What this gets right:
- Full Hopscotch pipeline preserved without re-implementing any of it. New Hopscotch
  features (e.g., a future `Get[T, Method, *args]`) flow through automatically.
- Component_object captured via `super().process()`'s factory branch.
- No throw-away resolution: tier-1 kwargs short-circuit DI lookups for
  template-overridden fields.
- The merge order in `_prep_component_kwargs` (template first, provided fills gaps)
  composes naturally with `di_fill`: DI values can never override template values.

What this trades off:
- Imports underscore-prefixed helpers (`_prep_component_kwargs`, `_resolve_t_attrs`,
  `get_callable_info`) from `tdom.processor`, and `_resolve_field_value_sync` from
  `HopscotchInjector`. Both are intentionally available; both could rename. Mitigation:
  concentrate the imports in one method; isolate via a private helper function.
- Two `_prep_component_kwargs` calls per component when DI is needed (one in Phase 1
  with `raise_on_missing=False`, one in Phase 4 inside `super().process()`). Both are
  microsecond-fast. Negligible.
- The `partial_kwargs` we compute in Phase 1 is *almost* what super() will compute
  again in Phase 4. The difference is just the missing-required check. Wasteful in
  the abstract; in practice irrelevant.

**Recommendation: Option C.** It costs nothing functional that Options A or B were
saving. It preserves component_object capture (A's win) and full Hopscotch features
(B's win) simultaneously by routing the resolution through Hopscotch but the
invocation through upstream.

## Revised architecture for tdom-svcs

Two changes from the current `tdom-svcs/src/tdom_svcs/processor.py`:

1. **Container moves from `app_state` → ContextVar** (Q1).
2. **DI moves from `_invoke_component`-style call wrapping → Hopscotch resolution
   delegated through `super().process()`** (Q2, Option C). The `_invoke_component`
   override is deleted (the upstream method no longer exists). Resolution runs through
   `build_resolved_kwargs(field_infos, HopscotchInjector(...)._resolve_field_value_sync,
   partial_kwargs)`, preserving the full Hopscotch pipeline.

```python
# tdom-svcs/src/tdom_svcs/processor.py

from contextvars import ContextVar
from dataclasses import dataclass

import svcs
from svcs_di.injector_helpers import build_resolved_kwargs
from svcs_hopscotch.auto import hopscotch_get_field_infos
from svcs_hopscotch.injectors.hopscotch import HopscotchInjector
from tdom.processor import (
    ComponentProcessor,
    ProcessContext,
    TemplateProcessor,
    _prep_component_kwargs,
    _resolve_t_attrs,
    get_callable_info,
)

_di_context: ContextVar[svcs.Container | None] = ContextVar("_di_context", default=None)


def _get_implementation(container: svcs.Container, cls: type) -> type:
    """Look up a Protocol's concrete impl via the container's locator; fall back to cls."""
    try:
        get_impl = container.registry.locator.get_implementation
    except AttributeError:
        return cls
    resource = getattr(container, "resource", None)
    location = getattr(container, "location", None)
    impl = get_impl(
        cls,
        resource=type(resource) if resource is not None else None,
        location=location,
    )
    return impl if impl is not None else cls


def needs_dependency_injection(value: object) -> bool:
    if not callable(value):
        return False
    return any(
        info.is_injectable or info.is_resource or info.operator is not None
        for info in hopscotch_get_field_infos(value)
    )


@dataclass(frozen=True)
class DIComponentProcessor(ComponentProcessor):
    """Resolves DI fields through Hopscotch; delegates the call to super()."""

    def process(
        self, template, last_ctx, app_state, component_callable,
        attrs, component_template, provided_attrs=(),
    ):
        container = _di_context.get()
        if container is None:
            return super().process(
                template, last_ctx, app_state, component_callable,
                attrs, component_template, provided_attrs,
            )

        # Component-level locator override (Protocol → impl).
        if isinstance(component_callable, type):
            component_callable = _get_implementation(container, component_callable)

        if not needs_dependency_injection(component_callable):
            return super().process(
                template, last_ctx, app_state, component_callable,
                attrs, component_template, provided_attrs,
            )

        # Phase 1: pre-prep partial kwargs (template attrs + provided + children, no raise).
        callable_info = get_callable_info(component_callable)
        partial_kwargs = _prep_component_kwargs(
            callable_info,
            _resolve_t_attrs(attrs, template.interpolations),
            children=component_template,
            provided_attrs=provided_attrs,
            raise_on_missing=False,
        )

        # Phase 2: full Hopscotch resolution — Get[T, Attr], locator, adapters, defaults.
        injector = HopscotchInjector(container=container)
        field_infos = hopscotch_get_field_infos(component_callable)
        resolved = build_resolved_kwargs(
            field_infos, injector._resolve_field_value_sync, partial_kwargs,
        )

        # Phase 3: the DI-fill delta — only fields Hopscotch resolved that weren't in kwargs.
        di_fill = tuple(
            (name, value)
            for name, value in resolved.items()
            if name not in partial_kwargs
        )

        # Phase 4: delegate. super().process() captures component_object via factory branch.
        return super().process(
            template, last_ctx, app_state, component_callable,
            attrs, component_template, di_fill + provided_attrs,
        )


_tp = TemplateProcessor(component_processor_api=DIComponentProcessor())
_default_ctx = ProcessContext()


def html(template, *, container: svcs.Container | None = None) -> str:
    token = _di_context.set(container)
    try:
        return _tp.process(template, _default_ctx, app_state=None)
    finally:
        _di_context.reset(token)
```

Diff vs. the current `tdom-svcs/src/tdom_svcs/processor.py`:

- `_di_context: ContextVar[svcs.Container | None]` re-introduced (Stage 1's spec
  removed it; restore it).
- `DIComponentProcessor.process()` resolves DI through Hopscotch's pipeline and
  hands the delta to `super().process()` via `provided_attrs`. The
  `_invoke_component` override is deleted.
- `needs_dependency_injection` is widened to include `info.operator is not None` so
  components using only `Get[T, Attr]` (no `Inject[T]`) still trigger DI.
- `DIComponentProcessor` is no longer parameterized over `[svcs.Container | None]`.
- `html()` wraps its body in `_di_context.set(container)` / `reset(token)` and
  passes `app_state=None` to `_tp.process()`.

Line count: ~70 vs. today's ~110. Slightly larger than the rejected Option A sketch
(~50) because Phase 1's pre-prep is explicit, but in exchange we get full Hopscotch
feature parity automatically.

### Imports of underscore-prefixed helpers

The architecture imports four helpers that are conventionally "private" but exposed
in their modules:

- `_prep_component_kwargs`, `_resolve_t_attrs`, `get_callable_info` — from `tdom.processor`.
- `_resolve_field_value_sync` (method on `HopscotchInjector`) — from `svcs-hopscotch`.

Both surfaces are stable in practice:
- `_prep_component_kwargs` was just *expanded* with the flags (`6fb4227`) precisely
  to support this kind of subclassing. Ian's commit message frames it as the
  alternative to `_invoke_component`. Renaming it would break the use case it was
  added for.
- `HopscotchInjector._resolve_field_value_sync` is in our workspace. We control its
  shape; if we rename, we update the call site in tdom-svcs in the same commit.

Optional follow-up upstream ask: rename `_prep_component_kwargs` → `prep_component_kwargs`
(no behavior change) so subclasses don't depend on a `_`-prefixed name. Low priority.

### Performance characteristics

Per DI component, Option C performs:

- 1 extra `_prep_component_kwargs` call (Phase 1, with `raise_on_missing=False`).
- 1 `hopscotch_get_field_infos` call (Phase 2). **Not currently cached** — each call
  walks the callable's annotations.
- 1 `build_resolved_kwargs` iteration over fields (Phase 2). Each field hits the
  Hopscotch resolver once.
- 1 dict comprehension over `resolved` to build `di_fill` (Phase 3).
- 1 `_prep_component_kwargs` call inside `super().process()` (Phase 4) plus the
  factory branch.

Compared to the current `_invoke_component`-based implementation, Option C adds
**one extra `_prep_component_kwargs` call** per DI component. That function does a
cached `get_callable_info` lookup, two dict iterations, and a set difference — all
microsecond-scale.

Verified caching status across the call chain:
- `get_callable_info` (`tdom/callables.py`) — `@lru_cache(maxsize=512)` (disabled
  under pytest). ✅ cached.
- `hopscotch_get_field_infos` (`svcs-hopscotch/auto.py`) — **no decorator**, walks
  annotations on every call. ❌ uncached.
- `get_field_infos` (`svcs-di/auto.py`) — **no decorator**. ❌ uncached.

**Real optimization opportunity**: cache `hopscotch_get_field_infos` (and svcs-di's
`get_field_infos`) with `@functools.cache`. They take a `type | Callable` and return
a list of `FieldInfo` derived from annotations — annotations don't change at runtime,
so the result is stable per callable. Same `pytest`-disable pattern as
`get_callable_info` is reasonable.

This optimization is **independent of the port** — it would speed up the *current*
HopscotchInjector path too (HopscotchInjector calls `get_field_infos_fn` on every
invocation via `inject_target`). Worth doing in svcs-hopscotch / svcs-di before or
during Stage 3, not as part of the port itself.

#### `functools.cache` vs `lru_cache(maxsize=N)`

For `hopscotch_get_field_infos` and `get_field_infos`, prefer `@functools.cache`:

- **Same thread-safety guarantees**. Python 3.14 docs (verified): "The cache is
  threadsafe, ensuring the underlying data structure remains coherent during
  concurrent updates." Both `cache` and `lru_cache` carry this guarantee.
- **Free-threaded compatible**. Same `functools` module; same threadsafe guarantee
  applies to free-threaded builds. The internal dict gets per-key locking under
  PEP 703 automatically.
- **One soft caveat documented for both**: "it's possible for the wrapped function to
  be called more than once if another thread makes an additional call before the
  initial call has been completed and cached." For pure functions of stable inputs
  (annotations don't change), duplicate computations produce equal results — harmless.
- **Slightly faster than `lru_cache`** in the hit path: no LRU bookkeeping (no
  doubly-linked list maintenance).
- **Unbounded growth is fine here**: the cache key is the callable identity, and
  callable count is bounded by code size (every distinct component class). The cache
  cannot grow without limit barring dynamically-generated classes per-render — which
  no workspace consumer does today.

`tdom`'s `get_callable_info` uses `@lru_cache(maxsize=512)`. That's defensive against
scenarios with high callable churn. For svcs-di / svcs-hopscotch, `@functools.cache`
is sufficient; if churn ever becomes a concern, `lru_cache` with a bound is a one-line
change.

#### Why `@lru_cache` and not svcs container caching?

svcs container caching memoizes **service instances per container** — appropriate for
things with request-scoped lifecycle (database connections, `AssetCollector`,
`Settings`). The cache is keyed by service type and lives as long as the container.

`hopscotch_get_field_infos` returns data derived from **static annotations**. The
cache key needs to be the callable's identity (different callables → different
field infos), not a service type. The result is identical across every container
in the process and doesn't change at runtime.

If we routed it through a container-scoped service:
- themester creates a fresh container per render. Container-cached field infos would
  be recomputed on every render — defeating the optimization.
- The cache-key granularity is wrong: svcs caches by service type; we need to cache
  by callable argument.
- Adding a `FieldInfoCache` service that internally does memoization is just
  `@lru_cache` with extra indirection through `container.get(...)`.

Module-level `@lru_cache` is the right tool. svcs container caching remains the
right tool for actual request-scoped state.

Rough scaling without that fix: each `hopscotch_get_field_infos` call walks
annotations once. For a component with 5 fields, this is tens of microseconds.
1000 DI components per render → ~10ms in field-info inspection. With caching, it
collapses to one inspection per unique callable across the whole render
(microseconds).

**Optimizations available without architectural change**:
- Add `@lru_cache` to `hopscotch_get_field_infos` and svcs-di's `get_field_infos`
  (above).
- Keep the no-DI fast paths tight (already in the architecture):
  `if container is None: return super().process(...)` and
  `if not needs_dependency_injection(component_callable): return super().process(...)`.

**Optimizations that require architectural change** (don't pursue without evidence):
- Hand-roll Phase 4 to avoid the second `_prep_component_kwargs` call. Costs the
  factory-branch reuse — same problem as Option B. Not worth the perf gain.
- Memoize Phase 2's `resolved` keyed on `(callable, partial_kwargs)`. Hard to hash
  because partial_kwargs can contain Templates and closures.
- Static analysis: for components whose template attrs and provided_attrs are
  invariant per render (rare in practice), pre-compute `di_fill` at registration time.
  Premature.

**Recommendation**: ship Option C as designed; add the `@lru_cache` to the field-info
helpers as a separate (small) commit in svcs-hopscotch / svcs-di. Profile after Stage
3 with a representative themester SSG build to confirm no other hotspots.

### Type checking opportunities

Concrete improvements to bake into the rewrite:

1. **Parametrize `_get_implementation`**:
   ```python
   def _get_implementation[T](container: svcs.Container, cls: type[T]) -> type[T]: ...
   ```
   Lets `ty` carry the type through the Protocol → impl swap.

2. **Wrap the private resolver access** in one place:
   ```python
   from svcs_di.injector_helpers import FieldResolverWithKwargs

   def _make_resolver(container: svcs.Container) -> FieldResolverWithKwargs:
       injector = HopscotchInjector(container=container)
       return injector._resolve_field_value_sync  # ty: ignore[private]
   ```
   Single ignore in a typed seam. If Hopscotch ever publishes the resolver, this
   helper is the only call site to update.

3. **Component-callable narrowing**: after `if isinstance(component_callable, type):`,
   `ty` should narrow to `type`. Verify; remove `# ty: ignore` if currently present.

4. **Protocol-satisfaction test**: per the workspace standard
   (`agent-os/standards/testing/protocol-satisfaction-test.md`), assert that
   `DIComponentProcessor` satisfies `IComponentProcessor[None]` via a static
   assignment in a test module:
   ```python
   _: IComponentProcessor[None] = DIComponentProcessor()
   ```

5. **Tight `html()` signature** — already in the architecture sketch:
   `html(template: Template, *, container: svcs.Container | None = None) -> str`.
   No `Any`, no `object`.

6. **`partial_kwargs` / `resolved` typed**: `dict[str, object]` (matches upstream's
   `AttributesDict` and svcs-di's `KwargsDict`). The `di_fill` literal is
   `tuple[tuple[str, object], ...]`, compatible with upstream's
   `tuple[Attribute, ...]`.

7. **Add `ty check` as a Stage 3 gate** in `just quality`. Run with strict-ish
   settings; address ignores explicitly rather than blanket-suppressing.

### Upstream changes — confirmed: none required

Option C uses only what's already in `ian/integrations` post-`6fb4227`:
- `_prep_component_kwargs(..., raise_on_missing=False, raise_on_requires_positional=...)`
- `_resolve_t_attrs`, `get_callable_info`
- `ComponentProcessor.process()` overridable, with `super()` delegation working for
  factory components
- `DefaultAppState = None`

Two **nice-to-have** follow-ups (not blockers):

1. **Drop the `_` prefix on `_prep_component_kwargs`** (and `_resolve_t_attrs`).
   The flag-based subclassing pattern Ian committed in `6fb4227` makes these part of
   the intentional public surface.
2. **Bundle Phase 1 into a `ComponentProcessor` static helper**:
   ```python
   class ComponentProcessor:
       @staticmethod
       def prep_partial_kwargs(component_callable, template, attrs, component_template, provided_attrs):
           callable_info = get_callable_info(component_callable)
           return _prep_component_kwargs(
               callable_info,
               _resolve_t_attrs(attrs, template.interpolations),
               children=component_template,
               provided_attrs=provided_attrs,
               raise_on_missing=False,
           )
   ```
   Saves subclasses three imports and a few lines. Worth proposing to Ian if he's
   amenable; tdom-svcs ships fine without it.

## Why the post-`6fb4227` upstream surface is load-bearing

The commits we now depend on are `6fb4227` (flags + reordered merge) and the various
"`DefaultAppState = None`" / `assume_ctx` pieces. None of these are large; together they
make tdom-svcs's port a thin subclass instead of a reimplementation. If any single
piece were reverted, here's what tdom-svcs would lose.

### 1. The reordered merge order makes `provided_attrs` work as DI fallback

Pre-`6fb4227`, `_prep_component_kwargs` wrote `provided_attrs` first, then template
`attrs` overwrote. Post-`6fb4227`, template `attrs` go first and `provided_attrs` only
fill keys still missing from kwargs.

The effective precedence is unchanged (template wins where both are set). What changed
is the *meaning* of `provided_attrs`: it is now explicitly a **fallback** mechanism
("set this if no one else did"), not a default-with-override. That's exactly the
semantics we need to push DI-resolved values:

- DI resolves `request: Inject[ISimpleRequest]` → `request_value`.
- We prepend `("request", request_value)` to `provided_attrs`.
- Template doesn't set `request`. Kwargs after template merge: `{"children": ...}`.
- Provided fills the gap: kwargs becomes `{"children": ..., "request": request_value}`.
- Missing-required check passes; the bare invocation succeeds.

Pre-`6fb4227` semantics did the same end-state, but the "provided is a default" framing
was awkward when used for required-field DI. The new framing is a better fit.

### 2. `raise_on_missing=False` is actively used (not a nice-to-have)

The recommended architecture (Option C) calls `_prep_component_kwargs` directly in
Phase 1 with `raise_on_missing=False`, then runs full Hopscotch resolution in Phase 2,
then delegates to `super().process()` in Phase 4 (which calls `_prep_component_kwargs`
*again* with the default `raise_on_missing=True`).

Without the flag, Phase 1 would raise `TypeError` for any required `Inject[T]` /
`Get[T, Attr]` field, because at that point Hopscotch hasn't resolved them yet. The
flag is the seam that lets us thread DI between two `_prep_component_kwargs` calls.

If `raise_on_missing` reverted to always-true, tdom-svcs would have to either:
- Fork `_prep_component_kwargs` (~30 lines including kebab→snake handling), or
- Force every `Inject[T]` / `Get[T, Attr]` field to carry a default value (gross).

### 3. `DefaultAppState = None` keeps `app_state` available for users

Pre-`a877d46`, `DefaultAppState = dict[str, object]`. The default was an *opinionated*
type. Post-`a877d46`, the default is `None` and the type parameter is genuinely free
for the integrator to use. tdom-svcs's container moves to a ContextVar, leaving
`app_state` for the user.

If `DefaultAppState` reverted to a mandatory dict, tdom-svcs could still work (just
parameterize as `TemplateProcessor[None]` explicitly), but every user of tdom-svcs
would inherit the dict-typed slot they didn't ask for.

### 4. The `super().process()` factory branch captures component_object

This is upstream behavior we depend on but didn't have to fight for — it has been
stable. The factory branch at `processor.py:573-589` constructs the
`(Template, ComponentObject | None)` tuple. Our recommended architecture calls
`super().process()` for both the missing-required check (when DI fills required
fields) and the factory branch.

If upstream ever moves the factory branch out of `process()`, we'd need to mirror the
move. Low risk — Ian's commits explicitly internalize the factory dance (`9adc788`)
to give subclasses *less* responsibility, not more.

### Net

Total upstream surface tdom-svcs depends on:

- `_prep_component_kwargs` callable as a public-ish helper, with the new flags and
  merge order.
- `ComponentProcessor.process()` overridable, with `super()` delegation working for
  factory components.
- `DefaultAppState = None`.
- `html()` / `svg()` accept optional `assume_ctx`.

The `_invoke_component` hook from earlier today (`7561617`, since reset) is **not**
needed under this architecture. tdom-svcs's `pauleveritt/invoke-component-hook` branch
no longer needs to carry a workspace-only patch — it just consumes `ian/integrations`
as-is, post-`6fb4227`. The remaining upstream coordination is merge timing only.

## Revised plan stages

### Stage 1 — Cleanup against current upstream (unchanged from original plan)

Still applies. Pure type/dead-code cleanup. Already in flight as spec
`2026-04-26-1130-cleanup-container-only-context`.

**Caveat**: that spec renames the public param to `container=` and types it
`svcs.Container | None`. Stage 1 plan doesn't need revision; the public API change is
correct regardless of which transport (cvar vs app_state) we land on internally.

### Stage 2 — Workspace migration to `Template`-returning components (unchanged)

Still applies. Components return `Template`, `children` is a `Template`. Independent of
the cvar-vs-app_state decision.

### Stage 3 — Port to `ian/integrations` post-`6fb4227` (revised)

**Changed since original plan and prior revisions of this doc:**
- The `_invoke_component` upstream hook attempt was reset. Ian preferred and committed
  flags on `_prep_component_kwargs` (`6fb4227`) instead.
- No workspace patch needed. The `pauleveritt/invoke-component-hook` branch was
  deleted; `tdom = { workspace = true }` points directly at `ian/integrations`.
- DI strategy: Option C (Hopscotch resolution → `super().process()`). Preserves full
  Hopscotch feature set including `Get[T, Attr]`.
- Container moves from `app_state` to ContextVar.

**New scope:**

1. Rewrite `tdom-svcs/src/tdom_svcs/processor.py` per the revised architecture:
   - Re-introduce `_di_context: ContextVar[svcs.Container | None]` (Stage 1's spec
     removed it).
   - Replace `_invoke_component` override with the four-phase Option C flow in
     `process()`: pre-prep partial kwargs (Phase 1), resolve via Hopscotch
     (Phase 2), compute the delta (Phase 3), delegate (Phase 4).
   - Drop the `[svcs.Container | None]` type parameter on `DIComponentProcessor`.
   - Wrap `html()` body in `_di_context.set(container)` / `reset(token)` bracket.
     Pass `app_state=None` to `_tp.process()`.
   - Widen `needs_dependency_injection` to also detect `info.operator is not None`
     (so a component with only `Get[T, Attr]` and no `Inject[T]` still triggers DI).

2. Add regression tests covering the full Hopscotch resolution surface:
   - **`Inject[T]` (basic)**: dataclass with `Inject[Settings]` field. Render with
     and without template override. Assert resolution and override both work.
   - **`Resource[T]`**: dataclass with `Resource[CurrentRequest]` field. Set
     `container.resource = request_instance`; assert injection.
   - **`Get[T, Attr]`**: dataclass with `site_title: Get[Settings, "site_title"]`.
     Assert resolution returns `container.get(Settings).site_title`. Assert template
     `site_title="Override"` short-circuits the operator branch (no `container.get`
     for Settings if Settings is also not otherwise needed).
   - **`Inject[svcs.Container]`**: dataclass with `container: Inject[svcs.Container]`
     field. Assert it receives the container itself, not the result of
     `container.get(svcs.Container)`.
   - **Locator-aware `Inject[Protocol]`**: register `IConfig` to `ConfigA` for
     `resource=Page`, `ConfigB` for `resource=Section`. Render the same component in
     both contexts; assert the right impl is injected.
   - **Component-level locator override (Protocol → impl on `<{IHeader}>`)**:
     `<{IHeader} />` with `IHeader` registered to `Header`. Assert kwarg prep uses
     `Header`'s field info.
   - **Component_object capture under DI**: factory class component with `Inject[T]`
     fields. Assert slot 2 of the returned tuple holds the constructed instance.
     Implementation: wrap `DIComponentProcessor` to record the return tuple.
   - **Required-DI-field fallback semantics**: dataclass component with required
     `Inject[T]`, no template attr. Assert renders correctly.
   - **No-DI fast path**: function component without `Inject[T]` / `Resource[T]` /
     `Get[T, Attr]`. Assert `process()` short-circuits to `super().process()`
     without resolution overhead (perf-style assertion via a counter on the resolver).

3. Drop dead imports and helpers from `tdom_svcs.processor`:
   - The `_invoke_component` method body is gone (the upstream method no longer exists).
   - The current `_get_implementation` is preserved (still called for component-level
     Protocol override).
   - `HopscotchInjector` is now imported for resolution (not invocation).

**Verify**: `just quality && just test` in tdom-svcs and themester. All existing
examples and tests pass byte-identically. Add new themester example exercising
`Get[T, Attr]` once Stage 3 is in to lock in the user's intended pattern.

### Stage 4 — Adopt as workspace-wide processor (unchanged)

Still applies. With the cvar transport, `tdom_svcs.html(template, container=None)` is
even more clearly a drop-in for `tdom.html(template)` — same single positional, optional
kwarg. The "no DI = no overhead" property holds: `_di_context.get()` returns `None`,
the `if container is not None` branches don't fire, and we delegate to the default
ComponentProcessor unmodified.

## Open questions / risks (revised)

1. **ContextVar leakage between async tasks.** ContextVar is task-local in asyncio;
   server frameworks propagate task-local state correctly. For themester's CLI/SSG
   use case (synchronous, single render per command) this is a non-issue. Doc note
   for users who run renders concurrently.
2. **Hopscotch features and `Get[T, Attr]`** (now first-class, not deferred). Option
   C runs *every* DI field through Hopscotch's resolver, so `Get[T, Attr]`,
   `Inject[svcs.Container]`, locator-aware Inject, adapter fallback, and defaults
   all work without special-case code in tdom-svcs. The user has flagged
   `Get[T, Attr]` as a load-bearing pattern (it replaces dataclass `__post_init__`
   for derived fields); the architecture is designed to support that from day one.
   Regression tests in Stage 3 cover each feature explicitly.
3. **Component-level Protocol → impl** (unchanged): `<{IHeader}>...</{IHeader}>` with
   `IHeader` registered to `Header`. Architecture handles this in `process()` before
   Phase 1, so all subsequent phases see `Header`'s field info.
4. **Field-level Protocol → impl** (now handled): `Inject[IProtocol]` where IProtocol
   has multi-impl registration goes through `_try_resolve_from_locator_sync` inside
   Hopscotch's resolver. No additional code in tdom-svcs.
5. **Component_object capture under DI**: regression test required. The delegation to
   `super().process()` is what makes capture work; without a test, future refactors
   could quietly bypass `super().process()` and lose the contract.
6. **Imports of underscore-prefixed helpers.** `_prep_component_kwargs`,
   `_resolve_t_attrs`, `get_callable_info` from `tdom.processor`;
   `_resolve_field_value_sync` from `HopscotchInjector`. Stable in practice (see
   "Imports of underscore-prefixed helpers" section above). Optional follow-up: ask
   Ian to drop the `_` prefix on `_prep_component_kwargs` since it's now part of the
   intentional subclassing surface.
7. **Doc divergence.** This revisited research doc supersedes the original
   `port-tstring-html-integrations.md`. Reference it from any spec or roadmap entry
   that previously cited the original.

## Sequencing (revised)

1. **In flight:** Stage 1 (`2026-04-26-1130-cleanup-container-only-context`). Continue.
2. **Next:** Stage 2 sub-steps (Template-returning components). Order unchanged.
3. **Then:** Revised Stage 3:
   - Verify workspace `tstring-html/` is on `ian/integrations` (done — branch deleted).
   - Rewrite `tdom-svcs/src/tdom_svcs/processor.py` per Option C (four-phase flow).
   - Add nine regression tests covering the full Hopscotch resolution surface.
   - Add a themester example exercising `Get[T, Attr]` to lock in the user's pattern.
4. **Then:** Stage 4 audit and switch.

Total estimated effort: 4-6 days, same as before. Stage 3 is slightly larger now
(more comprehensive test coverage given Get[T, Attr] is in scope), but no workspace
patches to maintain.
