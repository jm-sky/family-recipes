"""Pydantic schemas for the shopping module."""

from datetime import datetime

from pydantic import BaseModel, Field

# ==================== Categories ====================


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    icon: str | None = Field(default=None, max_length=64)
    sortOrder: int | None = None


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    icon: str | None = Field(default=None, max_length=64)
    sortOrder: int | None = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    icon: str | None = None
    sortOrder: int


class CategoriesResponse(BaseModel):
    categories: list[CategoryResponse]


# ==================== Shopping lists ====================


class ShoppingListCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ShoppingListUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ShoppingListResponse(BaseModel):
    id: str
    name: str
    itemCount: int = 0
    checkedCount: int = 0
    createdAt: datetime
    updatedAt: datetime


class ShoppingListsResponse(BaseModel):
    lists: list[ShoppingListResponse]


# ==================== Shopping list items ====================


class ShoppingItemCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    categoryId: str | None = None
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=32)


class QuickAddRequest(BaseModel):
    text: str = Field(min_length=1, max_length=255)


class ShoppingItemUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    categoryId: str | None = None
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=32)
    isChecked: bool | None = None
    position: int | None = None


class ShoppingItemResponse(BaseModel):
    id: str
    listId: str
    name: str
    categoryId: str | None = None
    ingredientId: str | None = None
    quantity: float | None = None
    unit: str | None = None
    isChecked: bool
    position: int
    createdAt: datetime
    updatedAt: datetime


class ShoppingListDetailResponse(ShoppingListResponse):
    items: list[ShoppingItemResponse]


class ReorderEntry(BaseModel):
    id: str
    position: int


class ReorderRequest(BaseModel):
    items: list[ReorderEntry]


# ==================== Product suggestions ====================


class ProductSuggestionResponse(BaseModel):
    name: str
    ingredientId: str | None = None
    categoryId: str | None = None
    categoryIcon: str | None = None
    source: str  # ingredient | recent | popular


class ProductSuggestionsResponse(BaseModel):
    suggestions: list[ProductSuggestionResponse]
