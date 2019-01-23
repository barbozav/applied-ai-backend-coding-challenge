from challenge.errors import ChallengeError


class EventStoreError(ChallengeError):
    """Base event store error."""


class ReadError(EventStoreError):
    """Event store read operation error."""


class WriteError(EventStoreError):
    """Event store write operation error."""


class NotFoundError(ReadError):
    """Inexistent event stream error."""


class ConcurrencyError(WriteError):
    """Optimistic lock for concurrency error."""
