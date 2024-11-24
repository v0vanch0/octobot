import pandas as pd
import json
import os
import hashlib
from components.utils import get_db_connection
from TTS.api import TTS
import string

# Инициализация модели TTS с безопасными настройками
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True).cuda()

# Путь к JSON файлу с аудио данными
audio_data_file = "audio/audio_data.json"


# Функция для создания уникального имени файла на основе ответа
def generate_unique_filename(answer, length=8):
    answer_hash = hashlib.md5(answer.encode('utf-8')).hexdigest()[:length]
    return f"audio_{answer_hash}.mp3"


# Функция для очистки текста
def clean_text(text):
    """Удаляет знаки препинания и приводит текст к нижнему регистру."""
    return text.translate(str.maketrans('', '', string.punctuation)).lower()


def load_csv_to_db(csv_path):
    try:
        # Подключение к базе данных
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM qa;')

        # Проверка существования таблицы
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="qa";')
        if not cursor.fetchone():
            print("Error: Table 'qa' does not exist in the database.")
            return

        # Чтение CSV с помощью pandas
        data = pd.read_csv(csv_path)

        # Проверка наличия необходимых столбцов
        if 'Вопрос, который вы бы хотели задать' not in data.columns or 'Ответ на заданный вами вопрос' not in data.columns:
            print(
                "Error: CSV file must contain 'Вопрос, который вы бы хотели задать' and 'Ответ на заданный вами "
                "вопрос' columns.")
            return

        # Загрузка текущих данных аудио
        if os.path.exists(audio_data_file):
            with open(audio_data_file, 'r', encoding='utf-8') as file:
                audio_data = json.load(file)
        else:
            audio_data = {}

        # Обработка каждой строки из CSV
        for _, row in data.iterrows():
            # Очистка текста вопросов и ответов
            question = clean_text(row['Вопрос, который вы бы хотели задать'])
            answer = clean_text(row['Ответ на заданный вами вопрос'])

            # Проверка на существование вопроса-ответа в базе
            cursor.execute('SELECT id FROM qa WHERE question = ? AND answer = ?', (question, answer))
            result = cursor.fetchone()

            if result:
                # Если запись существует, обновляем ответ
                qa_id = result['id']
                cursor.execute('UPDATE qa SET answer = ? WHERE id = ?', (answer, qa_id))
                print(f"Updated existing entry for question: {question}")
            else:
                # Если записи нет, создаем новую
                cursor.execute('INSERT INTO qa (question, answer) VALUES (?, ?)', (question, answer))
                qa_id = cursor.lastrowid
                print(f"Inserted new entry for question: {question}")

            # Генерация уникального имени файла
            audio_filename = generate_unique_filename(answer)
            audio_file_path = os.path.join("audio", "files", audio_filename)

            # Создание аудиофайла
            tts.tts_to_file(
                text=answer,
                speaker_wav="./audio/files/example_04_real.wav",
                language="ru",
                file_path=audio_file_path,
                speed=1.15
            )

            # Сохранение пути к аудио в JSON
            audio_data[answer] = audio_file_path

        # Запись обновленных данных в JSON файл
        with open(audio_data_file, 'w', encoding='utf-8') as file:
            json.dump(audio_data, file, ensure_ascii=False, indent=4)

        # Сохранение изменений в базе данных
        conn.commit()
        print("CSV data imported and updated successfully.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


# Укажите путь к вашему CSV-файлу
csv_path = 'database/octo.csv'
load_csv_to_db(csv_path)
