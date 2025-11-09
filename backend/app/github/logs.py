"""
Obtención de logs de GitHub Actions.

Este módulo descarga logs de workflow runs para mostrarlos al usuario.
"""

import requests
import zipfile
import io
from typing import List, Dict


def get_workflow_runs(token: str, owner: str, repo: str, per_page: int = 10) -> List[Dict]:
    """
    Lista las últimas ejecuciones de workflows del repositorio.

    Args:
        token: Access token de GitHub
        owner: Owner del repo
        repo: Nombre del repo
        per_page: Número de runs a obtener (default 10)

    Returns:
        List[Dict]: Lista de workflow runs con datos:
            - id: ID del run
            - status: Estado (queued, in_progress, completed)
            - conclusion: Resultado si completed (success, failure, cancelled)
            - created_at: Timestamp de creación
            - html_url: URL para ver en GitHub

    Ejemplo:
        runs = get_workflow_runs(token, "username", "repo")
        latest_run = runs[0]
        print(latest_run["status"])
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    params = {
        "per_page": per_page,
        "page": 1
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    return data.get("workflow_runs", [])


def get_workflow_run_logs(token: str, owner: str, repo: str, run_id: str) -> str:
    """
    Descarga los logs de un workflow run.

    GitHub retorna los logs como un archivo ZIP con logs de todos los jobs.
    Esta función descarga el ZIP, lo descomprime y extrae el texto.

    Args:
        token: Access token de GitHub
        owner: Owner del repo
        repo: Nombre del repo
        run_id: ID del workflow run

    Returns:
        str: Logs completos del workflow en texto plano

    Ejemplo:
        logs = get_workflow_run_logs(token, "username", "repo", "123456")
        print(logs)
    """
    # Endpoint para descargar logs
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Descargar el ZIP de logs
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status()

    # GitHub retorna un ZIP con logs de cada job
    # Extraer y concatenar todos los logs
    all_logs = []

    try:
        # Leer el ZIP desde bytes
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))

        # Iterar sobre cada archivo en el ZIP
        for file_name in zip_file.namelist():
            # Leer contenido del archivo
            with zip_file.open(file_name) as f:
                content = f.read().decode("utf-8", errors="ignore")
                all_logs.append(f"=== {file_name} ===\n{content}\n")

    except zipfile.BadZipFile:
        # Si no es un ZIP válido, retornar el contenido como texto
        all_logs.append(response.text)

    return "\n".join(all_logs)


def parse_logs_for_errors(logs: str) -> List[str]:
    """
    Parsea los logs buscando mensajes de error.

    Busca líneas que contengan palabras clave de error.
    Útil para mostrar al usuario qué salió mal.

    Args:
        logs: Logs completos en texto plano

    Returns:
        List[str]: Lista de líneas con errores

    Ejemplo:
        logs = get_workflow_run_logs(...)
        errors = parse_logs_for_errors(logs)
        for error in errors:
            print(error)
    """
    error_keywords = [
        "error:",
        "error ",
        "failed",
        "failure",
        "exit code 1",
        "exit status 1",
        "fatal:",
        "exception:",
        "traceback",
    ]

    error_lines = []

    # Buscar líneas con keywords de error (case insensitive)
    for line in logs.split("\n"):
        line_lower = line.lower()
        for keyword in error_keywords:
            if keyword in line_lower:
                error_lines.append(line.strip())
                break  # No agregar la misma línea múltiples veces

    return error_lines


def get_workflow_run_status(token: str, owner: str, repo: str, run_id: str) -> Dict:
    """
    Obtiene el estado actual de un workflow run.

    Args:
        token: Access token de GitHub
        owner: Owner del repo
        repo: Nombre del repo
        run_id: ID del workflow run

    Returns:
        Dict: Datos del run con status, conclusion, etc.

    Ejemplo:
        status = get_workflow_run_status(token, "username", "repo", "123456")
        if status["status"] == "completed":
            if status["conclusion"] == "success":
                print("Deployment exitoso!")
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()
