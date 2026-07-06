"""Pydantic schemas for the recipes module."""

from datetime import datetime

from pydantic import BaseModel, Field

# ==================== Tags ====================


class TagCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=64)


class TagResponse(BaseModel):
    id: str
    name: str


class TagsResponse(BaseModel):
    tags: list[TagResponse]


# ==================== Recipe ingredients ====================


class RecipeIngredientInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=32)


class RecipeIngredientResponse(BaseModel):
    id: str
    name: str
    ingredientId: str | None = None
    quantity: float | None = None
    unit: str | None = None
    sortOrder: int


# ==================== Recipes ====================


class RecipeCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    sourceUrl: str | None = Field(default=None, max_length=1024)
    category: str = Field(min_length=1, max_length=32)
    servings: int | None = Field(default=None, ge=1)
    ingredients: list[RecipeIngredientInput] = Field(min_length=1)
    tagIds: list[str] = Field(default_factory=list)


class RecipeUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    sourceUrl: str | None = Field(default=None, max_length=1024)
    category: str | None = Field(default=None, min_length=1, max_length=32)
    servings: int | None = Field(default=None, ge=1)
    ingredients: list[RecipeIngredientInput] | None = None
    tagIds: list[str] | None = None


class RecipeSummaryResponse(BaseModel):
    id: str
    title: str
    sourceUrl: str | None = None
    imageUrl: str | None = None
    category: str
    servings: int | None = None
    tagIds: list[str]
    createdAt: datetime
    updatedAt: datetime


class RecipesResponse(BaseModel):
    recipes: list[RecipeSummaryResponse]


class RecipeDetailResponse(RecipeSummaryResponse):
    ingredients: list[RecipeIngredientResponse]


class RecipeImageResponse(BaseModel):
    imageUrl: str


class AddToListRequest(BaseModel):
    listId: str


class AddToListResponse(BaseModel):
    addedCount: int
    skippedCount: int
