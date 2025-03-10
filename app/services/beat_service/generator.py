from typing import Dict, Tuple
import os
import httpx
from app.services.beat_service.generate_functions import create_beat_data, store_in_redis
token = os.getenv("LOVEAI_API_TOKEN")

async def generate_beat_by_genre(db_genre, db_user, db) -> Tuple[int, Dict]:
    if not token:
        raise ValueError("Токен LOVEAI_API_TOKEN отсутствует или не загружен!")

    url = "https://api.loveaiapi.com/music/suno/generate2"
    payload = {
        'prompt': db_genre.prompt,
        'title': "",
        "custom": False,
        "instrumental": True,
        "style": "",
        "callback_url": 'https://mathewpandora.pythonanywhere.com/beats/callback'
    }

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            beat_with_user = create_beat_data(db_user, db_genre)
            store_in_redis(db_genre.genre, beat_with_user)
            return response.status_code, response.json(),
        except httpx.RequestError as e:
            return 500, {"error": str(e)}
