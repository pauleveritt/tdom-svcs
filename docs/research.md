# tdom Context via `svcs`

This project has a modified version of `tdom` to allow the `html()` function to be passed an arbitrary context. It also
has an example context that uses `svcs-di` as a container.

## Goals

- A minimal isolated set of changest to `tdom` that can be upstreamed without any specific policies
- The initial policies include
  - An optional `config` argument to `html` that is an instance of a tdom-managed frozen dataclass
  - An optional `context` argument to `html()` that is dict-like (matches the interface of a `svcs` container)
  - Component *location* is pluggable and has the context as an argument
  - Component *instantiation* is also pluggable and has the context as an argument 
- Examples that show the use:
  - Injecting `Container` into a component using `DefaultInjector`
  - Use `DefaultInjector` to get an `Inject` from the container
  - Use of `KeywordInjector` to inject component "props"
  - `HopscotchInjector`
    - Find alternate registrations (using decorator) of a component

## Sources

- tdom and svcs-di source are in the parent directory