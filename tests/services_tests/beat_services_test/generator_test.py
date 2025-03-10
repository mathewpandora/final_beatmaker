import asyncio
from app.services.beat_service.generator import generate_beat_by_genre
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("LOVEAI_API_TOKEN")

# Создаем асинхронную функцию для вызова generate_beat_by_genre
async def main():
    response = await generate_beat_by_genre(token, "rasta", "mrkflme")
    print(response)

"""
(200, {'task_id': '1da399ad-1ac9-4bd9-a228-469b57016f16'})
"""


# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())
