"""
Rutas para configuración de secrets y variables.

Endpoints:
- POST /repos/{repo_id}/settings - Guarda env_vars y build_args
- GET /repos/{repo_id}/settings - Obtiene settings
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict

from app.core.database import get_db
from app.models import Repo, Settings

router = APIRouter()


class SettingsRequest(BaseModel):
    """Request de POST /repos/{repo_id}/settings"""
    env_vars: Dict[str, str] = {}
    build_args: Dict[str, str] = {}


class SettingsResponse(BaseModel):
    """Response de GET /repos/{repo_id}/settings"""
    env_vars: Dict[str, str]
    build_args: Dict[str, str]


@router.post("/repos/{repo_id}/settings")
def save_settings(
    repo_id: str = Path(...),
    request: SettingsRequest = ...,
    db: Session = Depends(get_db)
):
    """
    Guarda la configuración de env_vars y build_args de un repo.

    Args:
        repo_id: ID del repositorio
        request: Env vars y build args
        db: Sesión de base de datos

    Returns:
        dict: Settings guardados
    """
    try:
        # Buscar repo
        repo = db.query(Repo).filter(Repo.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Buscar settings (o crear si no existen)
        settings = db.query(Settings).filter(Settings.repo_id == repo_id).first()

        if not settings:
            # Crear settings
            settings = Settings(
                repo_id=repo_id,
                env_vars=request.env_vars,
                build_args=request.build_args
            )
            db.add(settings)
        else:
            # Actualizar settings
            settings.env_vars = request.env_vars
            settings.build_args = request.build_args

        db.commit()
        db.refresh(settings)

        return {
            "repo_id": str(settings.repo_id),
            "env_vars": settings.env_vars,
            "build_args": settings.build_args
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving settings: {str(e)}")


@router.get("/repos/{repo_id}/settings", response_model=SettingsResponse)
def get_settings(repo_id: str = Path(...), db: Session = Depends(get_db)):
    """
    Obtiene la configuración de un repo.

    Args:
        repo_id: ID del repositorio
        db: Sesión de base de datos

    Returns:
        SettingsResponse: Env vars y build args
    """
    try:
        # Buscar repo
        repo = db.query(Repo).filter(Repo.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Buscar settings
        settings = db.query(Settings).filter(Settings.repo_id == repo_id).first()

        if not settings:
            # Retornar settings vacíos si no existen
            return SettingsResponse(env_vars={}, build_args={})

        return SettingsResponse(
            env_vars=settings.env_vars or {},
            build_args=settings.build_args or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting settings: {str(e)}")
