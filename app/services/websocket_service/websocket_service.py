from fastapi import WebSocket, WebSocketDisconnect, HTTPException, status
from typing import Optional
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Beat
from app.core.redis_client import redis_client
import logging
import asyncio

logger = logging.getLogger("app")

# OAuth2PasswordBearer для извлечения токена
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def check_beat_in_redis(uuid_beat_id: str):
    """Проверяем, существует ли запись в Redis для данного title."""
    key_without_user = f"beat:{uuid_beat_id}:without_user"
    key_with_user = f"beat:{uuid_beat_id}:with_user"

    without_user_data = redis_client.get(key_without_user)
    with_user_data = redis_client.get(key_with_user)

    if without_user_data and with_user_data:
        return True
    return False


async def check_beat_in_db(db: AsyncSession, uuid_beat_id: str):
    """Проверяем, существует ли бит с данным title в базе данных и статусом 'complete'."""
    result = await db.execute(
        select(Beat).filter(Beat.title == uuid_beat_id, Beat.status == "complete")
    )
    existing_beat = result.scalars().first()
    return existing_beat


async def process_beat_websocket(ws: WebSocket, title: str, db: AsyncSession):
    """Логика обработки WebSocket соединения."""
    await ws.accept()

    # Проверка, если бит уже есть в Redis
    beat_in_redis = await check_beat_in_redis(title)
    if not beat_in_redis:
        await ws.send_text("No beat data in Redis. Waiting for it...")

    # Проверка, если бит уже есть в базе данных
    db_beat = await check_beat_in_db(db, title)
    if db_beat:
        # Если бит найден в базе данных с статусом 'complete'
        beat_data = {
            "title": db_beat.title,
            "url": db_beat.url,
            "image_url": db_beat.image_url
        }
        await ws.send_json(beat_data)
        await ws.close()
        return

    # Если бит еще не существует в базе данных, продолжаем ждать
    try:
        while not db_beat:
            db_beat = await check_beat_in_db(db, title)
            if db_beat:
                # Если бит найден в базе данных
                beat_data = {
                    "genre": db_beat.genre,
                    "url": db_beat.url,
                    "image_url": db_beat.image_url
                }
                await ws.send_json(beat_data)
                await ws.close()
                return

            # Если бит не найден, продолжаем ожидать с задержкой
            await ws.send_text("Waiting for beat to appear in the database...")
            await asyncio.sleep(20)  # Задержка 20 секунд перед следующей проверкой

    except WebSocketDisconnect:
        logger.info(f"Client disconnected for beat {title}")


async def get_token_from_url(token: Optional[str] = None) -> str:
    """Получаем токен из параметра URL, если его нет — выбрасываем ошибку"""
    print("1111")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Токен не предоставлен")
    return token