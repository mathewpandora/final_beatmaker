import requests

# Замените на ваш URL
url = "http://localhost:8000/user/get_beats"

# Если нужен заголовок авторизации, добавьте его здесь
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmb3JzdHVkaW5nb25seUB5YW5kZXgucnUiLCJqdGkiOiIyMjBlY2EyNy04OGFhLTQxMmYtOGQ0MC02MDhlZmFmNjA0NzMifQ.RBxGXnDTRYrZDtnj6-4QoVZq-EmI0RMgkutiQ5A4KGU",  # Укажите ваш токен
    "Content-Type": "application/json",
}

# Параметры запроса
params = {
    "page": 1,       # Укажите нужную страницу
    "page_size": 5,  # Укажите размер страницы
}

# Выполняем POST-запрос
response = requests.post(url, headers=headers, params=params)

# Проверяем статус-код ответа
if response.status_code == 200:
    # Успешный ответ, обрабатываем данные
    user_info = response.json()
    print("User beats:", user_info)
else:
    # Обработка ошибки
    print("Error:", response.status_code, response.json())
