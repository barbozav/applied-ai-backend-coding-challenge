from challenge.errors import ChallengeError


class AggregateError(ChallengeError):
    """Base aggregate error."""


class InvalidEventError(AggregateError, ValueError):
    """Invalid event triggered error."""


class TranslationError(AggregateError):
    """Base Translation error."""


class InvalidStatusError(TranslationError, ValueError):
    """Invalid status transition error."""
