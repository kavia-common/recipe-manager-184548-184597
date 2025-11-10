"""Recipe Backend API package.

This module provides accessors for the FastAPI app without causing side-effect
imports at package import time. Importing the app eagerly in __init__ can
trigger startup errors if dependencies are not ready. Use create_app() or
get_app() to obtain an application instance.
"""

from typing import Optional
from fastapi import FastAPI

# Avoid importing the app at module import time to prevent side effects.
# from .main import app, create_app  # do not import app here

# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    This function delegates to src.api.main.create_app to construct the app.
    """
    from .main import create_app as _create_app
    return _create_app()

# PUBLIC_INTERFACE
def get_app() -> FastAPI:
    """Get the pre-instantiated FastAPI app instance.

    Returns the module-level 'app' created in src.api.main when imported,
    without importing it eagerly at package import time here.
    """
    from .main import app as _app
    return _app

__all__ = ["create_app", "get_app"]
