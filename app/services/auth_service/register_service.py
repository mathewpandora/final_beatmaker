from sqlalchemy.ext.asyncio import AsyncSession
from app.db.schemas.auth_schemas import UserBase
from app.db.models import User
from sqlalchemy.future import select
from app.services.auth_service.password_service import get_password_hash


async def is_email_registered(db: AsyncSession, email: str) -> bool:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first() is not None


async def create_user(db: AsyncSession, user: UserBase) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password=hashed_password,
        total_generations=0,
        available_generations=0,
        is_verified=False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user