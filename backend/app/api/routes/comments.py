from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead
from app.services.comment_service import add_comment, list_comments_for_user

router = APIRouter(prefix="/tickets/{ticket_id}/comments", tags=["comments"])


@router.get("", response_model=list[CommentRead])
def get_comments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_comments_for_user(db, ticket_id, current_user)


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    ticket_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return add_comment(db, ticket_id, payload, current_user)
