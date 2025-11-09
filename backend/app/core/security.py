"""
Funciones de seguridad.

Este módulo contiene funciones para:
1. Verificar firmas HMAC de webhooks de GitHub
2. Encriptar/desencriptar tokens de GitHub
"""

import hmac
import hashlib
from cryptography.fernet import Fernet
import base64
from .config import settings


def verify_github_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verifica la firma HMAC SHA-256 de un webhook de GitHub.

    GitHub envía webhooks con una firma en el header X-Hub-Signature-256.
    Esta función verifica que el webhook realmente viene de GitHub y no fue modificado.

    Args:
        payload: Cuerpo del request en bytes
        signature: Firma del header X-Hub-Signature-256 (formato: "sha256=...")
        secret: Secret configurado en la GitHub App

    Returns:
        bool: True si la firma es válida, False si no

    Ejemplo:
        signature = request.headers.get("X-Hub-Signature-256")
        payload = await request.body()
        if verify_github_webhook_signature(payload, signature, settings.GITHUB_WEBHOOK_SECRET):
            # Webhook válido
            process_webhook(payload)
    """
    if not signature:
        return False

    # GitHub envía la firma como "sha256=<hash>"
    # Extraer solo el hash
    if signature.startswith("sha256="):
        signature = signature[7:]

    # Calcular el HMAC del payload usando el secret
    mac = hmac.new(
        secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    )
    expected_signature = mac.hexdigest()

    # Comparar las firmas de forma segura (previene timing attacks)
    return hmac.compare_digest(expected_signature, signature)


def _get_encryption_key() -> bytes:
    """
    Genera una key de encriptación desde SECRET_KEY.

    Fernet requiere una key de 32 bytes en formato base64.
    Esta función convierte SECRET_KEY a ese formato.

    Returns:
        bytes: Key de encriptación en formato Fernet
    """
    # Tomar los primeros 32 bytes del SECRET_KEY
    key = settings.SECRET_KEY.encode()[:32]
    # Rellenar con ceros si es más corto
    key = key.ljust(32, b'0')
    # Convertir a base64 (formato que Fernet requiere)
    return base64.urlsafe_b64encode(key)


def encrypt_token(token: str) -> str:
    """
    Encripta un token de GitHub para guardarlo en BD.

    Los tokens de GitHub son sensibles y no deben guardarse en texto plano.
    Esta función los encripta usando Fernet (encriptación simétrica).

    Args:
        token: Token de GitHub en texto plano

    Returns:
        str: Token encriptado en formato string

    Ejemplo:
        encrypted = encrypt_token("ghp_abc123...")
        # Guardar 'encrypted' en la BD
    """
    key = _get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str) -> str:
    """
    Desencripta un token de GitHub.

    Convierte el token encriptado de vuelta a texto plano para usarlo.

    Args:
        encrypted_token: Token encriptado (obtenido de la BD)

    Returns:
        str: Token en texto plano listo para usar

    Ejemplo:
        encrypted = user.github_token  # Desde BD
        token = decrypt_token(encrypted)
        # Usar 'token' para llamar a GitHub API
    """
    key = _get_encryption_key()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_token.encode())
    return decrypted.decode()
