"""
Modelo de Repositorio.

Representa un repositorio de GitHub conectado a la aplicación.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class TechnologyEnum(str, enum.Enum):
    """
    Tecnologías soportadas para deployment.

    Cada tecnología tendrá un workflow diferente.
    """
    REACT_VITE = "react-vite"
    FASTAPI = "fastapi"
    NESTJS = "nestjs"


class Repo(Base):
    """
    Tabla de repositorios.

    Cada repo pertenece a un usuario y puede tener múltiples deployments.
    """

    __tablename__ = "repos"

    # ID único del repo
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ID del usuario dueño del repo
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Owner del repo original en GitHub (username o org)
    # Ejemplo: para https://github.com/facebook/react -> "facebook"
    original_owner = Column(String, nullable=False)

    # Nombre del repo original en GitHub
    # Ejemplo: para https://github.com/facebook/react -> "react"
    original_repo_name = Column(String, nullable=False)

    # URL completa del repo original
    # Ejemplo: "https://github.com/facebook/react"
    original_repo_url = Column(String, nullable=False)

    # Nombre del repo forkeado en la organización
    # Ejemplo: "react" (el fork se hace a la org configurada)
    forked_repo_name = Column(String, nullable=False)

    # URL completa del repo forkeado
    # Ejemplo: "https://github.com/mi-org/react"
    forked_repo_url = Column(String, nullable=True)

    # Branch a monitorear para deployments
    # Cada push a este branch disparará el workflow
    branch = Column(String, nullable=False, default="main")

    # Tecnología del proyecto
    # Determina qué tipo de workflow se generará
    technology = Column(Enum(TechnologyEnum), nullable=False)

    # Expresión cron para ejecución programada del workflow
    # Default: cada 6 horas (0 */6 * * *)
    cron_schedule = Column(String, nullable=False, default="0 */6 * * *")

    # Timestamp de creación
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con usuario
    # Un repo pertenece a un usuario
    user = relationship("User", back_populates="repos")

    # Relación con deployments
    # Un repo puede tener múltiples deployments
    deployments = relationship("Deployment", back_populates="repo", cascade="all, delete-orphan")

    # Relación con settings
    # Un repo tiene una configuración (env_vars, build_args)
    settings = relationship("Settings", back_populates="repo", uselist=False, cascade="all, delete-orphan")
