"""Domain exceptions for the family module."""


class FamilyException(Exception):
    """Base exception for family module errors."""


class FamilyNotFoundError(FamilyException):
    """Raised when the user has no family or the family does not exist."""


class AlreadyInFamilyError(FamilyException):
    """Raised when a user who is already in a family tries to create or join one."""


class NotFamilyOwnerError(FamilyException):
    """Raised when a non-owner attempts an owner-only operation."""


class CannotRemoveOwnerError(FamilyException):
    """Raised when trying to remove the family owner from the family."""


class MemberNotFoundError(FamilyException):
    """Raised when the target user is not a member of the family."""


class MemberLimitReachedError(FamilyException):
    """Raised when the family plan member limit is reached."""


class InvitationNotFoundError(FamilyException):
    """Raised when an invitation token does not exist."""


class InvitationExpiredError(FamilyException):
    """Raised when an invitation link has expired."""


class InvitationAlreadyAcceptedError(FamilyException):
    """Raised when an invitation has already been used."""
