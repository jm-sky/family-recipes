"""Domain exceptions for the shopping module."""


class ShoppingException(Exception):
    """Base exception for shopping module errors."""


class ShoppingListNotFoundError(ShoppingException):
    """Raised when a shopping list does not exist or is not in the user's family."""


class ShoppingItemNotFoundError(ShoppingException):
    """Raised when a shopping list item does not exist or is not in the list."""


class CategoryNotFoundError(ShoppingException):
    """Raised when a category does not exist or is not in the user's family."""


class InvalidUnitError(ShoppingException):
    """Raised when a provided unit is not in the predefined unit list."""
