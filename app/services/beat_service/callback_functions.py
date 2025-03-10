import re
from app.services.websocket_service.websokcet_manager import ConnectionManager
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Beat, User, GenrePrompt
from app.core.redis_client import redis_client
import json
import logging

logger = logging.getLogger("app")


async def process_beat_audio_and_image(response_data, db):
    """Обработка аудио и изображения для каждого бита в данных ответа."""
    beat_objects = {0: {}, 1: {}}
    for index, beat in enumerate(response_data):
        if beat.status == "complete":
            if beat.audio_url and beat.audio_url.strip():
                if beat.image_url and beat.image_url.strip():
                    genre = await get_genre_by_prompt(beat.prompt, db)
                    beat_objects[index] = {
                        "title": beat.title,
                        "url": beat.audio_url,
                        "image_url": beat.image_url,
                        "genre": genre
                    }
                    logger.info(
                        f"Processed beat: {beat.title} ({beat.id}) with audio: {beat.audio_url} and image: {beat.image_url}")
                else:
                    logger.warning(f"Missing image for beat {beat.title}")
            else:
                logger.warning(f"Missing audio for beat {beat.title}")
    return beat_objects


def get_redis_data(genre):
    """Получение данных из Redis по ключам (по одному элементу) и их удаление."""
    key_without_user = f"beat:{genre}:without_user"
    key_with_user = f"beat:{genre}:with_user"

    # Получаем один первый элемент
    without_user_data = redis_client.lpop(key_without_user)  # Берём первый и удаляем
    with_user_data = redis_client.lpop(key_with_user)  # Берём первый и удаляем

    if not without_user_data or not with_user_data:
        logger.error(f"Missing Redis data for genre {genre}")
        raise HTTPException(status_code=404, detail="Data missing in Redis")

    # Декодируем JSON
    without_user_json = json.loads(without_user_data)
    with_user_json = json.loads(with_user_data)

    return without_user_json, with_user_json


async def check_if_beat_exists(db: AsyncSession, title: str):
    """Проверка, существует ли запись с таким же title и статусом 'complete'."""
    result = await db.execute(
        select(Beat).filter(Beat.title == title, Beat.status == "complete")
    )
    existing_beat = result.scalars().first()
    return existing_beat


def create_beat_objects(without_user_json, with_user_json, beat_objects):
    """Создание объектов бита для сохранения в базу данных."""
    db_beat_with_user = Beat(
        user_id=with_user_json['user_id'],
        task_id=with_user_json['gen_token'],
        title=with_user_json['title'],
        genre=with_user_json['genre'],
        url=beat_objects[0]['url'],
        image_url=beat_objects[0]['image_url'],
        status="complete"
    )

    db_beat_without_user = Beat(
        task_id=without_user_json['gen_token'],
        title=without_user_json['title'],
        genre=without_user_json['genre'],
        url=beat_objects[1]['url'],
        image_url=beat_objects[1]['image_url'],
        status="complete"
    )

    return db_beat_with_user, db_beat_without_user


async def save_to_database(db, db_beat_with_user, db_beat_without_user):
    """Сохранение объектов бита в базу данных и возврат id для db_beat_with_user."""
    db.add_all([db_beat_with_user, db_beat_without_user])
    await db.commit()
    await db.refresh(db_beat_with_user)
    await db.refresh(db_beat_without_user)
    logger.info("Successfully saved beats to database")
    return db_beat_with_user.id


