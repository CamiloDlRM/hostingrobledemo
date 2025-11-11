"""
Rutas de la API.
"""

from .users import router as users_router
from .user_repos import router as user_repos_router
from .secrets import router as secrets_router
from .workflows import router as workflows_router
from .deployments import router as deployments_router

__all__ = ["users_router", "user_repos_router", "secrets_router", "workflows_router", "deployments_router"]
