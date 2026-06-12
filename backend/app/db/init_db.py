from sqlalchemy import select

import app.models  # noqa: F401
from app.constants import UserRole
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import User


SEED_USERS = [
    {
        "email": "employee1@example.com",
        "password": "password123",
        "full_name": "Employee One",
        "role": UserRole.EMPLOYEE.value,
    },
    {
        "email": "agent1@example.com",
        "password": "password123",
        "full_name": "Agent One",
        "role": UserRole.AGENT.value,
    },
    {
        "email": "agent2@example.com",
        "password": "password123",
        "full_name": "Agent Two",
        "role": UserRole.AGENT.value,
    },
    {
        "email": "admin1@example.com",
        "password": "password123",
        "full_name": "Admin One",
        "role": UserRole.ADMIN.value,
    },
]


def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for user_data in SEED_USERS:
            stmt = select(User).where(User.email == user_data["email"])
            existing_user = db.execute(stmt).scalar_one_or_none()

            if existing_user:
                continue

            user = User(
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
            )
            db.add(user)

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()