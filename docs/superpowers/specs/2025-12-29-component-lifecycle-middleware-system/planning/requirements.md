# Spec Requirements: Component Lifecycle Middleware System

## Initial Description
Component Lifecycle Middleware System — Implement pluggable middleware hooks for logging, validation, transformation, and error handling during component initialization and rendering phases. `M`

## Requirements Discussion

### First Round Questions

**Q1:** I assume the middleware system should leverage the existing hook system implemented in item 1 (Minimal tdom Core Hooks), providing a higher-level API that wraps the pre-resolution, post-resolution, and rendering hooks. Is that correct, or should this be a completely separate system?
**Answer:** Leverage existing hook system from item 1 (wrap pre-resolution, post-resolution, rendering hooks)

**Q2:** For middleware execution order, I'm thinking we should support a priority-based ordering system where middleware can specify their execution order (similar to web frameworks like Starlette or Flask), allowing developers to control when logging happens relative to validation. Should we use numeric priorities, or an explicit before/after dependency declaration?
**Answer:** Use weighting/priority system with a default in the middle

**Q3:** I assume common middleware types should include: logging (request/response timing, component names), validation (props validation, type checking), transformation (props transformation, output sanitization), and error handling (exception catching, fallback rendering). Should we provide built-in implementations for these common patterns, or just provide base classes and examples?
**Answer:** No built-in middleware implementations - just base classes and examples

**Q4:** For middleware context, I'm thinking each middleware should have access to: the component being rendered, its props (both explicit and injected), the svcs container, and a shared context dict for passing data between middleware. Is this sufficient, or should middleware also access the parent component tree or request-level data?
**Answer:** Need a `setup_container()` function that accepts context and registers it with a dict-like protocol. Context should be available as `context: Inject[Context]`. Context should be a protocol that allows either `RequestContext` or `svcs.Container` as a context argument. Context registration via `setup_container()` function (first choice - automatic registration). Injection syntax: Option B - `context: Inject[RequestContext]` (typed context object). Context should be mutable. Middleware should use svcs-di injection to request what it wants from context/container. No existing svcs container context pattern to follow. Context is part of container lifecycle (not per-request for now).

**Q5:** I assume middleware should be configured at the container/registry level (global to all components) but also allow per-component middleware overrides through decorator parameters. Is that correct, or should middleware only be global?
**Answer:** Need to distinguish registry vs container registrations - some middleware is stateless between requests, some collects state (like static assets)

**Q6:** For error handling in middleware, I'm thinking failed middleware should either: halt execution and return an error state, or log the error and continue to the next middleware. Should we support both modes with a configurable strategy, or pick one approach?
**Answer:** Error handling: Halt execution on middleware failure

