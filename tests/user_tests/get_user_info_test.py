import requests

# Замените на ваш URL
url = "http://localhost:8000/user/user_info"

# Если нужен заголовок авторизации, добавьте его здесь
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmb3JzdHVkaW5nb25seUB5YW5kZXgucnUiLCJqdGkiOiIzNGQ3ZWQzOC00MzJkLTQ2YTAtODQ2Zi04MzE4YjUxMmY2YTEifQ.K8AqM6ONhoA1HxVbiHIQXfuk9n1HFs2L5ZG-l1M3kHU",  # Укажите ваш токен
    "Content-Type": "application/json",
}

# Выполняем POST-запрос
response = requests.post(url, headers=headers)

# Проверяем статус-код ответа
if response.status_code == 200:
    # Успешный ответ, обрабатываем данные
    user_info = response.json()
    print("User Info:", user_info)
else:
    # Обработка ошибки
    print("Error:", response.status_code, response.json())
