"""
Rutas para generación y gestión de workflows.

Endpoints:
- POST /repos/{repo_id}/deploy - Genera workflow y hace commit
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import re

from app.core.database import get_db
from app.core.config import settings as app_settings
from app.core.security import decrypt_token
from app.models import Repo, Settings, Deployment, DeploymentStatusEnum
from app.github import workflows

router = APIRouter()


class DeployRequest(BaseModel):
    """Request de POST /repos/{repo_id}/deploy"""
    port: int  # Puerto asignado por el usuario


class DeployResponse(BaseModel):
    """Response de POST /repos/{repo_id}/deploy"""
    deployment_id: str
    status: str
    message: str


@router.post("/repos/{repo_id}/deploy", response_model=DeployResponse)
def deploy_repo(
    repo_id: str = Path(...),
    request: DeployRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Crea un workflow de deployment y lo hace commit al repo.

    Este endpoint:
    1. Obtiene el repo y sus settings de la BD
    2. Genera el YAML del workflow según la tecnología
    3. Hace commit del workflow al repo del usuario
    4. Crea un deployment en la BD con status='pending'

    Args:
        repo_id: ID del repositorio
        request: Puerto para el deployment
        db: Sesión de base de datos

    Returns:
        DeployResponse: ID del deployment creado
    """
    try:
        # 1. Obtener repo
        repo = db.query(Repo).filter(Repo.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        # 2. Obtener settings
        repo_settings = db.query(Settings).filter(Settings.repo_id == repo_id).first()
        if not repo_settings:
            raise HTTPException(
                status_code=400,
                detail="Settings not configured. Please configure env_vars and build_args first."
            )

        # 3. Validar puerto
        if request.port < 1 or request.port > 65535:
            raise HTTPException(status_code=400, detail="Invalid port number")

        # 4. Generar nombre del container
        # Formato: owner-reponame (lowercase, sin caracteres especiales)
        container_name = f"{repo.repo_owner}-{repo.repo_name}".lower()
        container_name = re.sub(r'[^a-z0-9\-]', '', container_name)

        # 5. Generar nombre de la imagen Docker
        docker_image = f"{app_settings.DOCKER_HUB_REPO}:{container_name}"

        # 6. Generar dominio
        # Formato: owner-repo.hostingroble.com
        domain = f"{container_name}.{app_settings.DOMAIN_BASE}"

        # 7. Generar workflow YAML
        workflow_yaml = workflows.generate_workflow_yaml(
            technology=repo.technology,
            env_vars=repo_settings.env_vars or {},
            build_args=repo_settings.build_args or {},
            docker_repo=app_settings.DOCKER_HUB_REPO,
            container_name=container_name,
            port=request.port,
            branch=repo.branch
        )

        # 8. Obtener token del usuario
        user = repo.user
        token = decrypt_token(user.github_token)

        # 9. Hacer commit del workflow al repo
        commit_result = workflows.create_workflow_in_repo(
            token=token,
            owner=repo.repo_owner,
            repo=repo.repo_name,
            branch=repo.branch,
            workflow_content=workflow_yaml
        )

        # 10. Crear deployment en BD
        deployment = Deployment(
            repo_id=repo.id,
            commit_sha=commit_result.get("commit", {}).get("sha", ""),
            status=DeploymentStatusEnum.PENDING,
            docker_image=docker_image,
            container_name=container_name,
            port=request.port,
            domain=domain,
            started_at=datetime.utcnow()
        )
        db.add(deployment)
        db.commit()
        db.refresh(deployment)

        return DeployResponse(
            deployment_id=str(deployment.id),
            status="pending",
            message=f"Workflow created successfully. Deployment pending at {domain}"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating deployment: {str(e)}")
