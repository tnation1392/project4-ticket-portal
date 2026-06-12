from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.permissions import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import (
    create_category,
    get_category_by_id,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_categories(db, include_inactive=False)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category_route(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return create_category(db, payload)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category_route(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    category = get_category_by_id(db, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return update_category(db, category, payload)