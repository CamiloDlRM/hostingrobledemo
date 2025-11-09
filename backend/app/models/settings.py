"""
Modelo de Settings.

Guarda la configuración de deployment de un repo.
"""

from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Settings(Base):
    """
    Tabla de configuración de repos.

    Guarda las variables de entorno y build arguments para cada repo.
    Estos valores se usan al generar el workflow y al hacer el deployment.
    """

    __tablename__ = "settings"

    # ID único
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ID del repo al que pertenece
    # Relación 1-a-1: cada repo tiene una configuración
    repo_id = Column(UUID(as_uuid=True), ForeignKey("repos.id"), nullable=False, unique=True)

    # Variables de entorno para el container
    # Formato JSON: {"PORT": "3000", "NODE_ENV": "production"}
    # Estas variables se pasan al container con -e en docker run
    env_vars = Column(JSON, nullable=True, default={})

    # Build arguments para el Dockerfile
    # Formato JSON: {"NODE_VERSION": "18", "APP_ENV": "prod"}
    # Estos argumentos se pasan con --build-arg en docker build
    build_args = Column(JSON, nullable=True, default={})

    # Timestamp de última actualización
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relación con repo
    repo = relationship("Repo", back_populates="settings")
