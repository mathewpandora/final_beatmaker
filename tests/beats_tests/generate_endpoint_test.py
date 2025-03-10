import requests

# URL эндпоинта
url = "http://127.0.0.1:8000/beats/generate"

# Тело запроса (это должен быть объект JSON)
data = {
    "genre": "drill"  # Пример данных для BaseGenre
}

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkB5YW5kZXgucnUiLCJqdGkiOiI1ZTI5OWNhZS1lZTFlLTQ0NDItYTg2My1mMzc4OWIxNWJmZjkifQ.zfbVz4I-4oMox1dNKUdPWkDAbVIR6pZPGwtjncszdJk
# Заголовки для авторизации (если требуется)
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MUB5YW5kZXgucnUiLCJqdGkiOiJkNzE1OGU4YS03MTNjLTQxYzItODNmYi1jMjdmOWVkZWNkNzcifQ.lQS04LGJ4TUro2B7-nLuetBvG_VVaofwdDq-j3g0xIo"  # Заменить <your_token> на действительный токен
}

# Отправка POST запроса
response = requests.post(url, json=data, headers=headers)

# Выводим ответ
if response.status_code == 200:
    print("Response:", response.json())
else:
    print(f"Error {response.status_code}: {response.text}")

"""
Response: {'message': 'Beat stored in Redis successfully', 'beat_id': '06b09800c66957010bf8997cdd777f1b'}
"""