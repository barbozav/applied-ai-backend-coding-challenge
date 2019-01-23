from challenge.errors import ChallengeError


class ServiceError(ChallengeError):
    """Base event service error."""


class ClientError(ServiceError):
    """External service client error."""


class TranslatorError(ServiceError):
    """Translation service error."""
