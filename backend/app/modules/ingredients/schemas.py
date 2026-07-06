"""Pydantic schemas for the ingredients module."""

from pydantic import BaseModel


class IngredientUnitResponse(BaseModel):
    unit: str
    amountInBase: float


class IngredientResponse(BaseModel):
    id: str
    name: str
    aliases: list[str]
    baseUnit: str
    units: list[IngredientUnitResponse]


class IngredientsResponse(BaseModel):
    ingredients: list[IngredientResponse]
