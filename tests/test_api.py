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


def test_add_existing_participant(image_path, name):
    """Тест для проверки добавления уже существующего участника."""
    print("\nТест: Попытка добавить участника, который уже существует.")
    test_add_participant(image_path, name)


def test_recognize_similar_face(image_path):
    """Тест для API распознавания лица, которое похоже, но не является дубликатом."""
    print("\nТест: Попытка распознать лицо, которое схоже, но не идентично.")
    test_recognize_face(image_path)


def test_recognize_unknown_face(image_path):
    """Тест для API распознавания лица, которое не зарегистрировано."""
    print("\nТест: Попытка распознать лицо, которое не зарегистрировано в базе данных.")
    test_recognize_face(image_path)


if __name__ == '__main__':
    # Тестирование добавления нового участника
    print("Тестирование добавления нового участника:")
    test_add_participant('test.jpg', 'John New')  # Укажите правильный путь к изображению нового лица

    # Тестирование повторного добавления уже существующего участника
    print("\nТестирование добавления уже существующего участника:")
    test_add_existing_participant('test.jpg', 'John New')  # Повторный запрос для проверки на дубликат

    # Тестирование распознавания лица, которое похоже, но не идентично
    print("\nТестирование распознавания схожего лица:")
    test_recognize_similar_face('test_similar.jpg')  # Укажите путь к изображению схожего лица

    # Тестирование распознавания чужого лица
    print("\nТестирование распознавания чужого лица:")
    test_recognize_unknown_face(
        'test2.jpg')  # Укажите путь к изображению лица, не зарегистрированного в базе данных