**Q7:** For async support, I assume middleware hooks should support both sync and async implementations (since tdom itself supports async rendering), with automatic detection of which to call. Is that correct, or is async support not needed for the initial version?
**Answer:** (No explicit answer provided - assume async support needed based on tdom's async capabilities)

**Q8:** What functionality should be explicitly OUT OF SCOPE for this first version? For example, should we exclude: middleware composition/chaining helper utilities, middleware performance profiling, or conditional middleware activation based on component properties?
**Answer:** (No explicit answer provided - defer to spec writer to determine reasonable scope boundaries)

### Existing Code to Reference

**Similar Features Identified:**
- Feature: Item 1 (Minimal tdom Core Hooks) - Path: Not yet implemented but should exist after completion of roadmap item 1
- Feature: HopscotchInjector patterns - Path: `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/` (existing injector patterns to reference)
- Feature: Error handling patterns from recent refactoring - Path: Class-only components, type validation patterns in the codebase
- Components to potentially reuse: Hook system from item 1 (pre-resolution, post-resolution, rendering hooks)
- Backend logic to reference: Existing injector implementations, component registry patterns

### Follow-up Questions

**Follow-up 1:** For the priority/weighting system, what numeric range should we use? I'm thinking -100 to +100 with 0 as the default middle, similar to how many middleware systems work (lower numbers execute first). Is that the right scale, or would you prefer something like 0-1000?
**Answer:** Priority range: -100 to +100 with 0 as default (lower numbers execute first)

**Follow-up 2:** You mentioned distinguishing registry vs container registrations - should stateless middleware be registered via a `register_middleware()` method on the component registry (at startup), while stateful middleware (like static assets collector) should be registered in the container via `setup_container()` and injected when needed?
**Answer:** Yes - stateless middleware registered via `register_middleware()` on the component registry (at startup), stateful middleware registered in container via `setup_container()` and injected when needed

**Follow-up 3:** For the `setup_container()` function that registers context, should this be: A standalone utility function in tdom-svcs that users call during app initialization? Part of a larger container setup/initialization pattern? Both - a utility that can be used standalone or as part of a setup helper?
**Answer:** Standalone utility function in tdom-svcs that users call during app initialization

**Follow-up 4:** You mentioned the context protocol should allow either `RequestContext` or `svcs.Container` - does this mean middleware can choose to inject either type depending on what they need, or that the protocol defines a common interface between them? Should we provide both `RequestContext` and a minimal `Context` protocol that both RequestContext and Container satisfy?
**Answer:** One protocol with a dict-like shape (retrieval only) that svcs.Container satisfies. The protocol should only define the parts needed for retrieval and be designed so svcs.Container meets it.

**Follow-up 5:** For the base classes, should we provide: Just one `Middleware` base class/protocol? Separate base classes for different lifecycle phases (ResolutionMiddleware, RenderingMiddleware)? A protocol definition and let users choose between protocol or inheritance?
**Answer:** Just one protocol (not separate classes for different phases)

**Follow-up 6:** When middleware halts execution on failure, what should the return value be - should we define a standard error result type, or let each middleware return their own error representation that gets propagated?
**Answer:** Middleware should define their own exceptions (no standard error result type)

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- **Leverage Existing Hook System:** Build on top of the hook system from roadmap item 1 (Minimal tdom Core Hooks), wrapping pre-resolution, post-resolution, and rendering hooks with a higher-level middleware API
- **Priority-Based Execution Order:** Implement numeric priority system ranging from -100 to +100, with 0 as the default middle value. Lower numbers execute first, allowing developers to control middleware execution sequence
- **Base Protocol Only:** Provide one middleware protocol definition without built-in implementations. Include examples for common patterns (logging, validation, transformation, error handling)
- **Context Injection System:** Implement `setup_container()` standalone utility function for registering context objects. Context should be injectable via `context: Inject[Context]` where Context is a dict-like protocol for retrieval that svcs.Container satisfies
- **Mutable Context:** Context should be mutable to allow middleware to share data
- **svcs-di Integration:** Middleware should use svcs-di injection syntax to request dependencies from context/container
- **Dual Registration Pattern:** Support both stateless middleware (registered on component registry via `register_middleware()` at startup) and stateful middleware (registered in container via `setup_container()` and injected when needed)
- **Error Handling Strategy:** Halt execution on middleware failure. Middleware defines their own exceptions without a standard error result type
- **Async Support:** Support both sync and async middleware implementations with automatic detection (based on tdom's async rendering capabilities)

### Reusability Opportunities
- **Hook System:** Reference and build upon the hook system from roadmap item 1 (pre-resolution, post-resolution, rendering hooks)
- **Injector Patterns:** Study existing injector implementations in `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/` for patterns to follow
- **Component Registry:** Leverage existing component registry patterns for middleware registration
- **Error Handling:** Apply error handling patterns from recent refactoring (class-only components, type validation)

### Scope Boundaries
**In Scope:**
- Middleware protocol definition (single protocol for all lifecycle phases)
- Priority-based execution ordering system (-100 to +100)
- Context injection via `Inject[Context]` protocol
- `setup_container()` utility function for context registration
- Dual registration: stateless (registry) and stateful (container) middleware
- Integration with existing hook system from item 1
- Example implementations for common patterns (logging, validation, transformation, error handling)
- Halt-on-error execution model with middleware-defined exceptions
- Async/sync middleware support

**Out of Scope:**
- Built-in middleware implementations beyond examples
- Standard error result types (middleware defines their own exceptions)
- Per-component middleware overrides via decorator parameters
- Middleware composition/chaining helper utilities (defer to future enhancement)
- Middleware performance profiling tools (defer to future enhancement)
- Conditional middleware activation based on component properties (defer to future enhancement)
- Per-request context lifecycle (context is part of container lifecycle for now)

### Technical Considerations
- **Hook System Dependency:** This feature depends on the completion of roadmap item 1 (Minimal tdom Core Hooks). The middleware system will wrap these hooks with a higher-level API
- **Container vs Registry:** Clear separation between stateless middleware (registry-level) and stateful middleware (container-level) for different use cases
- **Protocol Design:** Context protocol should be minimal, dict-like (retrieval only), and designed so that svcs.Container naturally satisfies it without modification
- **Initialization Pattern:** `setup_container()` is a standalone utility function called during app initialization, not part of a larger framework
- **svcs-di Integration:** Full use of svcs-di injection patterns (`Inject[T]`, `auto()`) for middleware dependencies
- **Error Propagation:** Middleware-defined exceptions halt execution without standard error wrapping, giving middleware full control over error semantics
- **Type Safety:** Maintain full type safety with mypy and pyright support for middleware protocols and context injection
- **Free-Threading Safety:** Ensure middleware system is compatible with Python 3.14 free-threaded mode
