"""Object Traversal & Inspection Toolkit."""

__version__ = "0.1.0"

from .exceptions import InvalidPath, OtitError, PathNotFound
from .traversal import delete, find, get, has, leaves, omit, paths, pick, set, walk

__all__ = [
    "OtitError",
    "PathNotFound",
    "InvalidPath",
    "delete",
    "find",
    "get",
    "has",
    "leaves",
    "omit",
    "paths",
    "pick",
    "set",
    "walk",
]
