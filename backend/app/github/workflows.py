"""
Generación de GitHub Actions workflows.

Este módulo genera archivos YAML de workflows según la tecnología del proyecto.
Los templates son básicos y el usuario los completará después.
"""

from typing import Dict
from app.github.api import commit_file


def generate_workflow_yaml(technology: str, env_vars: dict, build_args: dict,
                          docker_repo: str, container_name: str, port: int,
                          branch: str) -> str:
    """
    Genera el contenido del workflow YAML según la tecnología.

    Este workflow se hace commit al repo del usuario en .github/workflows/deploy.yml
    Cuando hay un push al branch especificado, el workflow corre automáticamente.

    Args:
        technology: 'react-vite', 'fastapi', o 'nestjs'
        env_vars: diccionario de variables de entorno {KEY: value}
        build_args: diccionario de build arguments {ARG: value}
        docker_repo: repositorio de Docker Hub (ej: username/repo)
        container_name: nombre del container (ej: username-reponame)
        port: puerto asignado para el container
        branch: branch a monitorear

    Returns:
        str: Contenido YAML del workflow

    Raises:
        ValueError: Si la tecnología no es soportada

    Ejemplo:
        yaml = generate_workflow_yaml(
            "react-vite",
            {"NODE_ENV": "production"},
            {"NODE_VERSION": "18"},
            "username/deployments",
            "username-repo",
            3000,
            "main"
        )
    """
    # Convertir env_vars a formato -e KEY=value para docker run
    env_flags = " ".join([f'-e {k}="{v}"' for k, v in env_vars.items()])

    # Convertir build_args a formato --build-arg KEY=value para docker build
    build_arg_flags = " ".join([f'--build-arg {k}="{v}"' for k, v in build_args.items()])

    # Tag de la imagen Docker
    image_tag = f"{docker_repo}:{container_name}"

    # NOTA: Estos son templates BÁSICOS
    # El usuario proporcionará los templates completos después
    # Estos templates solo crean la estructura para que el workflow pueda correr

    if technology == "react-vite":
        return f"""name: Deploy React+Vite App

on:
  push:
    branches: [{branch}]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{{{ secrets.DOCKER_HUB_USERNAME }}}}
          password: ${{{{ secrets.DOCKER_HUB_PASSWORD }}}}

      - name: Build Docker image
        run: |
          docker build {build_arg_flags} -t {image_tag} .

      - name: Push Docker image
        run: |
          docker push {image_tag}

      - name: Deploy to server
        run: |
          echo "Container: {container_name}"
          echo "Port: {port}"
          echo "Env vars: {env_flags}"
          # El usuario completará los pasos de deployment aquí
          # Por ahora solo imprime la configuración
"""

    elif technology == "fastapi":
        return f"""name: Deploy FastAPI App

on:
  push:
    branches: [{branch}]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{{{ secrets.DOCKER_HUB_USERNAME }}}}
          password: ${{{{ secrets.DOCKER_HUB_PASSWORD }}}}

      - name: Build Docker image
        run: |
          docker build {build_arg_flags} -t {image_tag} .

      - name: Push Docker image
        run: |
          docker push {image_tag}

      - name: Deploy to server
        run: |
          echo "Container: {container_name}"
          echo "Port: {port}"
          echo "Env vars: {env_flags}"
          # El usuario completará los pasos de deployment aquí
"""

    elif technology == "nestjs":
        return f"""name: Deploy NestJS App

on:
  push:
    branches: [{branch}]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{{{ secrets.DOCKER_HUB_USERNAME }}}}
          password: ${{{{ secrets.DOCKER_HUB_PASSWORD }}}}

      - name: Build Docker image
        run: |
          docker build {build_arg_flags} -t {image_tag} .

      - name: Push Docker image
        run: |
          docker push {image_tag}

      - name: Deploy to server
        run: |
          echo "Container: {container_name}"
          echo "Port: {port}"
          echo "Env vars: {env_flags}"
          # El usuario completará los pasos de deployment aquí
"""

    else:
        raise ValueError(f"Unsupported technology: {technology}")


def create_workflow_in_repo(token: str, owner: str, repo: str, branch: str,
                           workflow_content: str) -> Dict:
    """
    Hace commit del workflow al repositorio del usuario.

    Crea el archivo .github/workflows/deploy.yml en el repo.
    Si el archivo ya existe, lo actualiza.

    Args:
        token: Access token de GitHub
        owner: Owner del repo
        repo: Nombre del repo
        branch: Branch donde hacer el commit
        workflow_content: Contenido del archivo YAML

    Returns:
        Dict: Datos del commit

    Ejemplo:
        yaml = generate_workflow_yaml(...)
        commit = create_workflow_in_repo(
            token,
            "username",
            "mi-repo",
            "main",
            yaml
        )
    """
    # Ruta del workflow en el repo
    workflow_path = ".github/workflows/deploy.yml"

    # Mensaje del commit
    commit_message = "Add automated deployment workflow"

    # Hacer commit usando la función de api.py
    return commit_file(
        token=token,
        owner=owner,
        repo=repo,
        path=workflow_path,
        content=workflow_content,
        message=commit_message,
        branch=branch
    )
