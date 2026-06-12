from fastapi import HTTPException, status

from app.constants import UserRole
from app.models.user import User


def is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN.value


def require_admin(user: User) -> None:
    if not is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )