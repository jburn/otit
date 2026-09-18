class OtitError(Exception):
    """Base exception for OTIT."""

class InvalidPath(OtitError):
    """Raised when a path is invalid for the requested operation."""

class PathNotFound(OtitError):
    """Raised when a path cannot be resolved."""

    def __init__(
        self,
        path: object,
        segment: object,
        position: int,
    ) -> None:
        self.path = path
        self.segment = segment
        self.position = position

        super().__init__(
            f"Could not resolve segment {segment!r} "
            f"at position {position} in path {path!r}"
        )
