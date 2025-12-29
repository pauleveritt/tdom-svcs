# Spec Requirements: Component Lifecycle Middleware System

## Initial Description
Component Lifecycle Middleware System — Implement pluggable middleware hooks for logging, validation, transformation, and error handling during component initialization and rendering phases. `M`

**Source:** Product Roadmap, Item 4

**Size:** M (Medium)

**Dependencies:**
- Item 1: Minimal tdom Core Hooks (completed)
- Item 2: Basic svcs Container Integration (completed)
- Item 3: Component Discovery and Registration (completed)

## Requirements Discussion

### First Round Questions

**Q1:** I'm assuming middleware should follow a chain-of-responsibility pattern where each middleware can pass control to the next or short-circuit the chain. Should middleware be able to modify the component instance, props, or rendered output as it passes through the chain?

**Answer:** It can change but immutably by making a new dataclass instance that replaces the parts. A generic walker that detects matching `node.tag` and applies a transform function might be useful.

**Q2:** I'm thinking middleware should hook into at least three lifecycle phases: (a) pre-resolution (before component lookup), (b) post-resolution (after component instantiated but before rendering), and (c) post-render (after HTML generation). Are there other lifecycle phases you need to intercept, such as error handling or cleanup?

**Answer:** Yes to the phases mentioned (pre-resolution, post-resolution, post-render, error handling, cleanup)

**Q3:** For middleware registration, I assume we'd want both global middleware (applies to all components) and component-specific middleware (only certain components). Should middleware also support conditional application based on component types, paths, or metadata?

**Answer:** Sure (yes to global middleware, component-specific middleware, and conditional application)

**Q4:** I'm thinking middleware configuration should be declarative, perhaps through a middleware stack defined at container initialization time like: `ComponentRenderer(middleware=[LoggingMiddleware(), ValidationMiddleware()])`. Should middleware also support dynamic registration at runtime, or is static configuration at startup sufficient?

**Answer:** Static configuration (at startup, not dynamic runtime)

**Q5:** For the middleware interface, I assume each middleware would be a class with methods like `before_resolution()`, `after_resolution()`, `before_render()`, and `after_render()`, each receiving context about the current component and able to modify or abort the process. Should middleware be async-capable for future async rendering support?

**Answer:** before_render should have the resolved kwargs meaning after `Inject[]` resolution

**Q6:** I'm thinking validation middleware should integrate with existing type hints and possibly pydantic or similar validation libraries for prop validation. Should we provide built-in middleware implementations for common use cases (logging, validation, timing), or just the middleware framework?

**Answer:** Nothing built-in (just provide the framework)

**Q7:** For error handling middleware, I assume it should be able to catch exceptions during any lifecycle phase and either handle them (return fallback component), log and re-raise, or transform them. Should error middleware support different error handling strategies per component or per exception type?

**Answer:** Keep it simple

**Q8:** Are there specific logging, validation, transformation, or error handling patterns you need in your use cases that should guide the middleware design? For example, do you need to log performance metrics, validate security permissions, transform props based on context, or handle graceful degradation?

**Answer:** None specific

### Existing Code to Reference

**Similar Features Identified:**
No similar existing features identified for reference.

### Follow-up Questions

**Follow-up 1:** You mentioned middleware should modify dataclasses immutably by creating new instances. Should middleware receive frozen dataclasses (like `@dataclass(frozen=True)`) for props, or should we rely on middleware authors to follow the immutability convention? Also, should we provide helper utilities like `replace()` or `evolve()` functions for common modification patterns?

**Answer:** The immutable part was mainly about after render which is given a Node and the container.

**Follow-up 2:** You mentioned a generic walker that detects matching `node.tag` and applies transform functions. Should this walker be part of the middleware framework itself, or should it be a separate utility that middleware implementations can use? Also, at what phase would this walker operate - during post-render when you have HTML nodes, or during component resolution when you have component instances?

**Answer:** Separate utility and post render (operates during post-render phase when you have HTML nodes)

**Follow-up 3:** You specified that `before_render` should receive resolved kwargs after `Inject[]` resolution. Should this phase also have access to the component class/function itself, or just the resolved kwargs? And should middleware be able to modify these resolved kwargs before they're passed to the component?

**Answer:** Also the target (meaning before_render should have access to the component class/function/target AND the resolved kwargs, and yes middleware can modify the resolved kwargs)

**Follow-up 4:** You confirmed cleanup as a lifecycle phase. Should cleanup always run (even on errors), similar to a `finally` block, or only on successful renders? Also, what resources would typically need cleanup in a component rendering context?

**Answer:** Make a suggestion (user wants recommendation for cleanup behavior)

