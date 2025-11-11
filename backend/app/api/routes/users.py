"""
Rutas para gestión de usuarios.

Endpoints:
- POST /users - Crea un usuario simple
- GET /users/{user_id} - Obtiene información de un usuario
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models import User

router = APIRouter()


class CreateUserRequest(BaseModel):
    """Request de POST /users"""
    username: str
    email: Optional[str] = None


class UserResponse(BaseModel):
    """Response de usuario"""
    id: str
    username: str
    email: Optional[str]
    created_at: str


@router.post("/users", response_model=UserResponse)
def create_user(request: CreateUserRequest, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en la plataforma.

    Args:
        request: Datos del usuario
        db: Sesión de base de datos

    Returns:
        UserResponse: Datos del usuario creado
    """
    try:
        # Verificar que el username no exista
        existing = db.query(User).filter(User.username == request.username).first()
        if existing:
            # Si existe, retornar el existente
            return UserResponse(
                id=str(existing.id),
                username=existing.username,
                email=existing.email,
                created_at=str(existing.created_at)
            )

        # Crear usuario
        user = User(
            username=request.username,
            email=request.email
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=str(user.created_at)
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene información de un usuario.

    Args:
        user_id: ID del usuario
        db: Sesión de base de datos

    Returns:
        UserResponse: Datos del usuario
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            created_at=str(user.created_at)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")
