"""Domain exceptions for the integrations module."""


class IntegrationsException(Exception):
    """Base exception for integrations module errors."""


class KeepNotConnectedError(IntegrationsException):
    """Raised when a user has no active Google Keep connection."""


class KeepMirrorNotFoundError(IntegrationsException):
    """Raised when a Keep list mirror does not exist or does not belong to the user."""


class KeepAuthenticationError(IntegrationsException):
    """Raised when gkeepapi/gpsoauth authentication against Google fails."""


class KeepNoteMissingError(IntegrationsException):
    """Raised when a mirror's Keep note no longer exists (e.g. deleted directly in Keep)."""


class KeepEncryptionError(IntegrationsException):
    """Raised when master token encryption/decryption fails."""
