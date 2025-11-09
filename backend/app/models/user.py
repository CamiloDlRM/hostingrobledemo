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

    Cada usuario tiene una cuenta de GitHub y puede tener múltiples repos conectados.
    El token de GitHub se guarda encriptado para seguridad.
    """

    __tablename__ = "users"

    # ID único del usuario (UUID generado automáticamente)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Username de GitHub (único en toda la aplicación)
    username = Column(String, unique=True, nullable=False, index=True)

    # Email del usuario (obtenido de GitHub)
    email = Column(String, nullable=True)

    # ID del usuario en GitHub (para referencia)
    github_user_id = Column(String, unique=True, nullable=False, index=True)

    # Token de acceso de GitHub (ENCRIPTADO)
    # Este token se usa para hacer llamadas a la API de GitHub en nombre del usuario
    # NUNCA almacenar en texto plano, usar encrypt_token() de security.py
    github_token = Column(String, nullable=False)

    # Timestamp de creación
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación con repos
    # Un usuario puede tener múltiples repos
    # cascade="all, delete-orphan" significa que si se borra un usuario, se borran sus repos
    repos = relationship("Repo", back_populates="user", cascade="all, delete-orphan")
