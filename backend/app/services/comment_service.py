from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants import UserRole
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate
from app.services.ticket_service import get_ticket_for_user


def list_comments_for_user(
    db: Session,
    ticket_id: int,
    current_user: User,
) -> list[Comment]:
    # Reuse ticket visibility rules first
    get_ticket_for_user(db, ticket_id, current_user)

    stmt = select(Comment).where(Comment.ticket_id == ticket_id)

    if current_user.role == UserRole.EMPLOYEE.value:
        stmt = stmt.where(Comment.is_internal.is_(False))

    stmt = stmt.order_by(Comment.created_at.asc())

    return list(db.execute(stmt).scalars().all())


def add_comment(
    db: Session,
    ticket_id: int,
    payload: CommentCreate,
    current_user: User,
) -> Comment:
    # Must be allowed to access the ticket first
    get_ticket_for_user(db, ticket_id, current_user)

    body = payload.body.strip()
    if not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment body cannot be empty",
        )

    if payload.is_internal and current_user.role == UserRole.EMPLOYEE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employees cannot create internal comments",
        )

    comment = Comment(
        ticket_id=ticket_id,
        author_user_id=current_user.id,
        body=body,
        is_internal=payload.is_internal,
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment
