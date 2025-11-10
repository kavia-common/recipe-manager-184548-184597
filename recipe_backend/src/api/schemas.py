"""Pydantic schemas for Recipe requests and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, validator


def _list_to_csv(value: Optional[Union[str, List[str]]]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, list):
        return ",".join([v.strip() for v in value if str(v).strip() != ""])
    return str(value)


def _csv_to_list(value: Optional[str]) -> Optional[List[str]]:
    if value is None or value == "":
        return []
    return [part.strip() for part in value.split(",") if part.strip() != ""]


# PUBLIC_INTERFACE
class RecipeBase(BaseModel):
    """Base fields for creating or updating a recipe."""

    title: str = Field(..., description="Title of the recipe", examples=["Pasta Primavera"])
    ingredients: Union[List[str], str] = Field(
        ...,
        description="Ingredients as a list of strings or a newline-separated text",
        examples=[["pasta", "tomatoes", "basil"], "pasta\ntomatoes\nbasil"],
    )
    instructions: str = Field(
        ...,
        description="Step-by-step instructions for preparing the recipe",
        examples=["Boil pasta. Mix with tomatoes and basil. Serve warm."],
    )
    tags: Optional[Union[List[str], str]] = Field(
        default=None,
        description="Optional tags for categorization (list or comma-separated string)",
        examples=[["italian", "vegetarian"], "italian, vegetarian"],
    )

    @validator("title")
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v.strip()

    @validator("instructions")
    def instructions_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("instructions cannot be empty")
        return v.strip()


# PUBLIC_INTERFACE
class RecipeCreate(RecipeBase):
    """Schema used when creating a recipe."""
    pass


# PUBLIC_INTERFACE
class RecipeUpdate(BaseModel):
    """Schema used when updating a recipe (full update)."""

    title: Optional[str] = Field(None, description="Title of the recipe")
    ingredients: Optional[Union[List[str], str]] = Field(
        None, description="Ingredients as a list or newline-separated text"
    )
    instructions: Optional[str] = Field(
        None, description="Step-by-step instructions"
    )
    tags: Optional[Union[List[str], str]] = Field(
        None, description="Tags as a list or comma-separated string"
    )

    @validator("title")
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("title cannot be empty")
        return v.strip() if isinstance(v, str) else v

    @validator("instructions")
    def instructions_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("instructions cannot be empty")
        return v.strip() if isinstance(v, str) else v


# PUBLIC_INTERFACE
class RecipeOut(BaseModel):
    """Schema returned to clients for a recipe."""
    id: int = Field(..., description="Unique identifier for the recipe", examples=[1])
    title: str = Field(..., description="Title of the recipe")
    ingredients: List[str] = Field(
        default_factory=list, description="Ingredients as a list of strings"
    )
    instructions: str = Field(..., description="Preparation instructions")
    tags: List[str] = Field(default_factory=list, description="Optional list of tags")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")

    class Config:
        from_attributes = True  # allow ORM model conversion


def to_db_ingredients(value: Union[List[str], str]) -> str:
    """Normalize ingredients into newline-separated text for storage."""
    if isinstance(value, list):
        return "\n".join([v.strip() for v in value if str(v).strip() != ""])
    return value


def from_db_ingredients(value: str) -> List[str]:
    """Convert newline-separated ingredients text into a list."""
    if not value:
        return []
    return [line.strip() for line in value.splitlines() if line.strip() != ""]


def to_db_tags(value: Optional[Union[List[str], str]]) -> Optional[str]:
    return _list_to_csv(value)


def from_db_tags(value: Optional[str]) -> List[str]:
    return _csv_to_list(value)
