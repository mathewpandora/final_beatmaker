from app.core.redis_client import redis_client
import uuid
import hashlib
import random
import time


def generate_unique_id():
    """Генерирует уникальный ID и проверяет его в Redis."""

    while True:  # Бесконечный цикл, пока не найдём уникальный ID
        # 1. Генерируем новый ID
        unique_part = str(uuid.uuid4())
        random_part = str(random.randint(100000, 999999))
        timestamp_part = str(int(time.time() * 1000))

        raw_id = unique_part + random_part + timestamp_part
        complex_id = hashlib.sha256(raw_id.encode()).hexdigest()[:32]  # Берём первые 32 символа

        # 2. Проверяем в Redis, есть ли такой ключ
        if not redis_client.sismember("generated_ids", complex_id):
            # 3. Если нет, добавляем в множество Redis
            redis_client.sadd("generated_ids", complex_id)
            return complex_id  # Возвращаем уникальный ID



