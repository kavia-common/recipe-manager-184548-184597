from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .models import Recipe  # noqa: F401  # ensures model is registered for metadata
from .routers_recipes import router as recipes_router

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI instance with routes and middleware.

    The app includes:
    - CORS middleware permitting typical localhost development origins.
    - OpenAPI metadata for documentation.
    - Routers for recipe CRUD operations under /recipes.
    - Health check endpoint at /.
    """
    app = FastAPI(
        title="Recipe Manager API",
        description=(
            "A simple API to view, add, and manage recipes. "
            "Includes CRUD endpoints with SQLite persistence."
        ),
        version="0.1.0",
        contact={"name": "Recipe Manager"},
        openapi_tags=[
            {"name": "Health", "description": "Service health endpoints."},
            {"name": "Recipes", "description": "CRUD operations for recipes."},
        ],
    )

    # CORS for typical local dev frontends.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://localhost:3000",
            "http://127.0.0.1",
            "http://127.0.0.1:3000",
            "*",  # permissive for preview systems
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize database tables if not present (no migrations required).
    Base.metadata.create_all(bind=engine)

    # Register routers.
    app.include_router(recipes_router)

    @app.get("/", tags=["Health"], summary="Health Check")
    def health_check():
        """Basic health check endpoint."""
        return {"message": "Healthy"}

    @app.get(
        "/healthz",
        tags=["Health"],
        summary="Detailed Health Check",
        description="Kubernetes-style health endpoint that returns 200 OK when the service is ready.",
    )
    def healthz():
        """Readiness probe endpoint returning simple OK JSON."""
        return {"status": "ok"}

    # Note: To seed example data, POST to /recipes with:
    # {
    #   "title": "Pasta Primavera",
    #   "ingredients": ["pasta", "tomatoes", "basil"],
    #   "instructions": "Boil pasta. Mix with tomatoes and basil. Serve warm.",
    #   "tags": ["italian", "vegetarian"]
    # }
    return app


# Instantiate app for ASGI servers like Uvicorn.
app = create_app()
