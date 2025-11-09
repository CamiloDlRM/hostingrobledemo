"""
Autenticación con GitHub.

Este módulo maneja el flujo OAuth de GitHub App para obtener tokens de usuario.
"""

import requests
from app.core.config import settings


def generate_authorization_url() -> str:
    """
    Genera la URL para que el usuario autorice la GitHub App.

    Esta es la URL a la que se redirige al usuario cuando clickea "Conectar con GitHub".
    El usuario autorizará la app y será redirigido de vuelta con un código.

    Returns:
        str: URL de autorización de GitHub

    Ejemplo:
        url = generate_authorization_url()
        # Redirigir al usuario a 'url'
        # Usuario autoriza la app
        # GitHub redirige a: http://tu-app.com/auth/callback?code=ABC123
    """
    # URL base de autorización de GitHub
    base_url = "https://github.com/login/oauth/authorize"

    # Parámetros del OAuth flow
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        # Scopes que necesitamos:
        # - repo: acceso completo a repos privados y públicos
        # - user: acceso al perfil del usuario
        # - workflow: permiso para crear/modificar workflows
        "scope": "repo user workflow",
        # URL a donde GitHub redirige después de autorizar
        "redirect_uri": f"{settings.BACKEND_URL}/auth/github/callback"
    }

    # Construir URL con parámetros
    param_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{base_url}?{param_string}"


def exchange_code_for_token(code: str) -> dict:
    """
    Intercambia el código de autorización por un access token.

    Después de que el usuario autoriza la app, GitHub redirige con un código.
    Este código se intercambia por un access token que usamos para llamar a la API.

    Args:
        code: Código de autorización de GitHub (del query param)

    Returns:
        dict: Datos del token con keys:
            - access_token: Token para usar en GitHub API
            - token_type: Tipo de token (usualmente "bearer")
            - scope: Scopes autorizados

    Raises:
        Exception: Si GitHub retorna error

    Ejemplo:
        code = request.query_params.get("code")
        token_data = exchange_code_for_token(code)
        access_token = token_data["access_token"]
        # Guardar access_token en BD (encriptado)
    """
    # Endpoint de GitHub para intercambiar código por token
    url = "https://github.com/login/oauth/access_token"

    # Datos del request
    data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": f"{settings.BACKEND_URL}/auth/github/callback"
    }

    # Headers para pedir respuesta en JSON
    headers = {
        "Accept": "application/json"
    }

    # Hacer request a GitHub
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()  # Lanzar excepción si hay error

    # Retornar datos del token
    return response.json()


def get_user_info(access_token: str) -> dict:
    """
    Obtiene información del usuario autenticado.

    Usa el access token para obtener datos del usuario desde GitHub API.

    Args:
        access_token: Token de acceso de GitHub

    Returns:
        dict: Datos del usuario con keys:
            - id: ID del usuario en GitHub
            - login: Username
            - email: Email del usuario
            - avatar_url: URL de la foto de perfil

    Ejemplo:
        token = "ghp_abc123..."
        user_info = get_user_info(token)
        username = user_info["login"]
    """
    url = "https://api.github.com/user"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()


def get_installation_token(installation_id: str) -> str:
    """
    Obtiene un installation token para GitHub App.

    NOTA: Esta función es para autenticación como GitHub App (no como usuario).
    Solo necesaria si usas instalaciones de GitHub App.
    Para OAuth de usuario, usar exchange_code_for_token.

    Args:
        installation_id: ID de la instalación de la GitHub App

    Returns:
        str: Installation token

    Ejemplo:
        token = get_installation_token("12345")
    """
    # Esta función requiere generar un JWT con la private key
    # y hacer un request a GitHub API
    # Por simplicidad, dejar para después si es necesario
    raise NotImplementedError("Installation tokens no implementados aún")
