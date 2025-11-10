"""Repository layer for Recipes to abstract SQLAlchemy operations."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from .models import Recipe
from .schemas import (
    RecipeCreate,
    RecipeUpdate,
    to_db_ingredients,
    to_db_tags,
)


class RecipeRepository:
    """Data access methods for Recipe entities."""

    def __init__(self, db: Session):
        self.db = db

    def list(self, skip: int = 0, limit: int = 100) -> List[Recipe]:
        return (
            self.db.query(Recipe)
            .order_by(Recipe.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get(self, recipe_id: int) -> Optional[Recipe]:
        return self.db.query(Recipe).filter(Recipe.id == recipe_id).first()

    def create(self, data: RecipeCreate) -> Recipe:
        recipe = Recipe(
            title=data.title.strip(),
            ingredients=to_db_ingredients(data.ingredients),
            instructions=data.instructions.strip(),
            tags=to_db_tags(data.tags),
        )
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def update(self, recipe: Recipe, data: RecipeUpdate) -> Recipe:
        if data.title is not None:
            recipe.title = data.title.strip()
        if data.ingredients is not None:
            recipe.ingredients = to_db_ingredients(data.ingredients)
        if data.instructions is not None:
            recipe.instructions = data.instructions.strip()
        if data.tags is not None:
            recipe.tags = to_db_tags(data.tags)

        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def delete(self, recipe: Recipe) -> None:
        self.db.delete(recipe)
        self.db.commit()
