import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.constants import UserRole
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User

TEST_DATABASE_URL = "sqlite:///./test_ticket_portal.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def seeded_users(db_session):
    users = {
        "employee": User(
            email="employee1@example.com",
            password_hash=get_password_hash("password123"),
            full_name="Employee One",
            role=UserRole.EMPLOYEE.value,
            is_active=True,
        ),
        "agent": User(
            email="agent1@example.com",
            password_hash=get_password_hash("password123"),
            full_name="Agent One",
            role=UserRole.AGENT.value,
            is_active=True,
        ),
        "admin": User(
            email="admin1@example.com",
            password_hash=get_password_hash("password123"),
            full_name="Admin One",
            role=UserRole.ADMIN.value,
            is_active=True,
        ),
    }

    db_session.add_all(users.values())
    db_session.commit()

    for user in users.values():
        db_session.refresh(user)

    return users


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()
