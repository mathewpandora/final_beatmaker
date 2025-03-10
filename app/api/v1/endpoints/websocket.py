from fastapi import WebSocket, Depends, APIRouter, WebSocketDisconnect
from app.core.security import get_current_user_ws
from app.services.websocket_service.websokcet_manager import manager
import asyncio
import logging

logger = logging.getLogger("app")

router = APIRouter()


@router.websocket("/generate-beat")
async def websocket_endpoint(ws: WebSocket, user_email: str = Depends(get_current_user_ws)):
    try:
        logger.info("🔄 WebSocket connection attempt for user: %s", user_email)
        # Регистрируем соединение через менеджер
        await manager.connect(user_email, ws)
        logger.info("✅ WebSocket connection established for user: %s", user_email)
        while True:
            # Здесь можно реализовать получение сообщений от клиента, если требуется,
            # или просто поддерживать соединение активным
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(user_email, ws)
        logger.warning("🔌 WebSocket disconnected for user: %s", user_email)
    except Exception as e:
        logger.error("❌ WebSocket error: %s", e)


