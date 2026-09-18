"""Object Traversal & Inspection Toolkit."""

__version__ = "0.1.0"

from .exceptions import InvalidPath, OtitError, PathNotFound
from .traversal import delete, get, has, set

__all__ = [
    "OtitError",
    "PathNotFound",
    "InvalidPath",
    "get",
    "has",
    "set",
    "delete",
]
