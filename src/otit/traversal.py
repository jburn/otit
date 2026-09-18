import builtins
from typing import Any
from collections.abc import Iterator

from ._path import Path, PathSegment, parse_path
from ._resolve import _ResolutionError, assign, iter_children, remove, resolve
from .exceptions import InvalidPath, PathNotFound

_MISSING = object()

def _path_not_found(
    path: Path,
    segment: PathSegment,
    position: int,
) -> PathNotFound:
    return PathNotFound(
        path=path,
        segment=segment,
        position=position,
    )

def _resolve_parent(
    obj: Any,
    path: Path,
) -> tuple[Any, PathSegment, int]:
    segments = parse_path(path)

    if not segments:
        raise InvalidPath(
            "The root path cannot be used for mutation"
        )

    current = obj

    for position, segment in enumerate(segments[:-1]):
        try:
            current = resolve(current, segment)
        except _ResolutionError:
            raise _path_not_found(
                path,
                segment,
                position,
            ) from None

    return current, segments[-1], len(segments) - 1

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
        except _ResolutionError:
            if default is not _MISSING:
                return default

            raise _path_not_found(
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

def set(
    obj: Any,
    path: Path,
    value: Any,
    create: bool = False
    ) -> None:
    parent, segment, position = _resolve_parent(obj, path)

    try:
        assign(
            parent,
            segment,
            value,
            create=create
        )
    except _ResolutionError:
        raise _path_not_found(
            path,
            segment,
            position,
        ) from None

def delete(obj: Any, path: Path) -> None:
    parent, segment, position = _resolve_parent(obj, path)

    try:
        remove(parent, segment)
    except _ResolutionError:
        raise _path_not_found(
            path,
            segment,
            position,
        ) from None

def _walk(
    obj: Any,
    path: tuple[PathSegment, ...],
    ancestors: builtins.set[int],
) -> Iterator[tuple[tuple[PathSegment, ...], Any]]:
    obj_id = id(obj)

    if obj_id in ancestors:
        return

    children = iter_children(obj)

    ancestors.add(obj_id)

    try:
        for segment, value in children:
            child_path = path + (segment,)

            yield child_path, value
            yield from _walk(
                value,
                child_path,
                ancestors,
            )
    finally:
        ancestors.remove(obj_id)

def walk(
    obj: Any,
) -> Iterator[tuple[tuple[PathSegment, ...], Any]]:
    yield from _walk(obj, (), builtins.set())
