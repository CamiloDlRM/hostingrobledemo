"""
Cliente para GitHub API.

Funciones para interactuar con repositorios de GitHub.
"""

import requests
import base64
from typing import List, Dict


def list_user_repos(token: str) -> List[Dict]:
    """
    Lista todos los repositorios del usuario autenticado.

    Args:
        token: Access token de GitHub

    Returns:
        List[Dict]: Lista de repos con datos:
            - id: ID del repo
            - name: Nombre del repo
            - full_name: Nombre completo (owner/repo)
            - html_url: URL del repo
            - private: Si es privado o no
            - default_branch: Branch por defecto

    Ejemplo:
        repos = list_user_repos(token)
        for repo in repos:
            print(repo["full_name"])
    """
    url = "https://api.github.com/user/repos"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Parámetros: repos propios y de organizaciones, ordenados por actualización
    params = {
        "affiliation": "owner,collaborator,organization_member",
        "sort": "updated",
        "per_page": 100  # Máximo por página
    }

    all_repos = []
    page = 1

    # Paginar resultados (GitHub limita a 100 por página)
    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        repos = response.json()
        if not repos:
            break  # No hay más repos

        all_repos.extend(repos)
        page += 1

        # Si hay menos de 100, ya no hay más páginas
        if len(repos) < 100:
            break

    return all_repos


def get_repo_info(token: str, owner: str, repo: str) -> Dict:
    """
    Obtiene información de un repositorio específico.

    Args:
        token: Access token de GitHub
        owner: Owner del repo (username u org)
        repo: Nombre del repo

    Returns:
        Dict: Datos del repo

    Ejemplo:
        info = get_repo_info(token, "facebook", "react")
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_repo_branches(token: str, owner: str, repo: str) -> List[Dict]:
    """
    Lista los branches de un repositorio.

    Args:
        token: Access token de GitHub
        owner: Owner del repo
        repo: Nombre del repo

    Returns:
        List[Dict]: Lista de branches con nombre y commit

    Ejemplo:
        branches = get_repo_branches(token, "facebook", "react")
        for branch in branches:
            print(branch["name"])
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/branches"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_file_content(token: str, owner: str, repo: str, path: str, branch: str = "main") -> str:
    """
    Obtiene el contenido de un archivo del repositorio.

    Args:
        token: Access token de GitHub
        owner: Owner del repo
        repo: Nombre del repo
        path: Ruta del archivo
        branch: Branch (por defecto "main")

    Returns:
        str: Contenido del archivo decodificado

    Ejemplo:
        content = get_file_content(token, "owner", "repo", "README.md")
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    params = {"ref": branch}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    # El contenido viene en base64
    content_b64 = data.get("content", "")
    content = base64.b64decode(content_b64).decode("utf-8")

    return content


def commit_file(token: str, owner: str, repo: str, path: str, content: str,
                message: str, branch: str = "main") -> Dict:
    """
    Crea o actualiza un archivo en el repositorio.

    Esta función se usa para hacer commit del workflow al repo del usuario.

    Args:
        token: Access token de GitHub
        owner: Owner del repo
        repo: Nombre del repo
        path: Ruta del archivo (ej: ".github/workflows/deploy.yml")
        content: Contenido del archivo
        message: Mensaje del commit
        branch: Branch donde hacer el commit

    Returns:
        Dict: Datos del commit creado

    Ejemplo:
        commit_file(
            token,
            "username",
            "mi-repo",
            ".github/workflows/deploy.yml",
            workflow_yaml,
            "Add deployment workflow"
        )
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Intentar obtener el archivo existente para actualizar
    sha = None
    try:
        existing = requests.get(url, headers=headers, params={"ref": branch})
        if existing.status_code == 200:
            sha = existing.json().get("sha")
    except:
        pass  # Archivo no existe, se creará

    # Codificar contenido en base64
    content_b64 = base64.b64encode(content.encode()).decode()

    # Datos del commit
    data = {
        "message": message,
        "content": content_b64,
        "branch": branch
    }

    # Si el archivo existe, incluir su SHA para actualizarlo
    if sha:
        data["sha"] = sha

    # Hacer el commit
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()

    return response.json()
