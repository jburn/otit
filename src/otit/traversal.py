import builtins
import copy
from collections.abc import Callable, Iterator
from typing import Any

from ._path import Path, PathSegment, parse_path
from ._resolve import (
    _is_leaf,
    _ResolutionError,
    _SegmentKind,
    assign,
    iter_children,
    remove,
    resolve,
    resolved_segment,
)
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
    """Resolve the parent object and final segment of a path."""
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

_NormalizedPath = tuple[
    tuple[PathSegment, _SegmentKind],
    ...
]

def _is_descendant(
    path: _NormalizedPath,
    parent: _NormalizedPath,
) -> bool:
    return (
        len(path) > len(parent)
        and path[:len(parent)] == parent
    )

def _remove_redundant_paths(
    paths: list[_NormalizedPath],
) -> list[_NormalizedPath]:
    result: list[_NormalizedPath] = []

    for path in sorted(paths, key=len):
        if any(
            path == existing
            or _is_descendant(path, existing)
            for existing in result
        ):
            continue

        result.append(path)

    return result

def _path_segments(
    path: _NormalizedPath,
) -> tuple[PathSegment, ...]:
    return tuple(
        segment
        for segment, _ in path
    )

def _prepare_omit_paths(
    obj: Any,
    paths: tuple[Path, ...],
) -> list[_NormalizedPath]:
    normalized: list[_NormalizedPath] = []

    for path in paths:
        resolved = _normalize_path(obj, path)

        if not resolved:
            raise InvalidPath(
                "The root path cannot be used with omit"
            )

        normalized.append(resolved)

    normalized = _remove_redundant_paths(normalized)

    return sorted(
        normalized,
        key=_omit_sort_key,
        reverse=True,
    )

def _omit_sort_key(
    path: _NormalizedPath,
) -> tuple[int, int]:
    segment, kind = path[-1]

    sequence_index = (
        segment
        if kind is _SegmentKind.SEQUENCE
        and isinstance(segment, int)
        else -1
    )

    return len(path), sequence_index

def _normalize_path(
    obj: Any,
    path: Path,
) -> tuple[tuple[PathSegment, _SegmentKind], ...]:
    """Return canonical path segments with their traversal kinds."""
    segments = parse_path(path)
    current = obj
    normalized: list[tuple[PathSegment, _SegmentKind]] = []

    for position, segment in enumerate(segments):
        try:
            normalized_segment = resolved_segment(
                current,
                segment,
            )
            current = resolve(current, segment)
        except _ResolutionError:
            raise _path_not_found(
                path,
                segment,
                position,
            ) from None

        normalized.append(normalized_segment)

    return tuple(normalized)

class _PickNode:
    def __init__(self, kind: _SegmentKind | None = None) -> None:
        self.kind = kind
        self.children: dict[PathSegment, _PickNode] = {}
        self.value: Any = _MISSING

def _insert_picked(
    root: _PickNode,
    path: tuple[tuple[PathSegment, _SegmentKind], ...],
    value: Any,
) -> None:
    current = root

    for segment, kind in path:
        if current.value is not _MISSING:
            return

        if current.kind is None:
            current.kind = kind

        child = current.children.get(segment)

        if child is None:
            child = _PickNode()
            current.children[segment] = child

        current = child

    current.value = copy.deepcopy(value)
    current.children.clear()

def _materialize_picked(node: _PickNode) -> Any:
    if node.value is not _MISSING:
        return node.value

    if node.kind is _SegmentKind.SEQUENCE:
        return [
            _materialize_picked(child)
            for _, child in sorted(node.children.items())
        ]

    return {
        segment: _materialize_picked(child)
        for segment, child in node.children.items()
    }

