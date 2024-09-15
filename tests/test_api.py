import requests

BASE_URL = 'http://localhost:5000'


def test_add_participant(image_path, name):
    """Тест для API добавления нового участника с проверкой на дубликаты и ошибки."""
    url = f'{BASE_URL}/api/add_participant'

    try:
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
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
    except FileNotFoundError:
        print(f"Файл {image_path} не найден.")
    except Exception as e:
        print(f"Произошла ошибка при попытке добавления участника: {str(e)}")


def test_recognize_face(image_path):
    """Тест для API распознавания лиц."""
    url = f'{BASE_URL}/api/recognize'

    try:
        with open(image_path, 'rb') as image_file:
            files = {'image': image_file}
            response = requests.post(url, files=files)

            if response.status_code == 200:
                print("Распознавание прошло успешно:")
                print(response.json())
            elif response.status_code == 400:
                print(f"Ошибка запроса: {response.status_code} - {response.json()['error']}")
            else:
                print(f"Неизвестная ошибка распознавания лица: {response.status_code}")
                try:
                    print(response.json())
                except requests.exceptions.JSONDecodeError:
                    print("Ответ сервера не является JSON.")
    except FileNotFoundError:
        print(f"Файл {image_path} не найден.")
    except Exception as e:
        print(f"Произошла ошибка при попытке распознавания лица: {str(e)}")


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

def test_voice_recognition_success_sim():
    """Тест для API voice_recognition с успешным результатом."""
    url = f'{BASE_URL}/api/voice_recognition'
    data = {"transcript": "Кто ты?"}

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
    data = {"transcript": "Как работает ядерный реактор?"}  # Текст, который не должен найтись в базе

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


def test_voice_recognition_missing_transcript():
    """Тест для API voice_recognition с некорректным запросом (без transcript)."""
    url = f'{BASE_URL}/api/voice_recognition'
    data = {}  # Отправляем пустой запрос без transcript

    response = requests.post(url, json=data)

    if response.status_code == 400:
        print("Тест успешен: API вернул ошибку при отсутствии transcript.")
        print(response.json())
    else:
        print(f"Неожиданный код ответа: {response.status_code}")
        try:
            print(response.json())
        except requests.exceptions.JSONDecodeError:
            print("Ответ сервера не является JSON.")


if __name__ == '__main__':
    # Тестирование добавления нового участника
    print("Тестирование добавления нового участника:")
    test_add_participant('test.jpg', 'John New')  # Укажите правильный путь к изображению нового лица

    # Тестирование повторного добавления уже существующего участника
    print("\nТестирование добавления уже существующего участника:")
    test_add_participant('test.jpg', 'John New')  # Повторный запрос для проверки на дубликат

    # Тестирование распознавания лица
    print("\nТестирование распознавания лица:")
    test_recognize_face('test.jpg')  # Укажите правильный путь к изображению

    # Тестирование voice_recognition с успешным результатом
    print("\nТестирование voice_recognition (успешный результат):")
    test_voice_recognition_success()
    # Тестирование voice_recognition с успешным результатом
    print("\nТестирование voice_recognition (успешный результат):")
    test_voice_recognition_success_sim()

    # Тестирование voice_recognition без совпадений
    print("\nТестирование voice_recognition (нет совпадений):")
    test_voice_recognition_no_match()

    # Тестирование voice_recognition с некорректным запросом
    print("\nТестирование voice_recognition (без transcript):")
    test_voice_recognition_missing_transcript()
