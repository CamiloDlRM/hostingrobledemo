"""
Rutas para gestión de repositorios.

Endpoints:
- POST /repos - Fork de repositorio a la organización y setup de workflow
- GET /repos/user/{user_id} - Lista repos del usuario en la plataforma
- DELETE /repos/{repo_id} - Elimina un repo
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import time

from app.core.database import get_db
from app.core.config import settings
from app.github import auth, workflows
from app.models import User, Repo, TechnologyEnum, Settings

router = APIRouter()


class CreateRepoRequest(BaseModel):
    """Request de POST /repos"""
    repo_url: str
    branch: str = "main"
    technology: TechnologyEnum
    cron_schedule: str = "0 */6 * * *"  # Default: cada 6 horas


class RepoResponse(BaseModel):
    """Response de repos"""
    id: str
    original_owner: str
    original_repo_name: str
    original_repo_url: str
    forked_repo_name: str
    forked_repo_url: Optional[str]
    branch: str
    technology: str
    cron_schedule: str
    created_at: str


@router.post("/repos")
def create_repo_fork(
    request: CreateRepoRequest,
    user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Hace fork de un repositorio a la organización y configura el workflow.

    Flujo:
    1. Valida que el repositorio existe en GitHub
    2. Hace fork del repo a la organización
    3. Genera workflow con cron y deployment
    4. Hace commit del workflow al repo forkeado
    5. Guarda todo en la BD

    Args:
        request: Datos del repo (URL, branch, tecnología, cron)
        user_id: ID del usuario
        db: Sesión de base de datos

    Returns:
        dict: Datos del repo forkeado y configurado
    """
    try:
        # Obtener usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Parsear URL del repositorio
        try:
            original_owner, original_repo_name = auth.parse_repo_url(request.repo_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Verificar que el repositorio existe
        if not auth.check_repo_exists(original_owner, original_repo_name):
            raise HTTPException(
                status_code=404,
                detail=f"Repository {original_owner}/{original_repo_name} not found or not accessible"
            )

        # Verificar que no exista ya un fork de este repo para este usuario
        existing = db.query(Repo).filter(
            Repo.user_id == user.id,
            Repo.original_owner == original_owner,
            Repo.original_repo_name == original_repo_name
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Repository {original_owner}/{original_repo_name} already forked"
            )

        # Validar branch no vacío
        if not request.branch or not request.branch.strip():
            raise HTTPException(status_code=400, detail="Branch cannot be empty")

        # Validar cron expression (validación básica)
        if not request.cron_schedule or not request.cron_schedule.strip():
            raise HTTPException(status_code=400, detail="Cron schedule cannot be empty")

        # Hacer fork a la organización
        print(f"Forking {original_owner}/{original_repo_name} to {settings.GITHUB_ORG_NAME}...")
        fork_data = auth.fork_repository(original_owner, original_repo_name)

        # Esperar un poco para que GitHub procese el fork
        time.sleep(2)

        forked_repo_name = fork_data.get("name")
        forked_repo_url = fork_data.get("html_url")
        default_branch = fork_data.get("default_branch", request.branch)

        print(f"Fork created: {forked_repo_url}")

        # Generar workflow YAML con cron
        workflow_yaml = workflows.generate_workflow_yaml(
            technology=request.technology,
            env_vars={},  # Vacío por ahora, el usuario lo configura después
            build_args={},  # Vacío por ahora
            docker_repo=settings.DOCKER_HUB_REPO,
            container_name=f"{user.username}-{forked_repo_name}",
            port=3000,  # Puerto default, se puede hacer configurable
            branch=request.branch,
            cron_schedule=request.cron_schedule
        )

        # Commit workflow al repo forkeado
        print(f"Adding workflow to {settings.GITHUB_ORG_NAME}/{forked_repo_name}...")
        workflows.create_workflow_in_org_repo(
            repo=forked_repo_name,
            branch=default_branch,
            workflow_content=workflow_yaml
        )

        print("Workflow added successfully")

        # Guardar en BD
        repo = Repo(
            user_id=user.id,
            original_owner=original_owner,
            original_repo_name=original_repo_name,
            original_repo_url=request.repo_url.strip(),
            forked_repo_name=forked_repo_name,
            forked_repo_url=forked_repo_url,
            branch=request.branch.strip(),
            technology=request.technology,
            cron_schedule=request.cron_schedule.strip()
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)

        # Crear settings vacíos
        repo_settings = Settings(
            repo_id=repo.id,
            env_vars={},
            build_args={}
        )
        db.add(repo_settings)
        db.commit()

        return {
            "id": str(repo.id),
            "original_owner": repo.original_owner,
            "original_repo_name": repo.original_repo_name,
            "original_repo_url": repo.original_repo_url,
            "forked_repo_name": repo.forked_repo_name,
            "forked_repo_url": repo.forked_repo_url,
            "branch": repo.branch,
            "technology": repo.technology,
            "cron_schedule": repo.cron_schedule,
            "message": "Repository forked successfully and workflow added"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating fork: {str(e)}")


@router.get("/repos/user/{user_id}", response_model=List[RepoResponse])
def list_user_repos(user_id: str, db: Session = Depends(get_db)):
    """
    Lista todos los repositorios de un usuario.

    Args:
        user_id: ID del usuario
        db: Sesión de base de datos

    Returns:
        List[RepoResponse]: Lista de repos del usuario
    """
    try:
        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Obtener repos del usuario
        repos = db.query(Repo).filter(Repo.user_id == user_id).all()

        return [
            RepoResponse(
                id=str(repo.id),
                original_owner=repo.original_owner,
                original_repo_name=repo.original_repo_name,
                original_repo_url=repo.original_repo_url,
                forked_repo_name=repo.forked_repo_name,
                forked_repo_url=repo.forked_repo_url or "",
                branch=repo.branch,
                technology=repo.technology,
                cron_schedule=repo.cron_schedule,
                created_at=str(repo.created_at)
            )
            for repo in repos
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing repos: {str(e)}")


@router.delete("/repos/{repo_id}")
def delete_repo(repo_id: str, user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    Elimina un repositorio de la BD.

    NOTA: No elimina el fork de GitHub, solo el registro en la BD.

    Args:
        repo_id: ID del repo
        user_id: ID del usuario (para verificar ownership)
        db: Sesión de base de datos

    Returns:
        dict: Mensaje de confirmación
    """
    try:
        # Obtener repo
        repo = db.query(Repo).filter(Repo.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Verificar que el repo pertenece al usuario
        if str(repo.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this repository")

        # Eliminar (cascade eliminará deployments y settings)
        db.delete(repo)
        db.commit()

        return {
            "message": "Repository deleted successfully",
            "note": "The GitHub fork still exists and must be deleted manually if needed"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting repo: {str(e)}")
