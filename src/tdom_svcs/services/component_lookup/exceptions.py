"""Exception classes for ComponentLookup service."""


class ComponentNotFoundError(Exception):
    """
    Raised when a component name is not found in the registry.

    This exception includes suggestions for similar component names
    to help users identify typos or misnamed components.
    """

    def __init__(self, name: str, suggestions: list[str]) -> None:
        """
        Initialize ComponentNotFoundError.

        Args:
            name: The component name that was not found
            suggestions: List of similar registered component names
        """
        self.name = name
        self.suggestions = suggestions

        # Build helpful error message
        msg = f"Component '{name}' not found in registry."
        if suggestions:
            suggestion_list = ", ".join(f"'{s}'" for s in suggestions[:5])
            msg += f"\n\nDid you mean one of these? {suggestion_list}"
        else:
            msg += "\n\nNo components are registered. Did you forget to call register_component()?"

        super().__init__(msg)


class InjectorNotFoundError(Exception):
    """
    Raised when the required injector is not registered in the container.

    This exception provides guidance on how to register the necessary
    injector or call setup_container() to configure the system properly.
    """

    def __init__(self, injector_type: str, is_async: bool = False) -> None:
        """
        Initialize InjectorNotFoundError.

        Args:
            injector_type: The name of the injector type that was not found
            is_async: Whether this is for an async component
        """
        self.injector_type = injector_type
        self.is_async = is_async

        # Build helpful error message
        if is_async:
            msg = (
                f"{injector_type} not found in container for async component.\n\n"
                "To use async components, you must register KeywordAsyncInjector:\n"
                "  from svcs_di.injectors.keyword import KeywordAsyncInjector\n"
                "  registry.register_value(KeywordAsyncInjector, KeywordAsyncInjector(container=container))\n\n"
                "Or call setup_container() which registers both sync and async injectors."
            )
        else:
            msg = (
                f"{injector_type} not found in container.\n\n"
                "You must register an injector:\n"
                "  from svcs_di.injectors.keyword import KeywordInjector\n"
                "  registry.register_value(KeywordInjector, KeywordInjector(container=container))\n\n"
                "Or call setup_container() which registers the necessary injectors."
            )

        super().__init__(msg)


class RegistryNotSetupError(Exception):
    """
    Raised when ComponentNameRegistry is not found in the container.

    This exception indicates that setup_container() has not been called
    or the registry was not properly registered.
    """

    def __init__(self) -> None:
        """Initialize RegistryNotSetupError."""
        msg = (
            "ComponentNameRegistry not found in container.\n\n"
            "You must call setup_container() to initialize the tdom-svcs system:\n"
            "  from tdom_svcs.services import setup_container\n"
            "  setup_container(container)\n\n"
            "This registers ComponentNameRegistry and other necessary services."
        )
        super().__init__(msg)
