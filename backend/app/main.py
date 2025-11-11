"""
Aplicación principal de FastAPI.

Este es el punto de entrada de la aplicación.
Configura CORS, incluye los routers y crea las tablas al iniciar.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.database import create_tables
from app.core.config import settings
from app.api.routes import (
    users_router,
    user_repos_router,
    secrets_router,
    workflows_router,
    deployments_router
)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear instancia de FastAPI
app = FastAPI(
    title="GitHub Deployment Automation",
    description="Automatiza deployments usando GitHub Apps y GitHub Actions",
    version="1.0.0"
)

# Configurar CORS para permitir requests del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,  # Frontend en desarrollo
        "http://localhost:3000",  # Alternativa
        "http://localhost:5173",  # Vite default
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los headers
)


@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.

    Crea todas las tablas en la base de datos si no existen.
    """
    logger.info("Starting application...")
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully")


@app.get("/")
async def root():
    """
    Endpoint raíz para verificar que la API está corriendo.

    Returns:
        dict: Mensaje de bienvenida
    """
    return {
        "message": "GitHub Deployment Automation API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Útil para verificar que el servidor está activo.

    Returns:
        dict: Estado del servidor
    """
    return {"status": "healthy"}


# Incluir routers
# Cada router maneja un conjunto de endpoints relacionados
# Todos los endpoints comienzan con /api

# Rutas de usuarios
app.include_router(
    users_router,
    prefix="/api",
    tags=["Users"]
)

# Rutas de repos
app.include_router(
    user_repos_router,
    prefix="/api",
    tags=["Repositories"]
)

# Rutas de configuración (secrets, env vars, build args)
app.include_router(
    secrets_router,
    prefix="/api",
    tags=["Settings"]
)

# Rutas de workflows y deployments
app.include_router(
    workflows_router,
    prefix="/api",
    tags=["Workflows"]
)

# Rutas de deployments y webhooks
app.include_router(
    deployments_router,
    prefix="/api",
    tags=["Deployments"]
)


if __name__ == "__main__":
    # Esto solo se ejecuta si corres python main.py directamente
    # En producción, usar uvicorn desde la línea de comandos
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload en desarrollo
    )
