import requests

BASE_URL = 'http://localhost:5000'


def test_add_fingerprint(image_path, name):
    """Тест для API добавления нового участника с изображением лица."""
    url = f'{BASE_URL}/api/add_fingerprint'
    files = {'image': open(image_path, 'rb')}
    data = {'name': name}

    response = requests.post(url, files=files, data=data)

    if response.status_code == 201:
        print(f"Участник {name} успешно добавлен:")
        print(response.json())
    elif response.status_code == 409:
        print(f"Ошибка: Участник {name} уже существует.")
        print(response.json())
    elif response.status_code == 400:
        print(f"Ошибка запроса: {response.status_code} - {response.json()['error']}")
    else:
        print(f"Неизвестная ошибка добавления участника: {response.status_code}")
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Ответ сервера не является JSON.")


def test_compare_fingerprint(image_path):
    """Тест для API сравнения отпечатков лиц."""
    url = f'{BASE_URL}/api/compare_fingerprint'
    files = {'image': open(image_path, 'rb')}

    response = requests.post(url, files=files)

    if response.status_code == 200:
        print("Отпечаток лица распознан:")
        print(response.json())
    elif response.status_code == 404:
        print("Совпадений не найдено.")
        print(response.json())
    elif response.status_code == 400:
        print(f"Ошибка запроса: {response.status_code} - {response.json()['error']}")
    else:
        print(f"Неизвестная ошибка сравнения отпечатков: {response.status_code}")
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Ответ сервера не является JSON.")


def test_voice_recognition_success():
    """Тест для API voice_recognition с успешным результатом."""
    url = f'{BASE_URL}/api/voice_recognition'
    data = {"transcript": "Как узнать погоду?"}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        print("Успешный запрос на voice_recognition:")
        print(response.json())
    elif response.status_code == 404:
        print("Совпадений не найдено.")
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}")
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Ответ сервера не является JSON.")


def test_voice_recognition_no_match():
    """Тест для API voice_recognition без совпадений."""
    url = f'{BASE_URL}/api/voice_recognition'
    data = {"transcript": "Как работает ядерный реактор?"}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        print("Успешный запрос на voice_recognition (не должно произойти):")
        print(response.json())
    elif response.status_code == 404:
        print("Тест успешен: Совпадений не найдено.")
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}")
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Ответ сервера не является JSON.")


def test_voice_answer():
    """Тест для API voice_answer (получение аудиофайла с ответом)."""
    url = f'{BASE_URL}/api/voice_answer'
    data = {"transcript": "Как узнать погоду?"}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        # Проверяем, что возвращается аудиофайл и сохраняем его
        content_type = response.headers['Content-Type']
        if content_type == 'audio/wav':
            with open('response.wav', 'wb') as f:
                f.write(response.content)
            print("Аудио ответ успешно получен и сохранён как 'response.wav'.")
        else:
            print(f"Ошибка: Ожидался аудиофайл, но был получен {content_type}")
    elif response.status_code == 404:
        print("Совпадений не найдено.")
        print(response.json())
    else:
        print(f"Ошибка: {response.status_code}")
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Ответ сервера не является JSON.")


def test_face_recognition_greeting(image_path):
    """Тест для API face_recognition_greeting (распознавание лица и приветствие)."""
    url = f'{BASE_URL}/api/face_recognition_greeting'
    files = {'image': open(image_path, 'rb')}

    response = requests.post(url, files=files)

    if response.status_code == 200:
        # Проверяем, что возвращается аудиофайл и сохраняем его
        content_type = response.headers['Content-Type']
        if content_type == 'audio/wav':
            with open('greeting.wav', 'wb') as f:
                f.write(response.content)
            print("Аудио приветствие успешно получено и сохранено как 'greeting.wav'.")
        else:
            print(f"Ошибка: Ожидался аудиофайл, но был получен {content_type}")
    elif response.status_code == 404:
        print("Участник не найден или лицо не распознано.")
        print(response.json())
    elif response.status_code == 400:
        print(f"Ошибка запроса: {response.status_code} - {response.json()['error']}")
    else:
        print(f"Ошибка: {response.status_code}")
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Ответ сервера не является JSON.")


if __name__ == '__main__':
    # Тестирование добавления нового участника с изображением лица
    print("Тестирование добавления нового участника с изображением лица:")
    test_add_fingerprint('test.jpg', 'John Face')

    # Тестирование повторного добавления уже существующего участника
    print("\nТестирование добавления уже существующего участника:")
    test_add_fingerprint('test.jpg', 'John Face')

    # Тестирование сравнения отпечатка лица
    print("\nТестирование сравнения отпечатка лица:")
    test_compare_fingerprint('test.jpg')

    # Тестирование voice_recognition с успешным результатом
    print("\nТестирование voice_recognition (успешный результат):")
    test_voice_recognition_success()

    # Тестирование voice_recognition без совпадений
    print("\nТестирование voice_recognition (нет совпадений):")
    test_voice_recognition_no_match()

    # Тестирование voice_answer (получение аудиофайла)
    print("\nТестирование voice_answer (получение аудиофайла):")
    test_voice_answer()

    # Тестирование face_recognition_greeting (распознавание лица и приветствие)
    print("\nТестирование face_recognition_greeting (распознавание лица и приветствие):")
    test_face_recognition_greeting('test.jpg')
