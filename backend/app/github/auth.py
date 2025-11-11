"""
Funciones para trabajar con la organización de GitHub.

Este módulo maneja operaciones relacionadas con la organización donde se harán los forks.
"""

import requests
from app.core.config import settings


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    """
    Parsea una URL de GitHub para extraer owner y repo.

    Args:
        repo_url: URL del repositorio (ej: https://github.com/owner/repo)

    Returns:
        tuple[str, str]: (owner, repo)

    Raises:
        ValueError: Si la URL no es válida

    Ejemplo:
        owner, repo = parse_repo_url("https://github.com/facebook/react")
        # owner = "facebook", repo = "react"
    """
    # Limpiar URL
    repo_url = repo_url.strip().rstrip("/")

    # Soportar diferentes formatos
    if repo_url.startswith("https://github.com/"):
        parts = repo_url.replace("https://github.com/", "").split("/")
    elif repo_url.startswith("http://github.com/"):
        parts = repo_url.replace("http://github.com/", "").split("/")
    elif repo_url.startswith("github.com/"):
        parts = repo_url.replace("github.com/", "").split("/")
    else:
        # Asumir formato owner/repo
        parts = repo_url.split("/")

    if len(parts) < 2:
        raise ValueError("URL de repositorio inválida. Formato esperado: https://github.com/owner/repo")

    owner = parts[0]
    repo = parts[1].replace(".git", "")  # Remover .git si existe

    return owner, repo


def fork_repository(owner: str, repo: str) -> dict:
    """
    Hace fork de un repositorio a la organización configurada.

    Args:
        owner: Owner del repositorio original
        repo: Nombre del repositorio

    Returns:
        dict: Datos del fork creado con keys:
            - id: ID del fork
            - name: Nombre del repo
            - full_name: Nombre completo (org/repo)
            - html_url: URL del fork
            - clone_url: URL para clonar
            - default_branch: Branch por defecto

    Raises:
        Exception: Si GitHub retorna error

    Ejemplo:
        fork = fork_repository("facebook", "react")
        fork_url = fork["html_url"]
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/forks"

    headers = {
        "Authorization": f"Bearer {settings.GITHUB_ORG_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Hacer fork a la organización
    data = {
        "organization": settings.GITHUB_ORG_NAME
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()


def check_repo_exists(owner: str, repo: str) -> bool:
    """
    Verifica si un repositorio existe y es accesible.

    Args:
        owner: Owner del repo
        repo: Nombre del repo

    Returns:
        bool: True si existe, False si no

    Ejemplo:
        if check_repo_exists("facebook", "react"):
            print("El repo existe")
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except:
        return False


def get_org_repo_info(repo: str) -> dict:
    """
    Obtiene información de un repositorio en la organización.

    Args:
        repo: Nombre del repo en la organización

    Returns:
        dict: Datos del repo

    Ejemplo:
        info = get_org_repo_info("react")
    """
    url = f"https://api.github.com/repos/{settings.GITHUB_ORG_NAME}/{repo}"

    headers = {
        "Authorization": f"Bearer {settings.GITHUB_ORG_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()
