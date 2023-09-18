"""Top-level package for rstms-ehandler."""

from .ehandler import ExceptionHandler, exception_handler, set_ehandler_option
from .version import __author__, __email__, __timestamp__, __version__

__all__ = [
    "ExceptionHandler",
    "exception_handler",
    "set_ehandler_option",
    "__version__",
    "__timestamp__",
    "__author__",
    "__email__",
]
