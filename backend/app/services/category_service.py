from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(db: Session, include_inactive: bool = False) -> list[Category]:
    stmt = select(Category)

    if not include_inactive:
        stmt = stmt.where(Category.is_active.is_(True))

    stmt = stmt.order_by(Category.name.asc())

    return list(db.execute(stmt).scalars().all())


def create_category(db: Session, payload: CategoryCreate) -> Category:
    category = Category(
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        is_active=True,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category_by_id(db: Session, category_id: int) -> Category | None:
    return db.get(Category, category_id)


def update_category(db: Session, category: Category, payload: CategoryUpdate) -> Category:
    if payload.name is not None:
        category.name = payload.name.strip()

    if payload.description is not None:
        category.description = payload.description.strip() if payload.description else None

