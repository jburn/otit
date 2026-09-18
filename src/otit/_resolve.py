import inspect
from collections.abc import Iterator, Mapping, MutableMapping, MutableSequence, Sequence
from enum import Enum
from typing import Any

from ._path import PathSegment


class _ResolutionError(Exception):
    """Internal error raised when a path segment cannot be resolved."""

class _SegmentKind(Enum):
    MAPPING = "mapping"
    SEQUENCE = "sequence"
    ATTRIBUTE = "attribute"


def _sequence_index(segment: PathSegment) -> int:
    """Convert a path segment to a sequence index."""
    try:
        return int(segment)
    except (TypeError, ValueError):
        raise _ResolutionError from None

def resolved_segment(
    obj: Any,
    segment: PathSegment,
) -> tuple[PathSegment, _SegmentKind]:
    """Return the canonical segment and its traversal kind."""
    if isinstance(obj, Mapping):
        return segment, _SegmentKind.MAPPING

    if (
        isinstance(obj, Sequence)
        and not isinstance(obj, (str, bytes, bytearray))
    ):
        return _sequence_index(segment), _SegmentKind.SEQUENCE

    if not isinstance(segment, str):
        raise _ResolutionError from None

    return segment, _SegmentKind.ATTRIBUTE

def resolve(obj: Any, segment: PathSegment) -> Any:
    """Resolve one path segment against an object."""
    if isinstance(obj, Mapping):
        try:
            return obj[segment]
        except KeyError:
            raise _ResolutionError from None

    if (
        isinstance(obj, Sequence)
        and not isinstance(obj, (str, bytes, bytearray))
    ):
        index = _sequence_index(segment)

        try:
            return obj[index]
        except IndexError:
            raise _ResolutionError from None

    if not isinstance(segment, str):
        raise _ResolutionError from None

    try:
        inspect.getattr_static(obj, segment)
    except AttributeError:
        raise _ResolutionError from None

    return getattr(obj, segment)


def assign(
    obj: Any,
    segment: PathSegment,
    value: Any,
    *,
    create: bool=False,
) -> None:
    """Assign a value to one path segment."""
    if isinstance(obj, MutableMapping):
        if not create and segment not in obj:
            raise _ResolutionError
        obj[segment] = value
        return

    if (
        isinstance(obj, MutableSequence)
        and not isinstance(obj, (str, bytes, bytearray))
    ):
        index = _sequence_index(segment)

        try:
            obj[index] = value
        except IndexError:
            raise _ResolutionError from None

        return

    if not isinstance(segment, str):
        raise _ResolutionError from None

    if not create:
        try:
            inspect.getattr_static(obj, segment)
        except AttributeError:
            raise _ResolutionError from None

    setattr(obj, segment, value)


def remove(obj: Any, segment: PathSegment) -> None:
    """Remove the value at one path segment."""
    if isinstance(obj, MutableMapping):
        try:
            del obj[segment]
        except KeyError:
            raise _ResolutionError from None

        return

    if (
        isinstance(obj, MutableSequence)
        and not isinstance(obj, (str, bytes, bytearray))
    ):
        index = _sequence_index(segment)

        try:
            del obj[index]
        except IndexError:
            raise _ResolutionError from None

        return

    if not isinstance(segment, str):
        raise _ResolutionError from None

    try:
        inspect.getattr_static(obj, segment)
    except AttributeError:
        raise _ResolutionError from None

    delattr(obj, segment)

def iter_children(
    obj: Any,
) -> Iterator[tuple[PathSegment, Any]]:
    """Yield directly traversable children of an object."""
    if isinstance(obj, Mapping):
        yield from obj.items()
        return

    if (
        isinstance(obj, Sequence)
        and not isinstance(obj, (str, bytes, bytearray))
    ):
        yield from enumerate(obj)
        return

    try:
        attributes = vars(obj)
    except TypeError:
        return

    yield from attributes.items()

def _is_leaf(obj: Any) -> bool:
    """Return whether an Object is a terminal traversal value"""
    if isinstance(obj, Mapping):
        return False

    if (
        isinstance(obj, Sequence)
        and not isinstance(obj, (str, bytes, bytearray))
    ):
        return False

    try:
        vars(obj)
    except TypeError:
        return True

    return False
