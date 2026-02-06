# Registry Introspection Helpers — References

## Key Files

### ServiceLocator Implementation
`/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/locator.py`
- `ServiceLocator` class
- `FactoryRegistration` dataclass
- `_single_registrations` dict
- `_multi_registrations` dict

### Middleware Helpers
`/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/middleware.py:107`
- `get_middleware_types()` function
- Existing pattern for middleware introspection

### Registry Implementation
`/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/registry.py`
- `HopscotchRegistry` class
- `locator` attribute
- Component and middleware registration

## Related Standards

### frozen-dataclass-services
Location: `agent-os/standards/frozen-dataclass-services/`
- Pattern for immutable service types
- Used throughout tdom-svcs

### protocol-first-design
Location: `agent-os/standards/protocol-first-design/`
- Type-first API design
- Clear contracts via protocols

### function-based-tests
Location: `agent-os/standards/function-based-tests/`
- Test organization pattern
- Used in all test files

### sybil-doctest
Location: `agent-os/standards/sybil-doctest/`
- Doctest integration with pytest
- Automatic testing of documentation examples

## Similar Implementations

### get_middleware_types()
Already exists in `tdom_svcs.middleware` — provides pattern for extracting registered types from registry.

### svcs Registry
The svcs library has similar introspection capabilities that we can reference for API design.
