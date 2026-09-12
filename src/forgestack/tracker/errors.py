"""Errors raised by tracker providers."""


class TrackerError(RuntimeError):
    """Base error for tracker configuration and provider failures."""


class TrackerConfigurationError(TrackerError):
    """The selected tracker is missing required local configuration."""


class TrackerNotFoundError(TrackerError):
    """A requested tracker record could not be found."""


class TrackerRequestError(TrackerError):
    """A tracker API request failed."""

    def __init__(self, status: int | None, detail: str) -> None:
        self.status = status
        self.detail = detail
        prefix = f"HTTP {status}: " if status is not None else ""
        super().__init__(prefix + detail)
