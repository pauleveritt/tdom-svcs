"""Exception classes for middleware system."""


class MiddlewareError(Exception):
    """
    Base exception for all middleware-related errors.

    This is an abstract base class that should not be instantiated directly.
    Use specific subclasses instead:
    - MiddlewareExecutionError: For runtime execution failures
    - MiddlewareConfigurationError: For setup/configuration issues
    - ContextNotSetupError: For missing context setup
    """

    def __init__(self, message: str) -> None:
        """
        Initialize base middleware error.

        Args:
            message: Description of the error
        """
        super().__init__(message)


class MiddlewareExecutionError(MiddlewareError):
    """
    Raised when middleware execution fails.

    This exception indicates that a middleware encountered an error during
    execution, such as invalid props, failed validation, or other runtime issues.
    """

    def __init__(self, message: str, middleware_name: str | None = None) -> None:
        """
        Initialize MiddlewareExecutionError.

        Args:
            message: Description of the execution failure
            middleware_name: Optional name of the middleware that failed
        """
        self.middleware_name = middleware_name

        if middleware_name:
            full_message = f"Middleware '{middleware_name}' execution failed: {message}"
        else:
            full_message = f"Middleware execution failed: {message}"

        super().__init__(full_message)


class MiddlewareConfigurationError(MiddlewareError):
    """
    Raised when middleware configuration is invalid or incomplete.

    This exception indicates that the middleware system was not properly
    configured, such as missing setup_container() call or invalid middleware
    registration.
    """

    def __init__(self, message: str) -> None:
        """
        Initialize MiddlewareConfigurationError.

        Args:
            message: Description of the configuration issue
        """
        super().__init__(message)


class ContextNotSetupError(MiddlewareConfigurationError):
    """
    Raised when Context is not found in the container.

    This exception indicates that setup_container() has not been called
    or the context was not properly registered.
    """

    def __init__(self) -> None:
        """Initialize ContextNotSetupError with helpful guidance."""
        msg = (
            "Context not found in container.\n\n"
            "You must call setup_container() to initialize the middleware system:\n"
            "  from tdom_svcs.services.middleware import setup_container\n"
            "  setup_container(container)\n\n"
            "This registers the context and makes it available to middleware.\n"
            "The context can be an svcs.Container, plain dict, or any dict-like object."
        )
        super().__init__(msg)
