"""Object Traversal & Inspection Toolkit."""

__version__ = "0.1.0"

from .exceptions import OtitError, PathNotFound
from .traversal import get, has

__all__ = [
    "OtitError",
    "PathNotFound",
    "get",
    "has",
]