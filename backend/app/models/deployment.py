"""
Modelo de Deployment.

Representa un deployment de un repositorio.
Cada deployment tiene un estado que se actualiza vía webhooks de GitHub.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base


class DeploymentStatusEnum(str, enum.Enum):
    """
    Estados posibles de un deployment.

    El flujo normal es: pending → building → deploying → success
    Si falla en cualquier punto: → failed
    """
    PENDING = "pending"        # Workflow creado, esperando que corra
    BUILDING = "building"      # GitHub Actions está construyendo la imagen
    DEPLOYING = "deploying"    # Imagen construida, desplegando container
    SUCCESS = "success"        # Deployment exitoso
    FAILED = "failed"          # Falló en algún paso


class Deployment(Base):
    """
    Tabla de deployments.

    Cada deployment representa una ejecución del workflow de GitHub Actions.
    El estado se actualiza automáticamente vía webhooks de GitHub.
    """

    __tablename__ = "deployments"

    # ID único del deployment
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ID del repo al que pertenece
    repo_id = Column(UUID(as_uuid=True), ForeignKey("repos.id"), nullable=False)

    # SHA del commit que se deployó
    # Permite saber exactamente qué código se deployó
    commit_sha = Column(String, nullable=True)

    # Estado actual del deployment
    # Se actualiza automáticamente vía webhooks de GitHub
    status = Column(Enum(DeploymentStatusEnum), nullable=False, default=DeploymentStatusEnum.PENDING)

    # Nombre de la imagen Docker
    # Ejemplo: "username/repo:latest"
    docker_image = Column(String, nullable=True)

    # Nombre del container en el servidor
    # Ejemplo: "username-reponame"
    container_name = Column(String, nullable=True)

    # Puerto asignado al container
    # El usuario proporciona este puerto (manejado externamente)
    port = Column(Integer, nullable=True)

    # Dominio donde está el deployment
    # Ejemplo: "username-repo.hostingroble.com"
    domain = Column(String, nullable=True)

    # ID del workflow run en GitHub
    # Se usa para descargar los logs del deployment
    workflow_run_id = Column(String, nullable=True)

    # URL del workflow run en GitHub
    # Permite al usuario ver los logs directamente en GitHub
    workflow_run_url = Column(String, nullable=True)

    # Mensaje de error si el deployment falló
    # Se llena automáticamente al parsear los logs
    error_message = Column(Text, nullable=True)

    # Timestamp de inicio del deployment
    started_at = Column(DateTime(timezone=True), server_default=func.now())

    # Timestamp de finalización (success o failed)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Relación con repo
    repo = relationship("Repo", back_populates="deployments")
