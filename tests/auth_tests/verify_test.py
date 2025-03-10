import requests

# Адрес вашего FastAPI приложения
url = "http://localhost:8000/auth/verify"

# Код верификации, который пользователь отправляет
verification_code = "225119"

data = {
    "code": { "code": verification_code },  # Код верификации теперь передается как объект
    "user": {
        "email": "forstudingonly@yandex.ru",
        "password": "Minecraft5"
    }
}
# Отправляем POST-запрос
response = requests.post(url, json=data)

# Проверка, если запрос прошел успешно
if response.status_code == 200:
    print("Ответ от сервера:", response.json())
else:
    print(f"Ошибка {response.status_code}: {response.text}")

#200 {"message": "Пользователь успешно верифицирован", "user_email": user.email}
