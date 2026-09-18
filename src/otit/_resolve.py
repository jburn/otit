import inspect
from collections.abc import Iterator, Mapping, MutableMapping, MutableSequence, Sequence
from typing import Any

from ._path import PathSegment


class _ResolutionError(Exception):
    """Internal error raised when a path segment cannot be resolved."""


def resolve(obj: Any, segment: PathSegment) -> Any:
    if isinstance(obj, Mapping):
        try:
            return obj[segment]
        except KeyError:
            raise _ResolutionError from None

    if (
        isinstance(obj, Sequence)
        and not isinstance(obj, (str, bytes, bytearray))
    ):
        try:
            index = int(segment)
        except (TypeError, ValueError):
            raise _ResolutionError from None

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
    if isinstance(obj, MutableMapping):
        if not create and segment not in obj:
            raise _ResolutionError
        obj[segment] = value
        return

    if (
        isinstance(obj, MutableSequence)
        and not isinstance(obj, (str, bytes, bytearray))
    ):
        try:
            index = int(segment)
        except (TypeError, ValueError):
            raise _ResolutionError from None

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
        try:
            index = int(segment)
        except (TypeError, ValueError):
            raise _ResolutionError from None

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
