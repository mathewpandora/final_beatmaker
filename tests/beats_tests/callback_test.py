import requests

# URL вашего API
url = "http://127.0.0.1:8000/beats/callback"

# Данные, которые вы хотите отправить
data = {
    "msg": "All generated successfully.",
    "code": 200,
    "data": [
        {
            "id": "8f50012a-5a6a-4f65-b5a4-2c865fc915d8",
            "tags": "happy, pop, uplifting",
            "title": "2b97c52d1dedad26b9839acb2643543e",
            "prompt": "INSTRUMENTAL MUST BE ONLY IN RAP-drill GENRE WITH DARK TONES AND HARD-HITTING BEATS. DESCRIPTION: A gritty and intense beat for storytelling.",
            "status": "complete",
            "duration": 139,
            "audio_url": "https://cdn1.suno.ai/8f50012a-5a6a-4f65-b5a4-2c865fc915d8.mp3",
            "image_url": "https://cdn2.suno.ai/image_8f50012a-5a6a-4f65-b5a4-2c865fc915d8.jpeg",
            "createTime": "2024-12-12T06:29:21.736Z",
            "model_name": "v4",
            "error_message": None,
            "gpt_description_prompt": "A happy and uplifting pop song"
        },
        {
            "id": "402830a1-82c5-4ff5-99b2-829c64eda2ee",
            "tags": "happy, pop, uplifting",
            "title": "2b97c52d1dedad26b9839acb2643543e",
            "prompt": "INSTRUMENTAL MUST BE ONLY IN RAP-drill GENRE WITH DARK TONES AND HARD-HITTING BEATS. DESCRIPTION: A gritty and intense beat for storytelling.",
            "status": "complete",
            "duration": 156,
            "audio_url": "https://cdn1.suno.ai/402830a1-82c5-4ff5-99b2-829c64eda2ee.mp3",
            "image_url": "https://cdn2.suno.ai/image_402830a1-82c5-4ff5-99b2-829c64eda2ee.jpeg",
            "createTime": "2024-12-12T06:29:21.736Z",
            "model_name": "v4",
            "error_message": None,
            "gpt_description_prompt": "A happy and uplifting pop song"
        }
    ],
    "callbackType": "complete"
}

# Отправка POST-запроса
response = requests.get(url, json=data)

# Проверка ответа
if response.status_code == 200:
    print("Data processed successfully:", response.json())
else:
    print(f"Error: {response.status_code}, {response.text}")
