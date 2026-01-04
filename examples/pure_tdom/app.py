from examples.pure_tdom.site import SimpleConfig, svcs_setup


def main() -> str:
    """Demonstrate pure tdom usage with config and context dictionaries."""

    # Create a context dictionary with user data
    context = {
        "user": {
            "name": "Alice",
            "role": "admin",
            "email": "alice@example.com",
        },
        "settings": {
            "theme": "dark",
            "language": "en",
        },
    }

    # Create a simple config
    config = SimpleConfig()
    svcs_setup(config)

    # Example: Render Dashboard
    from examples.pure_tdom.components import Dashboard
    
    dashboard = Dashboard(context=context)
    return dashboard()


if __name__ == "__main__":
    print(main())
