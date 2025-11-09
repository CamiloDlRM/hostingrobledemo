"""
Procesamiento de webhooks de GitHub.

Este módulo procesa eventos de GitHub para actualizar el estado de deployments.
Los webhooks son CRÍTICOS para que la app sepa cuándo un deployment termina.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Deployment, DeploymentStatusEnum, Repo
from app.github.logs import parse_logs_for_errors, get_workflow_run_logs
from app.core.security import decrypt_token


def process_push_event(payload: dict, db: Session):
    """
    Procesa un evento de push al repositorio.

    Cuando hay un push al branch configurado, podemos:
    - Actualizar el último commit SHA en el deployment
    - Crear un nuevo deployment si es necesario

    Args:
        payload: Payload del webhook de GitHub
        db: Sesión de base de datos

    Ejemplo de payload:
        {
            "ref": "refs/heads/main",
            "after": "abc123...",  # SHA del nuevo commit
            "repository": {
                "full_name": "username/repo"
            }
        }
    """
    # Extraer datos del payload
    ref = payload.get("ref", "")  # Formato: refs/heads/branch-name
    commit_sha = payload.get("after", "")
    repo_full_name = payload.get("repository", {}).get("full_name", "")

    # Extraer branch del ref
    if ref.startswith("refs/heads/"):
        branch = ref.replace("refs/heads/", "")
    else:
        return  # No es un push a un branch

    # Extraer owner y repo name
    if "/" not in repo_full_name:
        return

    owner, repo_name = repo_full_name.split("/", 1)

    # Buscar el repo en nuestra BD
    repo = db.query(Repo).filter(
        Repo.repo_owner == owner,
        Repo.repo_name == repo_name,
        Repo.branch == branch
    ).first()

    if not repo:
        return  # Repo no está en nuestra BD

    # Buscar deployment pendiente o crear uno nuevo
    # (El deployment se crea en el endpoint POST /repos/{id}/deploy)
    # Aquí solo actualizamos el commit SHA si hay un deployment pendiente
    latest_deployment = db.query(Deployment).filter(
        Deployment.repo_id == repo.id,
        Deployment.status == DeploymentStatusEnum.PENDING
    ).order_by(Deployment.started_at.desc()).first()

    if latest_deployment:
        latest_deployment.commit_sha = commit_sha
        db.commit()


def process_workflow_run_event(payload: dict, db: Session):
    """
    Procesa un evento de workflow_run.

    Este es el evento MÁS IMPORTANTE. GitHub lo envía cuando:
    - Un workflow empieza a correr (status: queued, in_progress)
    - Un workflow termina (status: completed, conclusion: success/failure)

    Esta función actualiza el estado del deployment en nuestra BD.

    Args:
        payload: Payload del webhook de GitHub
        db: Sesión de base de datos

    Ejemplo de payload:
        {
            "action": "completed",  # o "requested", "in_progress"
            "workflow_run": {
                "id": 123456,
                "status": "completed",
                "conclusion": "success",  # o "failure"
                "html_url": "https://github.com/...",
                "head_sha": "abc123...",
                "repository": {
                    "full_name": "username/repo"
                }
            }
        }
    """
    # Extraer datos del workflow run
    workflow_run = payload.get("workflow_run", {})
    run_id = str(workflow_run.get("id", ""))
    status = workflow_run.get("status", "")  # queued, in_progress, completed
    conclusion = workflow_run.get("conclusion", "")  # success, failure, cancelled, skipped
    html_url = workflow_run.get("html_url", "")
    commit_sha = workflow_run.get("head_sha", "")

    # Datos del repo
    repo_data = workflow_run.get("repository", {})
    repo_full_name = repo_data.get("full_name", "")

    if "/" not in repo_full_name:
        return

    owner, repo_name = repo_full_name.split("/", 1)

    # Buscar el repo en nuestra BD
    repo = db.query(Repo).filter(
        Repo.repo_owner == owner,
        Repo.repo_name == repo_name
    ).first()

    if not repo:
        return  # Repo no está en nuestra BD

    # Buscar el deployment correspondiente
    # Buscar por commit SHA o por el más reciente
    deployment = db.query(Deployment).filter(
        Deployment.repo_id == repo.id,
        Deployment.commit_sha == commit_sha
    ).first()

    if not deployment:
        # Si no hay deployment con ese commit, usar el más reciente
        deployment = db.query(Deployment).filter(
            Deployment.repo_id == repo.id
        ).order_by(Deployment.started_at.desc()).first()

    if not deployment:
        return  # No hay deployment para actualizar

    # Guardar workflow run ID y URL
    deployment.workflow_run_id = run_id
    deployment.workflow_run_url = html_url

    # Actualizar estado según el status del workflow
    if status == "queued":
        deployment.status = DeploymentStatusEnum.PENDING

    elif status == "in_progress":
        deployment.status = DeploymentStatusEnum.BUILDING

    elif status == "completed":
        # El workflow terminó, ver si fue exitoso o falló
        if conclusion == "success":
            deployment.status = DeploymentStatusEnum.SUCCESS
            deployment.finished_at = datetime.utcnow()

        elif conclusion == "failure":
            deployment.status = DeploymentStatusEnum.FAILED
            deployment.finished_at = datetime.utcnow()

            # Intentar obtener los logs y extraer el error
            try:
                # Obtener token del usuario para descargar logs
                user = repo.user
                token = decrypt_token(user.github_token)

                # Descargar logs
                logs = get_workflow_run_logs(token, owner, repo_name, run_id)

                # Parsear errores
                errors = parse_logs_for_errors(logs)

                # Guardar errores en el deployment
                if errors:
                    # Tomar los primeros 10 errores
                    deployment.error_message = "\n".join(errors[:10])
                else:
                    deployment.error_message = "Deployment failed (check logs for details)"

            except Exception as e:
                deployment.error_message = f"Deployment failed: {str(e)}"

        else:
            # Otros conclusions: cancelled, skipped
            deployment.status = DeploymentStatusEnum.FAILED
            deployment.finished_at = datetime.utcnow()
            deployment.error_message = f"Workflow {conclusion}"

    # Guardar cambios en BD
    db.commit()


def validate_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Valida la firma de un webhook de GitHub.

    Wrapper alrededor de verify_github_webhook_signature de security.py

    Args:
        payload: Cuerpo del request en bytes
        signature: Header X-Hub-Signature-256
        secret: Secret configurado en GitHub App

    Returns:
        bool: True si válido, False si no
    """
    from app.core.security import verify_github_webhook_signature
    return verify_github_webhook_signature(payload, signature, secret)
