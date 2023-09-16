import sys
from termcolor import cprint


def greet() -> None:
    """Return a greeting with the first argument."""

    try:
        name = sys.argv[1]
        result = f"Hello {name}."
    except IndexError:
        result = "Hello anonymous user."

    return cprint(result, "red", "on_cyan", attrs=["bold"])
