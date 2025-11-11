"""
Configuración de la aplicación.

Este módulo carga todas las variables de entorno necesarias para la aplicación.
Usa pydantic-settings para validación automática de tipos y valores por defecto.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configuración de la aplicación cargada desde variables de entorno.

    Todas las variables se cargan del archivo .env o de las de entorno del sistema.
    """

    # Base de datos PostgreSQL
    # Formato: postgresql://usuario:contraseña@host:puerto/nombre_bd
    DATABASE_URL: str

    # Configuración de GitHub Organization
    # Token con permisos para hacer fork a la organización y gestionar repos
    GITHUB_ORG_NAME: str  # Nombre de la organización donde se harán los forks
    GITHUB_ORG_TOKEN: str  # Personal Access Token o GitHub App token con permisos: repo, workflow
    GITHUB_WEBHOOK_SECRET: str  # Secret para validar webhooks de GitHub

    # Configuración de Docker Hub
    # Credenciales para subir imágenes Docker
    DOCKER_HUB_USERNAME: str
    DOCKER_HUB_PASSWORD: str
    DOCKER_HUB_REPO: str  # Formato: username/nombre-repo

    # Configuración del servidor de deployment
    # Credenciales SSH para conectarse al servidor donde se hacen deploys
    SERVER_SSH_HOST: str
    SERVER_SSH_USER: str
    SERVER_SSH_KEY_PATH: str

    # Dominio base para los deployments
    # Ejemplo: hostingroble.com
    # Los subdominios se generarán automáticamente: usuario-repo.hostingroble.com
    DOMAIN_BASE: str

    # URLs de la aplicación
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"

    # Secret key para encriptación de tokens
    SECRET_KEY: str

    class Config:
        """Configuración de pydantic."""
        # Cargar variables desde archivo .env
        env_file = ".env"
        # Permitir mayúsculas y minúsculas en nombres de variables
        case_sensitive = False


# Instancia global de configuración
# Se carga una sola vez al iniciar la aplicación
settings = Settings()
