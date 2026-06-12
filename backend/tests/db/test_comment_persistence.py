from app.constants import UserRole
from app.core.security import get_password_hash
from app.models.category import Category
from app.models.comment import Comment
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.comment import CommentCreate
from app.services.comment_service import add_comment


def create_active_category(db_session, name: str = "Hardware") -> Category:
    category = Category(
        name=name,
        description=f"{name} issues",
        is_active=True,
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def create_user(
    db_session,
    email: str,
    full_name: str,
    role: str,
) -> User:
    user = User(
        email=email,
        password_hash=get_password_hash("password123"),
        full_name=full_name,
        role=role,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_ticket_for_user(
    db_session,
    category: Category,
    created_by_user_id: int,
    title: str = "Test Ticket",
) -> Ticket:
    ticket = Ticket(
        title=title,
        description="Ticket description",
        category_id=category.id,
        priority="medium",
        status="new",
        created_by_user_id=created_by_user_id,
        assigned_to_user_id=None,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(ticket)
    return ticket


def test_public_comment_persists_as_non_internal(db_session, seeded_users):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Public Comment Ticket",
    )

    created_comment = add_comment(
        db=db_session,
        ticket_id=ticket.id,
        payload=CommentCreate(
            body="This is a public update.",
            is_internal=False,
        ),
        current_user=seeded_users["employee"],
    )

    persisted_comment = db_session.get(Comment, created_comment.id)

    assert persisted_comment is not None
    assert persisted_comment.ticket_id == ticket.id
    assert persisted_comment.author_user_id == seeded_users["employee"].id
    assert persisted_comment.body == "This is a public update."
    assert persisted_comment.is_internal is False
    assert persisted_comment.created_at is not None


def test_internal_comment_persists_as_internal(db_session, seeded_users):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Internal Comment Ticket",
    )

    created_comment = add_comment(
        db=db_session,
        ticket_id=ticket.id,
        payload=CommentCreate(
            body="Internal troubleshooting note.",
            is_internal=True,
        ),
        current_user=seeded_users["agent"],
    )

    persisted_comment = db_session.get(Comment, created_comment.id)

    assert persisted_comment is not None
    assert persisted_comment.ticket_id == ticket.id
    assert persisted_comment.author_user_id == seeded_users["agent"].id
    assert persisted_comment.body == "Internal troubleshooting note."
    assert persisted_comment.is_internal is True
    assert persisted_comment.created_at is not None


def test_comment_body_is_trimmed_before_persisting(db_session, seeded_users):
    category = create_active_category(db_session)
    ticket = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Trimmed Comment Ticket",
    )

    created_comment = add_comment(
        db=db_session,
        ticket_id=ticket.id,
        payload=CommentCreate(
            body="   Extra detail from employee.   ",
            is_internal=False,
        ),
        current_user=seeded_users["employee"],
    )

    persisted_comment = db_session.get(Comment, created_comment.id)

    assert persisted_comment is not None
    assert persisted_comment.body == "Extra detail from employee."
    assert persisted_comment.is_internal is False


def test_internal_comment_is_linked_to_correct_ticket_and_author(db_session, seeded_users):
    category = create_active_category(db_session)
    ticket_one = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Ticket One",
    )
    ticket_two = create_ticket_for_user(
        db_session,
        category=category,
        created_by_user_id=seeded_users["employee"].id,
        title="Ticket Two",
    )

    created_comment = add_comment(
        db=db_session,
        ticket_id=ticket_two.id,
        payload=CommentCreate(
            body="Work note for ticket two.",
            is_internal=True,
        ),
        current_user=seeded_users["admin"],
    )

    persisted_comment = db_session.get(Comment, created_comment.id)

    assert persisted_comment is not None
    assert persisted_comment.ticket_id == ticket_two.id
    assert persisted_comment.ticket_id != ticket_one.id
    assert persisted_comment.author_user_id == seeded_users["admin"].id
    assert persisted_comment.is_internal is True
