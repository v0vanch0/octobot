import requests

# URL endpoint для вопроса-ответа
url = 'http://127.0.0.1:5000/ask_question' # Замените на адрес и порт вашего приложения

# Список тестовых вопросов
test_questions = [
    "Hial oko",
    "Какой сегодня день?",
    "Где находится туалет?",
    "Что ты умеешь?"
    # ... другие тестовые вопросы
]

# Запускаем тесты
for question in test_questions:
    data = {'question': question}
    response = requests.post(url, data=data)

    if response.status_code == 200:
        answer = response.json()['answer']
        print(f"Вопрос: {question}\nОтвет: {answer}\n")
    else:
        print(f"Ошибка: {response.status_code} - {response.text}\n")