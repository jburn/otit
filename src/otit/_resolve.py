from collections.abc import Mapping, Sequence
from typing import Any

from ._path import PathSegment


def resolve(obj: Any, segment: PathSegment) -> Any:
    if isinstance(obj, Mapping):
        return obj[segment]

    if (
        isinstance(obj, Sequence)
        and not isinstance(obj, (str, bytes, bytearray))
    ):
        index = int(segment)
        return obj[index]

    if not isinstance(segment, str):
        raise TypeError(
            f"Object attributes require string segments, got {segment!r}"
        )

    return getattr(obj, segment)
