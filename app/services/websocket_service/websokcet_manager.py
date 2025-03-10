from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Словарь: ключ — email пользователя, значение — список WebSocket-соединений
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, user_email: str, websocket: WebSocket):
        # Регистрируем новое соединение
        await websocket.accept()
        if user_email not in self.active_connections:
            self.active_connections[user_email] = []
        self.active_connections[user_email].append(websocket)

    def disconnect(self, user_email: str, websocket: WebSocket):
        # Убираем соединение из списка активных
        if user_email in self.active_connections:
            self.active_connections[user_email].remove(websocket)
            if not self.active_connections[user_email]:
                del self.active_connections[user_email]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, user_email: str, message: str):
        # Отправляем сообщение всем соединениям указанного пользователя
        if user_email in self.active_connections:
            for connection in self.active_connections[user_email]:
                await connection.send_text(message)
                await connection.close()  # Закрыть соединение после отправки сообщения

            # После отправки всех сообщений для этого пользователя, удаляем его из активных соединений
            del self.active_connections[user_email]

# Глобальный экземпляр менеджера соединений
manager = ConnectionManager()


def get_manager() -> ConnectionManager:
    """Зависимость для получения экземпляра ConnectionManager."""
    return manager

