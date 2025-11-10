from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, Response
from sqlalchemy.orm import Session

from .database import get_db
from .models import Recipe as RecipeModel
from .repository import RecipeRepository
from .schemas import (
    RecipeCreate,
    RecipeOut,
    RecipeUpdate,
    from_db_ingredients,
    from_db_tags,
)

router = APIRouter(prefix="/recipes", tags=["Recipes"])


def to_recipe_out(model: RecipeModel) -> RecipeOut:
    """
    Convert ORM model to API schema while transforming fields.
    """
    return RecipeOut(
        id=model.id,
        title=model.title,
        ingredients=from_db_ingredients(model.ingredients),
        instructions=model.instructions,
        tags=from_db_tags(model.tags) or [],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[RecipeOut],
    summary="List recipes",
    description="Retrieve a paginated list of recipes.",
)
def list_recipes(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return"),
    db: Session = Depends(get_db),
) -> List[RecipeOut]:
    """Return a list of recipes with pagination."""
    repo = RecipeRepository(db)
    items = repo.list(skip=skip, limit=limit)
    return [to_recipe_out(m) for m in items]


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=RecipeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a recipe",
    description="Create a new recipe with title, ingredients, and instructions.",
)
def create_recipe(
    payload: RecipeCreate,
    db: Session = Depends(get_db),
) -> RecipeOut:
    """Create and return a new recipe."""
    repo = RecipeRepository(db)
    created = repo.create(payload)
    return to_recipe_out(created)


# PUBLIC_INTERFACE
@router.get(
    "/{id}",
    response_model=RecipeOut,
    summary="Get recipe by ID",
)
def get_recipe(
    id: int = Path(..., ge=1, description="Recipe ID"),
    db: Session = Depends(get_db),
) -> RecipeOut:
    """Retrieve a recipe by ID."""
    repo = RecipeRepository(db)
    model = repo.get(id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return to_recipe_out(model)


# PUBLIC_INTERFACE
@router.put(
    "/{id}",
    response_model=RecipeOut,
    summary="Update a recipe",
)
def update_recipe(
    payload: RecipeUpdate,
    id: int = Path(..., ge=1, description="Recipe ID"),
    db: Session = Depends(get_db),
) -> RecipeOut:
    """Update a recipe and return the updated entity."""
    repo = RecipeRepository(db)
    model = repo.get(id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    updated = repo.update(model, payload)
    return to_recipe_out(updated)


# PUBLIC_INTERFACE
@router.delete(
    "/{id}",
    status_code=204,
    summary="Delete a recipe",
)
def delete_recipe(
    id: int = Path(..., ge=1, description="Recipe ID"),
    db: Session = Depends(get_db),
):
    """Delete a recipe by ID and return no content.

    This endpoint returns 204 No Content with an empty body. Do not attach any
    response_model, response_class, or default return value to 204 routes.
    """
    repo = RecipeRepository(db)
    model = repo.get(id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    repo.delete(model)
    # Explicitly return an empty Response to ensure no body for 204 No Content
    return Response(status_code=204)
