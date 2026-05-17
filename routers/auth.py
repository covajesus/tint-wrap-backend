from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from classes.users import UserClass
from database import get_db
from dependencies.auth import get_current_user
from models.users import User
from schemas.auth import LoginRequest, LoginResponse, UserPublic
from utils.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = UserClass(db).authenticate(credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )

    token = create_access_token(subject=str(user.id))
    return LoginResponse(
        access_token=token,
        user=UserPublic.model_validate(user),
    )


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)
