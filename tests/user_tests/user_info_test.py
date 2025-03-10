import requests

# URL вашего API
BASE_URL = "http://127.0.0.1:8000/auth"  # Убедитесь, что путь правильный

# Данные запроса
payload = {"email": "forstudingonly@yandex.ru"}  # Укажите реальный email

try:
    # Отправляем GET-запрос (если сервер ожидает GET)
    response = requests.post(f"{BASE_URL}/user_info", json=payload)

    # Проверяем статус-код
    if response.status_code == 200:
        print("🟢 User info:", response.json())  # Выводим ответ сервера
    else:
        print(f"🔴 Error {response.status_code}: {response.json()}")  # Выводим ошибку

except requests.RequestException as e:
    print(f"❌ Request failed: {e}")

