from collections.abc import Sequence
from typing import TypeAlias

PathSegment: TypeAlias = str | int
Path: TypeAlias = str | Sequence[PathSegment]


def parse_path(path: Path) -> tuple[PathSegment, ...]:
    if isinstance(path, str):
        if not path:
            return ()

        return tuple(path.split("."))

    return tuple(path)
