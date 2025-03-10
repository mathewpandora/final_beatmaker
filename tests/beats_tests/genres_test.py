import requests

# Замените на ваш URL
url = "http://localhost:8000/genres/get_genres"

# Если нужен заголовок авторизации, добавьте его здесь


# Параметры запроса


# Выполняем POST-запрос
response = requests.get(url)

# Проверяем статус-код ответа
if response.status_code == 200:
    # Успешный ответ, обрабатываем данные
    user_info = response.json()
    print("User genres:", user_info)
else:
    # Обработка ошибки
    print("Error:", response.status_code, response.json())