async def handle_callback(response_data, db: AsyncSession):
    """
    Обработка callback:
      - получение beat объектов (с пользователем и без)
      - извлечение данных пользователя из Redis по жанру
      - создание и сохранение в БД объектов Beat
    """
    # 1. Обработка аудио и изображений, получение beat объектов
    beat_objects = await process_beat_audio_and_image(response_data, db)
    beat_object_for_user = beat_objects[0]
    beat_object_without_user = beat_objects[1]
    # 2. Получаем данные пользователя из Redis по жанру
    user = get_and_remove_user_by_genre(beat_object_for_user['genre'])
    if "error" in user:
        raise HTTPException(status_code=404, detail="User data not found in Redis")
    # 3. Создаём объекты Beat для сохранения в БД
    # Объект с пользователем (с user_id из Redis)
    db_beat_with_user = Beat(
        user_id=user['user_id'],
        task_id=beat_object_for_user.get('task_id', None),
        title=beat_object_for_user['title'],
        genre=beat_object_for_user['genre'],
        url=beat_object_for_user['url'],
        image_url=beat_object_for_user['image_url'],
        status="complete"
    )
    # Объект без пользователя
    db_beat_without_user = Beat(
        task_id=beat_object_without_user.get('task_id', None),
        title=beat_object_without_user['title'],
        genre=beat_object_without_user['genre'],
        url=beat_object_without_user['url'],
        image_url=beat_object_without_user['image_url'],
        status="complete"
    )
    beat_id = await save_to_database(db, db_beat_with_user, db_beat_without_user)
    return {"message": "Beat processed and saved successfully", "beat_id": beat_id}


async def notify_user_about_beat(beat_id: int, db: AsyncSession, manager: ConnectionManager):
    """Извлечение email пользователя по beat_id и отправка ему JSON объекта через WebSocket."""
    # Получаем бит по beat_id
    beat = await db.execute(select(Beat).where(Beat.id == beat_id))
    beat = beat.scalars().first()  # Извлекаем первый результат (бит)

    if not beat:
        raise HTTPException(status_code=404, detail=f"Beat with id {beat_id} not found.")

    # Получаем пользователя по user_id из бита
    if beat.user_id:
        user = await db.execute(select(User).where(User.id == beat.user_id))
        user = user.scalars().first()  # Извлекаем пользователя

        if user:
            user_email = user.email

            # Формируем объект с данными о бите
            beat_data = {
                "id": beat.id,
                "user_id": beat.user_id,
                "task_id": beat.task_id,
                "genre": beat.genre,
                "title": beat.title,
                "status": beat.status,
                "url": beat.url,
                "image_url": beat.image_url,
                "created_at": beat.created_at.isoformat(),  # Преобразуем datetime в строку
            }

            # Отправляем JSON-объект через WebSocket
            await manager.broadcast(user_email, json.dumps(beat_data))  # Сериализация в JSON
        else:
            raise HTTPException(status_code=404, detail=f"User with id {beat.user_id} not found.")
    else:
        raise HTTPException(status_code=404, detail=f"Beat with id {beat_id} does not have an associated user.")



async def get_genre_by_prompt(prompt: str, db: AsyncSession):
    """
    Ищет жанр по переданному prompt в БД.

    :param prompt: Текстовый промпт
    :param db: Асинхронная сессия БД
    :return: Название жанра или None, если не найдено
    """
    # Нормализация prompt: убираем пробелы, \n и приводим к нижнему регистру
    normalized_prompt = re.sub(r'\s+', '', prompt).lower()
    logger.info(normalized_prompt)
    # Получаем все записи жанров из БД
    result = await db.execute(select(GenrePrompt))
    genre_prompts = result.scalars().all()

    # Проверяем, есть ли совпадение
    for genre_prompt in genre_prompts:
        db_prompt_normalized = re.sub(r'\s+', '', genre_prompt.prompt).lower()
        if db_prompt_normalized == normalized_prompt:
            return genre_prompt.genre  # Возвращаем найденный жанр

    return None  # Если жанр не найден


def get_and_remove_user_by_genre(genre: str):
    # Формируем ключ с жанром
    key_pattern = f"genreBeat:{genre}:with_user:*"

    # Получаем все ключи для данного жанра
    keys = redis_client.keys(key_pattern)

    # Если ключи не найдены, возвращаем ошибку
    if not keys:
        return {"error": "No data found for this genre"}

    # Получаем первый найденный ключ
    first_key = keys[0]

    # Получаем данные по этому ключу
    data = redis_client.get(first_key)

    if data:
        # Преобразуем данные из формата JSON в Python-словарь
        beat_data = json.loads(data)

        # Удаляем ключ из Redis
        redis_client.delete(first_key)

        # Возвращаем данные
        logger.info(beat_data)
        return beat_data
    else:
        return {"error": "Data not found in Redis"}