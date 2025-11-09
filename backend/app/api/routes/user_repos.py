"""
Rutas para autenticación y gestión de repositorios.

Endpoints:
- POST /auth/github - Inicia OAuth flow
- GET /auth/github/callback - Callback de OAuth
- GET /repos - Lista repos del usuario
- POST /repos - Guarda un repo
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import re

from app.core.database import get_db
from app.core.security import encrypt_token
from app.github import auth, api
from app.models import User, Repo, TechnologyEnum, Settings

router = APIRouter()


class AuthUrlResponse(BaseModel):
    """Response de POST /auth/github"""
    authorization_url: str


class GitHubUser(BaseModel):
    """Datos del usuario autenticado"""
    id: str
    username: str
    email: str
    access_token: str


class RepoResponse(BaseModel):
    """Response de GET /repos"""
    id: str
    name: str
    full_name: str
    url: str
    private: bool


class CreateRepoRequest(BaseModel):
    """Request de POST /repos"""
    repo_url: str
    branch: str = "main"
    technology: TechnologyEnum


@router.post("/auth/github", response_model=AuthUrlResponse)
def start_github_auth():
    """
    Inicia el flujo de OAuth con GitHub.

    El frontend redirige al usuario a esta URL.
    El usuario autoriza la app y GitHub redirige de vuelta.

    Returns:
        AuthUrlResponse: URL de autorización de GitHub
    """
    try:
        url = auth.generate_authorization_url()
        return AuthUrlResponse(authorization_url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating auth URL: {str(e)}")


@router.get("/auth/github/callback", response_model=GitHubUser)
def github_callback(code: str = Query(...), db: Session = Depends(get_db)):
    """
    Callback de OAuth. GitHub redirige aquí con un código.

    Intercambia el código por un token, obtiene info del usuario,
    y guarda el usuario en BD (o actualiza si ya existe).

    Args:
        code: Código de autorización de GitHub
        db: Sesión de base de datos

    Returns:
        GitHubUser: Datos del usuario autenticado
    """
    try:
        # Intercambiar código por token
        token_data = auth.exchange_code_for_token(code)
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")

        # Obtener info del usuario
        user_info = auth.get_user_info(access_token)

        github_user_id = str(user_info.get("id"))
        username = user_info.get("login")
        email = user_info.get("email", "")

        # Buscar usuario en BD
        user = db.query(User).filter(User.github_user_id == github_user_id).first()

        if user:
            # Usuario existe, actualizar token
            user.github_token = encrypt_token(access_token)
            user.username = username
            user.email = email
        else:
            # Usuario nuevo, crear
            user = User(
                github_user_id=github_user_id,
                username=username,
                email=email,
                github_token=encrypt_token(access_token)
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        return GitHubUser(
            id=str(user.id),
            username=user.username,
            email=user.email or "",
            access_token=access_token  # Retornar token para que frontend lo guarde
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error in OAuth callback: {str(e)}")


@router.get("/repos", response_model=List[RepoResponse])
def list_repos(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    Lista los repositorios de GitHub del usuario.

    Args:
        user_id: ID del usuario autenticado
        db: Sesión de base de datos

    Returns:
        List[RepoResponse]: Lista de repos del usuario
    """
    try:
        # Obtener usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Desencriptar token
        from app.core.security import decrypt_token
        token = decrypt_token(user.github_token)

        # Listar repos de GitHub
        repos = api.list_user_repos(token)

        # Convertir a response
        return [
            RepoResponse(
                id=str(r.get("id")),
                name=r.get("name", ""),
                full_name=r.get("full_name", ""),
                url=r.get("html_url", ""),
                private=r.get("private", False)
            )
            for r in repos
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing repos: {str(e)}")


@router.post("/repos")
def create_repo(request: CreateRepoRequest, user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    Guarda un repositorio en la BD.

    Extrae owner y repo_name de la URL y crea el registro.

    Args:
        request: Datos del repo
        user_id: ID del usuario
        db: Sesión de base de datos

    Returns:
        dict: Datos del repo creado
    """
    try:
        # Obtener usuario
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Validar URL de GitHub
        # Formato: https://github.com/owner/repo
        url_pattern = r"https?://github\.com/([^/]+)/([^/]+)"
        match = re.match(url_pattern, request.repo_url.strip())

        if not match:
            raise HTTPException(
                status_code=400,
                detail="Invalid GitHub URL. Format: https://github.com/owner/repo"
            )

        repo_owner = match.group(1)
        repo_name = match.group(2)

        # Validar branch no vacío
        if not request.branch or not request.branch.strip():
            raise HTTPException(status_code=400, detail="Branch cannot be empty")

        # Verificar que el repo no exista ya
        existing = db.query(Repo).filter(
            Repo.user_id == user.id,
            Repo.repo_owner == repo_owner,
            Repo.repo_name == repo_name
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Repository already exists")

        # Crear repo
        repo = Repo(
            user_id=user.id,
            repo_owner=repo_owner,
            repo_name=repo_name,
            repo_url=request.repo_url.strip(),
            branch=request.branch.strip(),
            technology=request.technology
        )
        db.add(repo)
        db.commit()
        db.refresh(repo)

        # Crear settings vacíos
        settings = Settings(
            repo_id=repo.id,
            env_vars={},
            build_args={}
        )
        db.add(settings)
        db.commit()

        return {
            "id": str(repo.id),
            "repo_owner": repo.repo_owner,
            "repo_name": repo.repo_name,
            "repo_url": repo.repo_url,
            "branch": repo.branch,
            "technology": repo.technology
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating repo: {str(e)}")
