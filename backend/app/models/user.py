"""
Modelo de Usuario.

Representa un usuario de la aplicación que se autentica vía GitHub.
"""

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class User(Base):
    """
    Tabla de usuarios.

    Usuarios de la plataforma que pueden gestionar repositorios.
    Ya no se usa OAuth de GitHub - autenticación simplificada.
    """

    __tablename__ = "users"

    # ID único del usuario (UUID generado automáticamente)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Username del usuario (único en toda la aplicación)
    username = Column(String, unique=True, nullable=False, index=True)

    # Email del usuario
    email = Column(String, nullable=True)

    # Timestamp de creación
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con repos
    # Un usuario puede tener múltiples repos
    # cascade="all, delete-orphan" significa que si se borra un usuario, se borran sus repos
    repos = relationship("Repo", back_populates="user", cascade="all, delete-orphan")
