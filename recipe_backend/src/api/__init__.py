"""Recipe Backend API package.

This module exposes the FastAPI application instance and the app factory
for ASGI servers and external imports.
"""

from .main import app, create_app

__all__ = ["app", "create_app"]
