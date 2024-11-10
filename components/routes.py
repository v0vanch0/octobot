# routes.py
from datetime import datetime
import json
import os

import numpy as np
from flask import request, jsonify
import cv2  # Для обработки изображений
from audio.audio_data import audiod
from components.face_rec import shape_predictor, face_rec_model, face_detector
from components.utils import get_db_connection
from components.voice_recognition import find_best_matching_question
from TTS.api import TTS

# Инициализация TTS модели
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").cuda()


def register_routes(app):
    """Функция для регистрации маршрутов приложения Flask."""

    text = "Пока что я не знаю ответа на этот вопрос"
    aud_file = "./audio/files/dont_know.mp3"
    tts.tts_to_file(text=text,
                    speaker_wav="./audio/files/example_04_real.wav",
                    language="ru",
                    file_path=aud_file,
                    speed=1.15)

    # Добавляем персональное приветствие в JSON
    audio_data_file = "audio/audio_data.json"
    with open(audio_data_file, 'r', encoding='utf-8') as file:
        audio_data = json.load(file)


    audio_data['no similar'] = os.path.abspath(aud_file)


    with open(audio_data_file, 'w', encoding='utf-8') as file:
        # Перезаписываем JSON файл
        json.dump(audio_data, file, ensure_ascii=False, indent=4)

    @app.route('/api/add_fingerprint', methods=['POST'])
    def add_fingerprint():
        """Добавление нового участника с изображением лица и персональным приветствием."""
        try:
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
                if distance < 0.6:  # Задаем порог для сравнения
                    conn.close()
                    return jsonify({"message": f"Participant {participant['name']} already exists."}), 409

            # Генерация персонального приветствия с использованием TTS
            greeting_text = f"Здравствуйте, {name}!"
            greeting_file = f"./audio/files/{name}_greeting.mp3"
            tts.tts_to_file(text=greeting_text,
                            speaker_wav="./audio/files/example_04_real.wav",
                            language="ru",
                            file_path=greeting_file,
                            speed=1.15)

            # Добавляем персональное приветствие в JSON
            audio_data_file = "audio/audio_data.json"
            with open(audio_data_file, 'r', encoding='utf-8') as file:
                audio_data = json.load(file)

            if personal_greeting:
                # Сохраняем путь к персональному приветствию
                audio_data[personal_greeting] = os.path.abspath(greeting_file)
            else:
                # Сохраняем стандартное приветствие
                audio_data[f"Приветствие для {name}"] = os.path.abspath(greeting_file)

            with open(audio_data_file, 'w', encoding='utf-8') as file:
                # Перезаписываем JSON файл
                json.dump(audio_data, file, ensure_ascii=False, indent=4)

            # Добавляем нового участника в базу данных
            cursor.execute('INSERT INTO participants (name, face_embedding) VALUES (?, ?)',
                           (name, fingerprint_bytes))
            conn.commit()
            conn.close()

            return jsonify({"message": f"Participant {name} added successfully."}), 201

        except Exception as e:
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
            return jsonify({"answer": "Пока я не знаю ответ на данных вопрос", "audio_path": audiod.get('no similar', "")}), 404

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
            print("Invalid image.")
            return jsonify({"error": "Invalid image."}), 400

        # Извлечение цифрового отпечатка лица
        faces = face_detector(image_np)

        if len(faces) == 0:
            print("No face detected in the image.")
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
            print("No matching participant found.")
            return jsonify({"message": "No matching participant found."}), 404

        # Проверка, посещал ли участник уже сегодня
        participant_id = recognized_participant['id']
        today = datetime.now().date()
        cursor.execute('SELECT * FROM visits WHERE participant_id = ? AND DATE(arrival_time) = ?',
                       (participant_id, today))

        visit_today = cursor.fetchone()

        if visit_today:
            conn.close()
            print("Visitor has already visited today.")
            return jsonify({"message": "Visitor has already visited today."}), 200

        # Приветствие участника с использованием персонального приветствия
        participant_name = recognized_participant['name']
        audio_data_file = "audio/audio_data.json"

        # Загрузка файла с аудиопутями
        with open(audio_data_file, 'r', encoding='utf-8') as file:
            audio_data = json.load(file)

        # Проверяем, есть ли персональное приветствие для участника
        greeting_text = f"Приветствие для {participant_name}"
        greeting_path = audio_data.get(greeting_text, audio_data.get('Доброго времени суток!', ""))

        # Запись визита в базу данных
        cursor.execute('INSERT INTO visits (participant_id, arrival_time) VALUES (?, ?)',
                       (participant_id, datetime.now()))
        conn.commit()
        conn.close()

        # Возвращаем путь к аудио файлу приветствия
        print("audio_path")
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
            return jsonify({"error": str(e)}), 500

    # CRUD маршруты для QA (вопрос-ответ)

    @app.route('/api/qa', methods=['POST'])
    def create_qa():
        """Создание новой пары вопрос-ответ."""
        try:
            data = request.get_json()
            question = data.get('question')
            answer = data.get('answer')

            if not question or not answer:
                return jsonify({"error": "Question and answer are required."}), 400

            conn = get_db_connection()
            cursor = conn.cursor()
            path = "./audio/files/" + answer + ".mp3"
            cursor.execute('INSERT INTO qa (question, answer) VALUES (?, ?)', (question, answer))
            path = "./audio/files/" + answer + ".mp3"
            # Добавление озвучки ответа
            tts.tts_to_file(text=answer,
                            speaker_wav="./audio/files/example_04_real.wav",
                            language="ru",
                            file_path=path,
                            speed=1.15)

            # Добавляем персональное приветствие в JSON
            audio_data_file = "audio/audio_data.json"
            with open(audio_data_file, 'r', encoding='utf-8') as file:
                audio_data = json.load(file)

            if answer:
                # Сохраняем путь к персональному приветствию
                audio_data[answer] = os.path.abspath(path)

            with open(audio_data_file, 'w', encoding='utf-8') as file:
                # Перезаписываем JSON файл
                json.dump(audio_data, file, ensure_ascii=False, indent=4)

            conn.commit()
            qa_id = cursor.lastrowid
            conn.close()

            return jsonify({"message": "QA pair created successfully.", "id": qa_id}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/qa', methods=['GET'])
    def get_all_qa():
        """Получение всех пар вопрос-ответ."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM qa')
            rows = cursor.fetchall()
            qa_list = [{"id": row["id"], "question": row["question"], "answer": row["answer"]} for row in rows]

            conn.close()

            return jsonify({"qa": qa_list}), 200
        except Exception as e:
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
                qa = {"id": row["id"], "question": row["question"], "answer": row["answer"]}
                return jsonify({"qa": qa}), 200
            else:
                return jsonify({"message": "QA pair not found."}), 404
        except Exception as e:
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

            if question and answer:
                cursor.execute('UPDATE qa SET question = ?, answer = ? WHERE id = ?', (question, answer, qa_id))
            elif question:
                cursor.execute('UPDATE qa SET question = ? WHERE id = ?', (question, qa_id))
            elif answer:
                cursor.execute('UPDATE qa SET answer = ? WHERE id = ?', (answer, qa_id))

            conn.commit()
            conn.close()

            if cursor.rowcount > 0:
                return jsonify({"message": "QA pair updated successfully."}), 200
            else:
                return jsonify({"message": "QA pair not found."}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/qa/<int:qa_id>', methods=['DELETE'])
    def delete_qa(qa_id):
        """Удаление пары вопрос-ответ по ID."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM qa WHERE id = ?', (qa_id,))
            conn.commit()
            conn.close()

            if cursor.rowcount > 0:
                return jsonify({"message": "QA pair deleted successfully."}), 200
            else:
                return jsonify({"message": "QA pair not found."}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