def get(
    obj: Any,
    path: Path,
    *,
    default: Any = _MISSING,
) -> Any:
    """Return the value at a path.

    Args:
        obj: Object to traverse.
        path: Dot-separated string or sequence of path segments.
        default: Value returned when the path cannot be resolved.

    Returns:
        The resolved value, or `default` if provided and the path
        cannot be resolved.

    Raises:
        PathNotFound: If the path cannot be resolved and no default
            was provided.
    """
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
    """Return whether a path can be resolved.

    Args:
        obj: Object to traverse.
        path: Dot-separated string or sequence of path segments.

    Returns:
        `True` if the path can be resolved, otherwise `False`.

    Notes:
        The empty path refers to the root object and therefore always
        resolves successfully.
    """
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
    """Set the value at a path.

    The parent path must already exist. By default, the final target
    must also exist. Set `create=True` to allow creation of a final
    mapping key or object attribute.

    `create=True` does not create missing parent containers or extend
    sequences.

    Args:
        obj: Object to modify.
        path: Path to the target value.
        value: Value to assign.
        create: Whether a missing final key or attribute may be created.

    Raises:
        PathNotFound: If the path cannot be resolved.
        InvalidPath: If the path refers to the root object.
    """
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
    """Delete the value at a path.

    The complete path must already exist. For mappings, the target key
    is removed. For mutable sequences, the target item is removed and
    subsequent items shift position. For objects, the target attribute
    is deleted.

    Args:
        obj: Object to modify.
        path: Path to the value to delete.

    Raises:
        PathNotFound: If the path cannot be resolved.
        InvalidPath: If the path refers to the root object.
    """
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

    ancestors.add(obj_id)

    try:
        for segment, value in iter_children(obj):
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
    """Yield every reachable child and its path.

    Paths are returned as tuples of string and integer segments.
    The root object itself is not yielded.

    Cycles are not traversed recursively, but shared objects reachable
    through different paths are visited independently.

    Args:
        obj: Object to traverse.

    Yields:
        Pairs of `(path, value)` for each reachable child.
    """
    yield from _walk(obj, (), builtins.set())

def find(
    obj: Any,
    predicate: Callable[[Any], bool],
) -> Iterator[tuple[tuple[PathSegment, ...], Any]]:
    """Yield values matching a predicate and their paths.

    Traverses the object using `walk()` and yields each value for which
    the predicate returns `True`.

    Args:
        obj: Object to traverse.
        predicate: Function called with each reachable value.

    Yields:
        Pairs of `(path, value)` for matching values.
    """
    for path, value in walk(obj):
        if predicate(value):
            yield path, value

def paths(
    obj: Any
) -> Iterator[tuple[PathSegment, ...]]:
    """Yield the path of every reachable child.

    Paths are returned as tuples of string and integer segments.
    The root object itself is not included.

    Args:
        obj: Object to traverse.

    Yields:
        The path of each reachable child.
    """
    for path, _ in walk(obj):
        yield path

def leaves(
    obj: Any
) -> Iterator[tuple[tuple[PathSegment, ...], Any]]:
    """Yield every terminal value and its path.

    A leaf is a value that OTIT does not treat as a traversable
    container. Empty mappings and sequences are not considered leaves.

    Args:
        obj: Object to traverse.

    Yields:
        Pairs of `(path, value)` for each leaf value.
    """
    for path, value in walk(obj):
        if _is_leaf(value):
            yield path, value

def pick(
    obj: Any,
    *selected_paths: Path,
) -> Any:
    """Return a structure containing only selected paths.

    Mapping keys are preserved. Object attributes are represented as
    dictionary keys. Selected sequence items are compacted while
    preserving their original order.

    The original object is not modified.

    Args:
        obj: Object to traverse.
        selected_paths: Paths whose values should be included.

    Returns:
        A new structure containing the selected paths.

    Raises:
        PathNotFound: If a requested path cannot be resolved.
        InvalidPath: If a requested path refers to the root object.
    """
    root = _PickNode()

    for path in selected_paths:
        normalized = _normalize_path(obj, path)

        if not normalized:
            raise InvalidPath(
                "The root path cannot be used with pick"
            )

        value = get(obj, path)

        _insert_picked(
            root,
            normalized,
            value,
        )

    return _materialize_picked(root)

def omit(
    obj: Any,
    *omitted_paths: Path,
) -> Any:
    """Return a copy of an object with selected paths removed.

    All paths are resolved against the original object. Removing
    sequence items therefore does not affect the meaning of later
    paths.

    If a parent path is omitted, descendant paths are redundant and
    are ignored.

    Args:
        obj: Object to copy.
        omitted_paths: Paths to remove from the copied object.

    Returns:
        A copy of `obj` with the requested paths removed.

    Raises:
        PathNotFound: If a requested path cannot be resolved.
        InvalidPath: If a requested path refers to the root object.
    """
    prepared = _prepare_omit_paths(
        obj,
        omitted_paths,
    )

    result = copy.deepcopy(obj)

    for path in prepared:
        delete(
            result,
            _path_segments(path),
        )

    return result
