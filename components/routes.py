# routes.py
import hashlib
import string
from datetime import datetime, timedelta
import json
import os

import numpy as np
from flask import request, jsonify, send_file
import cv2  # Для обработки изображений
from audio.audio_data import load_audio_data
audiod = load_audio_data()
from components.face_rec import shape_predictor, face_rec_model, face_detector
from components.utils import get_db_connection
from components.voice_recognition import find_best_matching_question
from TTS.api import TTS
import pandas as pd
import logging

mutex = False
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация TTS модели
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").cuda()


def generate_unique_filename(answer, length=8):
    answer_hash = hashlib.md5(answer.encode('utf-8')).hexdigest()[:length]
    return f"audio_{answer_hash}.mp3"


def clean_text(text):
    return text.translate(str.maketrans('', '', string.punctuation)).lower()


# Функция для удаления старых посещений
def delete_old_visits():
    """Удаляет посещения, старше одного года."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cutoff_date = datetime.now() - timedelta(days=365)  # 1 год
    # cursor.execute('DELETE FROM visits WHERE arrival_time < ?', (cutoff_date,))
    cursor.execute('DELETE FROM visits')
    conn.commit()
    conn.close()
    logging.info("Старые посещения удалены.")


# Функция для экспорта посещений в Excel
def export_visits_to_excel():
    """Экспортирует посещения в файл Excel с именами вместо ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем данные о посещениях с именами участников
    cursor.execute('''
        SELECT participants.name, 
               visits.arrival_time
        FROM visits
        JOIN participants ON visits.participant_id = participants.id
    ''')

    rows = cursor.fetchall()
    conn.close()

    # Преобразуем данные в DataFrame
    df = pd.DataFrame(rows, columns=['Имя посетителя', 'Дата и время посещения'])
    filename = f'visits_with_names_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
    # Сохраняем в Excel
    df.to_excel(filename, index=False)
    return filename