**Follow-up 5:** For component-specific middleware, should middleware be attached via decorator (like `@with_middleware(LoggingMiddleware)`), or via registration mapping (like registering middleware for specific component types in configuration)?

**Answer:** We will eventually make a `@component` decorator that will allow specifying middleware per-component. For now, add it to the function (meaning registration mapping in configuration for now, decorator support is future)

**Follow-up 6:** Should middleware receive a shared context object that flows through all phases and all middleware in the chain, allowing earlier middleware to pass data to later middleware (e.g., timing data, validation results)?

**Answer:** Yes, we added a `context` argument to the `html()` function. We'll use a svcs.Container most of the time (yes to shared context, and it already exists via html() function's context parameter)

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
N/A - No visual files found during asset check.

## Requirements Summary

### Functional Requirements

**Core Middleware Framework:**
- Implement pluggable middleware system following chain-of-responsibility pattern
- Support five lifecycle phases: pre-resolution, post-resolution, before-render, post-render, error handling, and cleanup
- Allow middleware to pass control to next in chain or short-circuit execution
- Middleware receives shared context (svcs.Container) that flows through all phases
- Static middleware configuration at startup (no dynamic runtime registration)

**Lifecycle Phases:**
1. **Pre-resolution:** Before component lookup begins
2. **Post-resolution:** After component instance created but before rendering
3. **Before-render:** After `Inject[]` resolution, receives component target (class/function) and resolved kwargs, can modify kwargs
4. **Post-render:** After HTML generation, receives Node and container, operates on HTML nodes
5. **Error handling:** Catches exceptions during any lifecycle phase
6. **Cleanup:** Runs after rendering (recommendation needed for error vs success behavior)

**Middleware Scope:**
- Global middleware that applies to all components
- Component-specific middleware via registration mapping in configuration
- Conditional application based on component types, paths, or metadata
- Future: `@component` decorator support for per-component middleware attachment

**Immutability and Transformations:**
- Post-render modifications should be immutable (create new Node instances, not mutate existing)
- Provide separate generic walker utility for node tag matching and transform application
- Walker operates on HTML nodes during post-render phase
- Before-render phase can modify resolved kwargs immutably

**Framework-Only Approach:**
- Provide middleware framework and interfaces only
- No built-in middleware implementations (logging, validation, timing, etc.)
- Keep error handling simple
- Let library users implement specific middleware for their use cases

### Reusability Opportunities
No existing similar features identified for reuse. This is a new middleware framework for the tdom-svcs integration layer.

### Scope Boundaries

**In Scope:**
- Middleware base classes/protocols defining lifecycle hook methods
- Middleware registration and configuration system (static, startup-time)
- Middleware chain execution logic with short-circuit support
- Integration with existing `html()` function's context parameter
- Generic node walker utility for post-render transformations
- Support for global, component-specific, and conditional middleware
- Error handling middleware phase
- Cleanup middleware phase
- Context passing through middleware chain (via svcs.Container)
- Before-render phase with access to component target and resolved kwargs

**Out of Scope:**
- Built-in middleware implementations (logging, validation, timing)
- Dynamic middleware registration at runtime
- Async middleware support (future consideration)
- `@component` decorator (future enhancement, mentioned in roadmap)
- Complex error handling strategies (keeping it simple)
- Specific use case patterns (no particular logging/validation requirements)

### Technical Considerations

**Integration Points:**
- Builds on completed Item 1 (Minimal tdom Core Hooks)
- Builds on completed Item 2 (Basic svcs Container Integration)
- Builds on completed Item 3 (Component Discovery and Registration)
- Integrates with existing `html()` function's context parameter
- Works with `Inject[]` resolution system from svcs-di
- Operates on Node objects from tdom core

**Architecture:**
- Three-layer architecture: tdom core (minimal hooks) + tdom-svcs (policy/middleware) + svcs-di (DI framework)
- Middleware lives in tdom-svcs policy layer
- Uses svcs.Container as shared context across middleware chain
- Static configuration approach aligns with container initialization patterns

**Type Safety:**
- Must maintain 100% type coverage with mypy and pyright
- Protocol-based middleware interfaces for flexibility
- Type hints for lifecycle hook method signatures
- Generic types for node walker utility

**Testing:**
- Test middleware chain execution and short-circuiting
- Test each lifecycle phase independently
- Test global vs component-specific middleware application
- Test conditional middleware application
- Test error handling and cleanup phases
- Test context passing through middleware chain
- Test immutable node transformations with walker utility
- Verify free-threading compatibility

**Design Recommendations Needed:**
- Cleanup phase behavior: Should it run always (like `finally`) or only on success? What resources typically need cleanup in component rendering?
