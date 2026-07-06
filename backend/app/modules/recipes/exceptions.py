"""Domain exceptions for the recipes module."""


class RecipeNotFoundError(Exception):
    """Raised when a recipe cannot be found."""


class TagNotFoundError(Exception):
    """Raised when a tag cannot be found."""


class InvalidRecipeCategoryError(Exception):
    """Raised when recipe category is not one of the allowed values."""


class RecipeValidationError(Exception):
    """Raised when recipe payload fails validation."""


class DuplicateTagNameError(Exception):
    """Raised when a tag name already exists in the family."""


class ShoppingListNotFoundError(Exception):
    """Raised when target shopping list is missing or belongs to another family."""
