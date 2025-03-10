from app.services.auth_service.token_service import is_token_valid
from app.core.redis_client import redis_client
from fastapi import HTTPException, Header, status, WebSocket
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError  # ✅ Исправленный импорт
from typing import Optional


# Функция для проверки токена и получения пользователя
async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Проверяет валидность JWT-токена и извлекает данные пользователя.
    Используется в защищенных эндпоинтах.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен не предоставлен или некорректен")

    token = authorization.replace("Bearer ", "").strip()

    try:
        payload = is_token_valid(token)  # Проверяем токен и декодируем
        user_email = payload.get("sub")  # Извлекаем email пользователя

        if not user_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Некорректный токен: отсутствует email")

        # Проверяем, не был ли токен аннулирован (черный список)
        if redis_client.get(f"blacklist:{token}"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен недействителен")

        return user_email  # Возвращаем email пользователя (можно заменить на объект User)

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен истёк")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен")


async def get_current_user_ws(ws: WebSocket) -> str:
    # Извлекаем токен из query-параметров
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=1008)
        raise HTTPException(status_code=401, detail="Токен не предоставлен")

    try:
        payload = is_token_valid(token)  # проверка и декодирование токена
        user_email = payload.get("sub")
        if not user_email:
            await ws.close(code=1008)
            raise HTTPException(status_code=400, detail="Некорректный токен: отсутствует email")
        if redis_client.get(f"blacklist:{token}"):
            await ws.close(code=1008)
            raise HTTPException(status_code=401, detail="Токен недействителен")
        return user_email
    except ExpiredSignatureError:
        await ws.close(code=1008)
        raise HTTPException(status_code=401, detail="Токен истёк")
    except InvalidTokenError:
        await ws.close(code=1008)
        raise HTTPException(status_code=401, detail="Некорректный токен")

