import requests

# URL вашего эндпоинта
url = "http://127.0.0.1:8000/auth/register"

# Данные, которые отправляются в теле запроса (user.email и user.password)
data = {
    "email": "test2@yandex.ru",  # Укажите email пользователя
    "password": "Minecraft5"    # Укажите пароль пользователя
}

# Отправка POST-запроса
response = requests.post(url, json=data)

# Печать ответа
print(response.status_code)
print(response.json())

"""
200
{'status': 'success', 'message': 'Registration successful. Please check your email to confirm.'}
"""