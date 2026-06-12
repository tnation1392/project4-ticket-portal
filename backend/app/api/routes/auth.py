from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        user=UserRead.model_validate(user),
    )

@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_user)):
    return current_user