from typing import Any

from ._path import Path, parse_path
from ._resolve import resolve
from .exceptions import PathNotFound

_MISSING = object()


def get(
    obj: Any,
    path: Path,
    *,
    default: Any = _MISSING,
) -> Any:
    segments = parse_path(path)
    current = obj

    for position, segment in enumerate(segments):
        try:
            current = resolve(current, segment)
        except (KeyError, IndexError, AttributeError, TypeError, ValueError):
            if default is not _MISSING:
                return default

            raise PathNotFound(
                path=path,
                segment=segment,
                position=position,
            ) from None

    return current


def has(obj: Any, path: Path) -> bool:
    try:
        get(obj, path)
    except PathNotFound:
        return False

    return True
