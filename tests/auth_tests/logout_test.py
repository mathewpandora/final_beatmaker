import requests

# Указываем URL вашего эндпоинта
url = "http://localhost:8000/auth/logout"

# Токен, который нужно передать в запросе
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QHlhbmRleC5ydSIsImp0aSI6IjljZTViM2JhLTMxNTQtNGEzNi05MzU1LWY4ZGVkNDIzMTdlZSIsImV4cCI6MTc0MDMxNDE2MH0.R_jvVESgoU7WR9HJ0hYcJGrjyeoMnXUTkvk-xfhJkbk"
# Заголовки с передачей токена в формате Bearer
headers = {
    "Authorization": f"Bearer {token}"
}

# Выполняем POST-запрос к эндпоинту
response = requests.post(url, headers=headers)

# Выводим ответ от сервера
print(response.status_code)  # Статус код ответа (например, 200)
print(response.json())  # Ответ в формате JSON

"""
200
{'message': 'Вы успешно вышли', 'user_email': 'forstudingonly@yandex.ru'}
"""

"""
401
{'detail': 'Токен недействителен (в черном списке).'}
"""