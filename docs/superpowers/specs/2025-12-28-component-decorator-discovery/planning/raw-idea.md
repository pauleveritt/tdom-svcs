# Raw Idea

## Roadmap Item 3: Component Discovery and Registration

Reuse svcs-di's @injectable decorator for marking components, create package scanning utility to discover decorated components, and register them in both ComponentNameRegistry (string names) and svcs container (type-based DI).

**Size:** M (Medium)

## Dependencies

- Item 1: Minimal tdom Core Hooks (completed)
- Item 2: Basic svcs Container Integration (completed)

## Context

This is the third item in the tdom-svcs product roadmap, building on the foundation of tdom hooks and svcs container integration to enable automatic component discovery and registration.
