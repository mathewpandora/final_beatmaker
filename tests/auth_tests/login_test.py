import requests

# URL эндпоинта
url = "http://localhost:8000/auth/login"

# Данные для входа (email и пароль)
login_data = {
    "email": "forstudingonly@yandex.ru",  # Укажите email пользователя
    "password": "Minecraft5"
}

# Отправляем POST запрос
response = requests.post(url, json=login_data)

# Проверяем статус код и выводим результат
if response.status_code == 200:
    print("Login successful!")
    data = response.json()
    print("Access token:", data["access_token"])
    print("Token type:", data["token_type"])
else:
    print("Login failed:", response.json())

"""
Login successful!
Access token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmb3JzdHVkaW5nb25seUB5YW5kZXgucnUiLCJqdGkiOiI0MzZjZjczZS0yNDVjLTQ2NzItOGZiMy04MGQ0MzJjZjRlMjkiLCJleHAiOjE3NDAwNzAxODN9.mH0ADCDaClCEOJZEuM2zdvVjsQaJhVDcdcA7ap5tzlk
Token type: bearer
"""


#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkB5YW5kZXgucnUiLCJqdGkiOiI1ZTI5OWNhZS1lZTFlLTQ0NDItYTg2My1mMzc4OWIxNWJmZjkifQ.zfbVz4I-4oMox1dNKUdPWkDAbVIR6pZPGwtjncszdJk
#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MUB5YW5kZXgucnUiLCJqdGkiOiJkNzE1OGU4YS03MTNjLTQxYzItODNmYi1jMjdmOWVkZWNkNzcifQ.lQS04LGJ4TUro2B7-nLuetBvG_VVaofwdDq-j3g0xIo