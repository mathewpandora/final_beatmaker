from app.core.redis_client import redis_client
import os
from dotenv import load_dotenv
import uuid
import jwt
from fastapi import FastAPI,HTTPException

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "my_secret_key")
ALGORITHM = "HS256"

app = FastAPI()


def create_access_token(data: dict) -> str:
    """
    Создает JWT-токен с уникальным идентификатором (JTI).
    """
    unique_id = str(uuid.uuid4())  # Генерируем уникальный идентификатор токена (JTI)
    to_encode = data.copy()
    to_encode["jti"] = unique_id  # Добавляем JTI

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY не задан в переменных окружения.")

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def is_token_valid(access_token: str) -> dict:
    """
    Проверяет валидность токена и его наличие в черном списке.

    Возвращает:
        dict: Раскодированные данные токена.

    Выбрасывает:
        HTTPException: Если токен истек, некорректен или в черном списке.
    """
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")

        if redis_client.exists(f"blacklist:{jti}"):
            raise HTTPException(status_code=401, detail="Токен недействителен (в черном списке).")

        return payload  # Если токен валиден, возвращаем его данные

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк!")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Некорректный токен!")


def invalidate_access_token(access_token: str):
    """
    Деактивирует токен, добавляя его в черный список Redis.
    В случае с бесконечным сроком жизни токена мы не учитываем TTL.
    """
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")

        # Проверка, есть ли токен уже в черном списке
        if redis_client.exists(f"blacklist:{jti}"):
            raise HTTPException(status_code=400, detail="Токен уже недействителен!")

        # Помечаем токен как недействительный в Redis без срока действия (токен живет вечно)
        redis_client.set(f"blacklist:{jti}", "invalid")  # Сохраняем токен в черном списке
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истёк!")  # Этот случай не должен быть актуален при бесконечном сроке жизни
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Некорректный токен!")

