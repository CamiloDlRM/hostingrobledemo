"""
Rutas para gestión de deployments y webhooks.

Endpoints:
- GET /repos/{repo_id}/deployments - Lista deployments de un repo
- GET /deployments/{deployment_id} - Detalle de un deployment
- GET /deployments/{deployment_id}/logs - Logs del workflow
- POST /webhooks/github - Recibe webhooks de GitHub
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.core.config import settings as app_settings
from app.core.security import decrypt_token
from app.models import Repo, Deployment
from app.github import webhooks, logs as github_logs

router = APIRouter()


class DeploymentResponse(BaseModel):
    """Response de GET /deployments/{id}"""
    id: str
    repo_id: str
    commit_sha: Optional[str]
    status: str
    docker_image: Optional[str]
    container_name: Optional[str]
    port: Optional[int]
    domain: Optional[str]
    workflow_run_url: Optional[str]
    error_message: Optional[str]
    started_at: str
    finished_at: Optional[str]


class DeploymentListItem(BaseModel):
    """Item de lista de deployments"""
    id: str
    commit_sha: Optional[str]
    status: str
    domain: Optional[str]
    started_at: str
    finished_at: Optional[str]


@router.get("/repos/{repo_id}/deployments", response_model=List[DeploymentListItem])
def list_deployments(repo_id: str = Path(...), db: Session = Depends(get_db)):
    """
    Lista todos los deployments de un repositorio.

    Args:
        repo_id: ID del repositorio
        db: Sesión de base de datos

    Returns:
        List[DeploymentListItem]: Lista de deployments ordenados por fecha
    """
    try:
        # Verificar que el repo existe
        repo = db.query(Repo).filter(Repo.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Obtener deployments del repo
        deployments = db.query(Deployment).filter(
            Deployment.repo_id == repo_id
        ).order_by(Deployment.started_at.desc()).all()

        # Convertir a response
        return [
            DeploymentListItem(
                id=str(d.id),
                commit_sha=d.commit_sha,
                status=d.status,
                domain=d.domain,
                started_at=d.started_at.isoformat() if d.started_at else "",
                finished_at=d.finished_at.isoformat() if d.finished_at else None
            )
            for d in deployments
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing deployments: {str(e)}")


@router.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(deployment_id: str = Path(...), db: Session = Depends(get_db)):
    """
    Obtiene el detalle de un deployment.

    Este endpoint se llama con polling desde el frontend para actualizar el estado.

    Args:
        deployment_id: ID del deployment
        db: Sesión de base de datos

    Returns:
        DeploymentResponse: Datos completos del deployment
    """
    try:
        # Buscar deployment
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        return DeploymentResponse(
            id=str(deployment.id),
            repo_id=str(deployment.repo_id),
            commit_sha=deployment.commit_sha,
            status=deployment.status,
            docker_image=deployment.docker_image,
            container_name=deployment.container_name,
            port=deployment.port,
            domain=deployment.domain,
            workflow_run_url=deployment.workflow_run_url,
            error_message=deployment.error_message,
            started_at=deployment.started_at.isoformat() if deployment.started_at else "",
            finished_at=deployment.finished_at.isoformat() if deployment.finished_at else None
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting deployment: {str(e)}")


@router.get("/deployments/{deployment_id}/logs")
def get_deployment_logs(deployment_id: str = Path(...), db: Session = Depends(get_db)):
    """
    Obtiene los logs de un deployment desde GitHub Actions.

    Args:
        deployment_id: ID del deployment
        db: Sesión de base de datos

    Returns:
        dict: Logs del workflow
    """
    try:
        # Buscar deployment
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")

        # Verificar que hay un workflow run ID
        if not deployment.workflow_run_id:
            return {
                "logs": "No logs available yet. Workflow has not started.",
                "errors": []
            }

        # Obtener repo y token
        repo = deployment.repo
        user = repo.user
        token = decrypt_token(user.github_token)

        # Descargar logs de GitHub
        try:
            raw_logs = github_logs.get_workflow_run_logs(
                token=token,
                owner=repo.repo_owner,
                repo=repo.repo_name,
                run_id=deployment.workflow_run_id
            )

            # Parsear errores
            errors = github_logs.parse_logs_for_errors(raw_logs)

            return {
                "logs": raw_logs,
                "errors": errors,
                "workflow_url": deployment.workflow_run_url
            }

        except Exception as e:
            # Si falla la descarga de logs, retornar error
            return {
                "logs": f"Error downloading logs: {str(e)}",
                "errors": [],
                "workflow_url": deployment.workflow_run_url
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")


@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Recibe webhooks de GitHub.

    GitHub envía eventos cuando:
    - Hay un push al repo (evento: push)
    - Un workflow corre (evento: workflow_run)

    Este endpoint valida la firma HMAC y procesa el evento.

    Args:
        request: Request de FastAPI
        x_hub_signature_256: Firma HMAC del webhook
        x_github_event: Tipo de evento
        db: Sesión de base de datos

    Returns:
        dict: Confirmación del procesamiento
    """
    try:
        # Leer el body como bytes
        body = await request.body()

        # Validar firma HMAC
        if not webhooks.validate_webhook_signature(
            body,
            x_hub_signature_256 or "",
            app_settings.GITHUB_WEBHOOK_SECRET
        ):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        # Parsear payload JSON
        payload = json.loads(body.decode())

        # Procesar evento según tipo
        if x_github_event == "push":
            webhooks.process_push_event(payload, db)
            return {"message": "Push event processed"}

        elif x_github_event == "workflow_run":
            webhooks.process_workflow_run_event(payload, db)
            return {"message": "Workflow run event processed"}

        else:
            # Evento no soportado, ignorar
            return {"message": f"Event {x_github_event} ignored"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")