def register_routes(app):
    """Функция для регистрации маршрутов приложения Flask."""

    # Предварительная генерация аудио для "не знаю ответа"
    text = "Пока что я не знаю ответа на этот вопрос"
    aud_file = "dont_know.mp3"  # Имя файла без пути
    tts.tts_to_file(text=text,
                    speaker_wav="./audio/files/example_04_real.wav",
                    language="ru",
                    file_path=os.path.join("./audio/files", aud_file),
                    speed=1.15)

    # Добавляем персональное приветствие в JSON
    audio_data_file = "audio/audio_data.json"
    if os.path.exists(audio_data_file):
        with open(audio_data_file, 'r', encoding='utf-8') as file:
            audio_data = json.load(file)
    else:
        audio_data = {}

    audio_data['no similar'] = aud_file  # Сохраняем только имя файла

    with open(audio_data_file, 'w', encoding='utf-8') as file:
        # Перезаписываем JSON файл
        json.dump(audio_data, file, ensure_ascii=False, indent=4)

    # Добавление маршрутов в Flask
    @app.route('/api/delete_old_visits', methods=['DELETE'])
    def delete_old_visits_route():
        """Удаляет посещения старше одного года."""
        try:
            delete_old_visits()
            return jsonify({"message": "Старые посещения успешно удалены."}), 200
        except Exception as e:
            logging.error(f"Ошибка при удалении старых посещений: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/export_visits_to_excel', methods=['GET'])
    def export_visits_to_excel_route():
        """Экспортирует посещения в файл Excel с именами."""
        try:
            filename = export_visits_to_excel()
            return send_file(filename, as_attachment=True), 200
        except Exception as e:
            logging.error(f"Ошибка при экспорте посещений: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/add_fingerprint', methods=['POST'])
    def add_fingerprint():
        """Добавление нового участника с изображением лица и персональным приветствием."""
        try:
            global mutex
            if not mutex:
                mutex = True
                # Получение изображения лица из запроса
                image_file = request.files.get('image')
                name = request.form.get('name')
                personal_greeting = request.form.get('personal_greeting')  # Получение приветствия, если предоставлено

                if not name or not image_file:
                    return jsonify({"error": "Name and image are required."}), 400

                # Чтение изображения с использованием OpenCV
                image_bytes = image_file.read()
                npimg = np.frombuffer(image_bytes, np.uint8)
                image_np = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

                if image_np is None:
                    return jsonify({"error": "Invalid image."}), 400

                # Извлечение цифрового отпечатка лица
                faces = face_detector(image_np)

                if len(faces) == 0:
                    return jsonify({"message": "No face detected in the image."}), 404

                shape = shape_predictor(image_np, faces[0])
                face_embedding = np.array(face_rec_model.compute_face_descriptor(image_np, shape))

                # Преобразуем массив в бинарные данные для хранения
                fingerprint_bytes = face_embedding.tobytes()

                conn = get_db_connection()
                cursor = conn.cursor()

                # Проверяем, существует ли участник с таким же отпечатком
                cursor.execute('SELECT * FROM participants')
                participants = cursor.fetchall()

                for participant in participants:
                    stored_fingerprint = participant['face_embedding']
                    stored_fingerprint = np.frombuffer(stored_fingerprint, dtype=np.float64)
                    distance = np.linalg.norm(stored_fingerprint - face_embedding)
                    if distance < 0.4:  # Задаем порог для сравнения
                        conn.close()
                        return jsonify({"message": f"Participant {participant['name']} already exists."}), 409

                # Генерация персонального приветствия с использованием TTS
                greeting_text = f"Здравствуйте, {name}!"
                greeting_file = f"{name}_greeting.mp3"  # Имя файла без пути
                tts.tts_to_file(text=greeting_text,
                                speaker_wav="./audio/files/example_04_real.wav",
                                language="ru",
                                file_path=os.path.join("./audio/files", greeting_file),
                                speed=1.15)

                # Добавляем персональное приветствие в JSON
                audio_data_file = "audio/audio_data.json"
                if os.path.exists(audio_data_file):
                    with open(audio_data_file, 'r', encoding='utf-8') as file:
                        audio_data = json.load(file)
                else:
                    audio_data = {}

                if personal_greeting:
                    # Сохраняем путь к персональному приветствию как имя файла
                    audio_data[personal_greeting] = greeting_file
                else:
                    # Сохраняем стандартное приветствие
                    audio_data[f"Приветствие для {name}"] = greeting_file

                with open(audio_data_file, 'w', encoding='utf-8') as file:
                    # Перезаписываем JSON файл
                    json.dump(audio_data, file, ensure_ascii=False, indent=4)

                # Добавляем нового участника в базу данных
                cursor.execute('INSERT INTO participants (name, face_embedding) VALUES (?, ?)',
                               (name, fingerprint_bytes))
                conn.commit()
                qa_id = cursor.lastrowid
                conn.close()
                mutex = True
                return jsonify({"message": f"Participant {name} added successfully."}), 201
            else:
                return jsonify({"error": "Слишком много вызовов"}), 400
        except Exception as e:
            logging.error(f"Ошибка при добавлении отпечатка: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/voice_answer', methods=['POST'])
    def voice_answer_route():
        """Обработка текста, нахождение лучшего вопроса и голосовой ответ с использованием TTS."""
        data = request.get_json()

        # Проверяем наличие поля transcript
        transcript = data.get('question', None)
        if not transcript:
            return jsonify({"error": "Transcript is required."}), 400

        # Поиск лучшего совпадения
        best_match = find_best_matching_question(transcript)

        if best_match:
            # Возвращаем аудио файл как ответ
            return jsonify({"audio_path": audiod.get(best_match['answer'], ""), "answer": best_match['answer']}), 200
        else:
            return jsonify(
                {"answer": "Пока я не знаю ответ на данный вопрос", "audio_path": audiod.get('no similar', "")}), 200

    @app.route('/api/audiofile/<path:path>', methods=['GET'])
    def get_audio_file(path):
        try:
            file_path = os.path.join("./audio/files", path)
            if not os.path.isfile(file_path):
                logging.error(f"Audio file not found: {file_path}")
                return jsonify({"error": "No such file"}), 400
            return send_file(file_path, mimetype='audio/mp3'), 200
        except Exception as e:
            logging.error(f"Error sending audio file: {e}")
            return jsonify({"error": "Internal server error."}), 500

    @app.route('/api/face_recognition_greeting', methods=['POST'])
    def face_recognition_greeting():
        """Распознавание лица, приветствие и запись визита."""
        # Получение файла изображения из запроса
        image_file = request.files.get('image')

        if not image_file:
            return jsonify({"error": "Image file is required."}), 400

        # Чтение изображения с использованием OpenCV
        image_bytes = image_file.read()
        npimg = np.frombuffer(image_bytes, np.uint8)
        image_np = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        if image_np is None:
            logging.error("Invalid image.")
            return jsonify({"error": "Invalid image."}), 400

        # Извлечение цифрового отпечатка лица
        faces = face_detector(image_np)

        if len(faces) == 0:
            logging.info("No face detected in the image.")
            return jsonify({"message": "No face detected in the image."}), 404

        shape = shape_predictor(image_np, faces[0])
        face_embedding = np.array(face_rec_model.compute_face_descriptor(image_np, shape))

        # Поиск участника по отпечатку лица
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM participants')
        participants = cursor.fetchall()

        recognized_participant = None
        for participant in participants:
            stored_fingerprint = participant['face_embedding']
            stored_fingerprint = np.frombuffer(stored_fingerprint, dtype=np.float64)
            distance = np.linalg.norm(stored_fingerprint - face_embedding)
            if distance < 0.6:
                recognized_participant = participant
                break

        if recognized_participant is None:
            conn.close()
            logging.info("No matching participant found.")
            return jsonify({"message": "No matching participant found."}), 404

        # Проверка, посещал ли участник уже сегодня
        participant_id = recognized_participant['id']
        today = datetime.now().date()
        cursor.execute('SELECT * FROM visits WHERE participant_id = ? AND DATE(arrival_time) = ?',
                       (participant_id, today))

        visit_today = cursor.fetchone()

        if visit_today:
            conn.close()
            logging.info("Visitor has already visited today.")
            return jsonify({"message": "Visitor has already visited today."}), 400

        # Приветствие участника с использованием персонального приветствия
        participant_name = recognized_participant['name']
        audio_data_file = "audio/audio_data.json"

        # Загрузка файла с аудиопутями
        if os.path.exists(audio_data_file):
            with open(audio_data_file, 'r', encoding='utf-8') as file:
                audio_data = json.load(file)
        else:
            audio_data = {}

        # Проверяем, есть ли персональное приветствие для участника
        greeting_key = f"Приветствие для {participant_name}"
        greeting_path = audio_data.get(greeting_key, audio_data.get('no similar', ""))

        # Запись визита в базу данных
        cursor.execute('INSERT INTO visits (participant_id, arrival_time) VALUES (?, ?)',
                       (participant_id, datetime.now()))
        conn.commit()
        conn.close()

        # Возвращаем путь к аудио файлу приветствия
        logging.info("audio_path")
        return jsonify({"audio_path": greeting_path}), 200

    # CRUD маршруты для посетителей (participants)

    @app.route('/api/visitors', methods=['GET'])
    def get_visitors():
        """Получение списка всех участников (посетителей)."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT id, name FROM participants')
            rows = cursor.fetchall()
            visitors = [{"id": row["id"], "name": row["name"]} for row in rows]

            conn.close()

            return jsonify({"visitors": visitors}), 200
        except Exception as e:
            logging.error(f"Ошибка при получении посетителей: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/visitors/<int:visitor_id>', methods=['GET'])
    def get_visitor(visitor_id):
        """Получение данных конкретного участника по его ID."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT id, name FROM participants WHERE id = ?', (visitor_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                visitor = {"id": row["id"], "name": row["name"]}
                return jsonify({"visitor": visitor}), 200
            else:
                return jsonify({"message": "Visitor not found."}), 404
        except Exception as e:
            logging.error(f"Ошибка при получении участника: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/visitors/<int:visitor_id>', methods=['PUT'])
    def update_visitor(visitor_id):
        """Обновление данных участника по его ID."""
        try:
            data = request.get_json()
            name = data.get('name')
            if not name:
                return jsonify({"error": "Name is required for update."}), 400

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('UPDATE participants SET name = ? WHERE id = ?', (name, visitor_id))
            conn.commit()
            conn.close()

            if cursor.rowcount > 0:
                return jsonify({"message": "Visitor updated successfully."}), 200
            else:
                return jsonify({"message": "Visitor not found."}), 404
        except Exception as e:
            logging.error(f"Ошибка при обновлении участника: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/visitors/<int:visitor_id>', methods=['DELETE'])
    def delete_visitor(visitor_id):
        """Удаление участника по его ID."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM participants WHERE id = ?', (visitor_id,))
            conn.commit()
            conn.close()

            if cursor.rowcount > 0:
                return jsonify({"message": "Visitor deleted successfully."}), 200
            else:
                return jsonify({"message": "Visitor not found."}), 404
        except Exception as e:
            logging.error(f"Ошибка при удалении участника: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/visits/<int:participant_id>', methods=['GET'])
    def get_visits(participant_id):
        """Получение всех посещений конкретного участника по его ID."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT arrival_time FROM visits WHERE participant_id = ?', (participant_id,))
            rows = cursor.fetchall()
            visits = [{"arrival_time": row["arrival_time"]} for row in rows]

            conn.close()

            if visits:
                # Преобразование даты в строковый формат ISO
                for visit in visits:
                    visit["arrival_time"] = visit["arrival_time"]
                return jsonify({"visits": visits}), 200
            else:
                return jsonify({"message": "No visits found for this participant."}), 404
        except Exception as e:
            logging.error(f"Ошибка при получении посещений: {e}")
            return jsonify({"error": str(e)}), 500

    # CRUD маршруты для QA (вопрос-ответ)

    @app.route('/api/qa', methods=['POST'])
    def create_qa():
        """Создание новой пары вопрос-ответ."""
        global audiod
        try:
            data = request.get_json()
            question = data.get('question')
            answer = data.get('answer')

            if not question or not answer:
                return jsonify({"error": "Question and answer are required."}), 400

            conn = get_db_connection()
            cursor = conn.cursor()
            fn = generate_unique_filename(answer)
            filename = f"{fn}.mp3"  # Имя файла без пути
            path = os.path.join("./audio/files", filename)

            # Добавление озвучки ответа
            tts.tts_to_file(text=answer,
                            speaker_wav="./audio/files/example_04_real.wav",
                            language="ru",
                            file_path=path,
                            speed=1.15)

            # Добавляем аудио путь в JSON
            audio_data_file = "audio/audio_data.json"
            if os.path.exists(audio_data_file):
                with open(audio_data_file, 'r', encoding='utf-8') as file:
                    audio_data = json.load(file)
            else:
                audio_data = {}

            audio_data[answer] = filename  # Сохраняем только имя файла

            with open(audio_data_file, 'w', encoding='utf-8') as file:
                # Перезаписываем JSON файл
                json.dump(audio_data, file, ensure_ascii=False, indent=4)
            audiod = load_audio_data()
            # Добавляем новую QA пару в базу данных
            cursor.execute('INSERT INTO qa (question, answer) VALUES (?, ?)', (question, answer))
            conn.commit()
            qa_id = cursor.lastrowid
            conn.close()

            return jsonify({"message": "QA pair created successfully.", "id": qa_id}), 201
        except Exception as e:
            logging.error(f"Ошибка при создании QA пары: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/qa', methods=['GET'])
    def get_all_qa():
        """Получение всех пар вопрос-ответ с путями к аудио файлам."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM qa')
            rows = cursor.fetchall()

            # Загрузка данных из audio_data.json
            audio_data_file = "audio/audio_data.json"
            if os.path.exists(audio_data_file):
                with open(audio_data_file, 'r', encoding='utf-8') as file:
                    audio_data = json.load(file)
            else:
                audio_data = {}

            qa_list = []
            for row in rows:
                answer = row["answer"]
                audio_path = audio_data.get(answer, "")  # Получение пути к аудио файлу по ответу
                qa_list.append({
                    "id": row["id"],
                    "question": row["question"],
                    "answer": answer,
                    "audio_path": audio_path
                })

            conn.close()

            return jsonify({"qa": qa_list}), 200
        except Exception as e:
            logging.error(f"Ошибка при получении QA пар: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/qa/<int:qa_id>', methods=['GET'])
    def get_qa(qa_id):
        """Получение конкретной пары вопрос-ответ по ID."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM qa WHERE id = ?', (qa_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                answer = row["answer"]
                audio_data_file = "audio/audio_data.json"
                if os.path.exists(audio_data_file):
                    with open(audio_data_file, 'r', encoding='utf-8') as file:
                        audio_data = json.load(file)
                else:
                    audio_data = {}
                audio_path = audio_data.get(answer, "")
                qa = {
                    "id": row["id"],
                    "question": row["question"],
                    "answer": answer,
                    "audio_path": audio_path
                }
                return jsonify({"qa": qa}), 200
            else:
                return jsonify({"message": "QA pair not found."}), 404
        except Exception as e:
            logging.error(f"Ошибка при получении QA пары: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/qa/<int:qa_id>', methods=['PUT'])
    def update_qa(qa_id):
        """Обновление пары вопрос-ответ по ID."""
        try:
            data = request.get_json()
            question = data.get('question')
            answer = data.get('answer')

            if not question and not answer:
                return jsonify({"error": "At least one of question or answer must be provided for update."}), 400

            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем текущую QA пару
            cursor.execute('SELECT * FROM qa WHERE id = ?', (qa_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return jsonify({"message": "QA pair not found."}), 404

            current_answer = row["answer"]

            # Обновляем вопрос и/или ответ
            if question and answer:
                question = clean_text(question)
                answer = clean_text(answer)
                cursor.execute('UPDATE qa SET question = ?, answer = ? WHERE id = ?', (question, answer, qa_id))
            elif question:
                question = clean_text(question)
                cursor.execute('UPDATE qa SET question = ? WHERE id = ?', (question, qa_id))
            elif answer:
                answer = clean_text(answer)
                cursor.execute('UPDATE qa SET answer = ? WHERE id = ?', (answer, qa_id))

            # Если ответ был изменён, обновляем аудио файл
            if answer and answer != current_answer:
                # Удаляем старый аудио файл, если он существует
                old_audio_path = audiod.get(current_answer, "")
                if old_audio_path:
                    old_file = os.path.join("./audio/files", old_audio_path)
                    if os.path.exists(old_file):
                        os.remove(old_file)

                # Генерация нового аудио файла для нового ответа
                new_audio_filename = f"{answer}.mp3"
                new_audio_path = os.path.join("./audio/files", new_audio_filename)
                tts.tts_to_file(text=answer,
                                speaker_wav="./audio/files/example_04_real.wav",
                                language="ru",
                                file_path=new_audio_path,
                                speed=1.15)

                # Обновляем audio_data.json
                audio_data_file = "audio/audio_data.json"
                if os.path.exists(audio_data_file):
                    with open(audio_data_file, 'r', encoding='utf-8') as file:
                        audio_data = json.load(file)
                else:
                    audio_data = {}

                audio_data[answer] = new_audio_filename
                # Удаляем старый ключ, если существовал
                if current_answer in audio_data:
                    del audio_data[current_answer]

                with open(audio_data_file, 'w', encoding='utf-8') as file:
                    json.dump(audio_data, file, ensure_ascii=False, indent=4)

            conn.commit()
            conn.close()

            return jsonify({"message": "QA pair updated successfully."}), 200
        except Exception as e:
            logging.error(f"Ошибка при обновлении QA пары: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/api/qa/<int:qa_id>', methods=['DELETE'])
    def delete_qa(qa_id):
        """Удаление пары вопрос-ответ по ID."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Получаем QA пару для удаления аудио файла
            cursor.execute('SELECT * FROM qa WHERE id = ?', (qa_id,))
            row = cursor.fetchone()
            if not row:
                conn.close()
                return jsonify({"message": "QA pair not found."}), 404

            answer = row["answer"]

            # Удаляем аудио файл
            audio_data_file = "audio/audio_data.json"
            if os.path.exists(audio_data_file):
                with open(audio_data_file, 'r', encoding='utf-8') as file:
                    audio_data = json.load(file)
            else:
                audio_data = {}

            audio_path = audio_data.get(answer, "")
            if audio_path:
                file_to_delete = os.path.join("./audio/files", audio_path)
                if os.path.exists(file_to_delete):
                    os.remove(file_to_delete)
                # Удаляем запись из audio_data.json
                del audio_data[answer]
                with open(audio_data_file, 'w', encoding='utf-8') as file:
                    json.dump(audio_data, file, ensure_ascii=False, indent=4)

            # Удаляем QA пару из базы данных
            cursor.execute('DELETE FROM qa WHERE id = ?', (qa_id,))

            conn.commit()
            conn.close()

            return jsonify({"message": "QA pair deleted successfully."}), 200
        except Exception as e:
            logging.error(f"Ошибка при удалении QA пары: {e}")
            return jsonify({"error": str(e)}), 500
