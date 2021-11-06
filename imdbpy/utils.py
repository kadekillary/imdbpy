from typing import Any, Callable, Optional, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def exception_handler(func: F) -> Optional[Any]:
    """Replace repetitive try/except blocks"""

    def inner_function(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
        except Exception as e:
            value = None
        return value

    return inner_function
