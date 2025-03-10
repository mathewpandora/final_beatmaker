from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, UTC
from sqlalchemy.future import select
from app.db.models import GenrePrompt, User, Beat
from app.db.schemas.beat_schemas import BaseGenre
from app.core.redis_client import redis_client
import json
from app.services.beat_service.title_generator import generate_unique_id

TTL = 1800


async def get_genre_prompt(genre_data: BaseGenre, db: AsyncSession):
    """Получение объекта жанра из базы данных"""
    db_prompt_object = await db.execute(select(GenrePrompt).where(GenrePrompt.genre == genre_data.genre))
    db_prompt = db_prompt_object.scalars().first()

    if not db_prompt:
        raise HTTPException(status_code=404, detail="Выбранного жанра пока не существует")
    return db_prompt


async def get_user_by_email(user_email: str, db: AsyncSession):
    """Получение объекта пользователя из базы данных"""
    db_user_object = await db.execute(select(User).where(User.email == user_email))
    db_user = db_user_object.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return db_user


def create_beat_data(db_user, db_genre):
    """Создание данных для Redis"""
    # Объект с информацией о бите для с пользователем
    beat_with_user = {
        "user_id": db_user.id,
        "genre": db_genre.genre,
        "status": "in_progress",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    return beat_with_user


def store_in_redis(genre: str, beat_with_user):
    """Запись данных в Redis с TTL"""
    redis_client.set(f"genreBeat:{genre}:with_user:{generate_unique_id()}", json.dumps(beat_with_user), ex=TTL)

async def update_user_generations(user_email: str, db: AsyncSession):
    """
    Проверяет наличие доступных генераций у пользователя и обновляет их.
    Если генерации есть, вычитается 1 из available_generations и прибавляется к total_generations.
    """
    # Получаем пользователя из базы данных
    result = await db.execute(select(User).filter(User.email == user_email))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email {user_email} not found.")
    # Проверяем наличие доступных генераций
    if user.available_generations > 0:
        # Уменьшаем доступные генерации и увеличиваем общие
        user.available_generations -= 1
        user.total_generations += 1
        # Сохраняем изменения в базе данных
        db.add(user)
        await db.commit()
    else:
        raise HTTPException(status_code=400, detail="No available generations left for the user.")

    return user


async def get_existing_beat(db: AsyncSession, genre: str, user_email: str) -> Beat:
    result = await db.execute(select(Beat).where(Beat.genre == genre, Beat.user_id == None))
    beat = result.scalars().first()
    if beat:
        db_user = await get_user_by_email(user_email, db)
        beat.user_id = db_user.id
        beat.created_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(beat)
    return beat




