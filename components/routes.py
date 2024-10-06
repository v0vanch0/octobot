# routes.py
import io
import numpy as np
import soundfile as sf
from TTS.api import TTS
from flask import request, jsonify, send_file
import cv2  # Добавлено для обработки изображений

from components.face_rec import shape_predictor, face_rec_model, face_detector
from components.utils import get_db_connection, record_visit
from components.voice_recognition import find_best_matching_question

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").cuda()


def register_routes(app):
    """Функция для регистрации маршрутов приложения Flask."""

    @app.route('/api/add_fingerprint', methods=['POST'])
    def add_fingerprint():
        """Добавление нового участника с изображением лица."""
        try:
            # Получение изображения лица из запроса
            image_file = request.files.get('image')
            name = request.form.get('name')

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

                # Преобразуем бинарные данные обратно в массив
                stored_fingerprint = np.frombuffer(stored_fingerprint, dtype=np.float64)
                distance = np.linalg.norm(stored_fingerprint - face_embedding)
                if distance < 0.6:  # Задаем порог для сравнения
                    conn.close()
                    return jsonify({"message": f"Participant {participant['name']} already exists."}), 409

            # Если участник не найден, добавляем его
            cursor.execute('INSERT INTO participants (name, face_embedding) VALUES (?, ?)', (name, fingerprint_bytes))
            conn.commit()
            conn.close()

            return jsonify({"message": f"Participant {name} added successfully."}), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Возвращаем ошибку как JSON

    @app.route('/api/compare_fingerprint', methods=['POST'])
    def compare_fingerprint():
        """Сравнение отпечатка лица с изображением."""
        try:
            # Получение изображения лица из запроса
            image_file = request.files.get('image')

            if not image_file:
                return jsonify({"error": "Image file is required."}), 400

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

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM participants')
            participants = cursor.fetchall()
            conn.close()
            recognized_participant = None
            for participant in participants:
                stored_fingerprint = participant['face_embedding']

                # Преобразуем бинарные данные обратно в массив
                stored_fingerprint = np.frombuffer(stored_fingerprint, dtype=np.float64)
                distance = np.linalg.norm(stored_fingerprint - face_embedding)
                if distance < 0.6:  # Задаем порог для сравнения
                    recognized_participant = participant
                    break

            if recognized_participant:
                return jsonify({"message": f"Participant {recognized_participant['name']} recognized."}), 200
            else:
                return jsonify({"message": "No match found."}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Возвращаем ошибку как JSON

    @app.route('/api/voice_recognition', methods=['POST'])
    def voice_recognition_route():
        """Обработка текста и нахождение лучшего вопроса с использованием нечёткого поиска."""
        data = request.get_json()

        # Проверяем наличие поля transcript
        transcript = data.get('transcript', None)
        if not transcript:
            return jsonify({"error": "Transcript is required."}), 400

        # Поиск лучшего совпадения
        best_match = find_best_matching_question(transcript)

        if best_match:
            return jsonify({
                "question": best_match['question'],
                "answer": best_match['answer'],
                "similarity": "high"
            }), 200
        else:
            return jsonify({"message": "No similar question found."}), 404

    @app.route('/api/voice_answer', methods=['POST'])
    def voice_answer_route():
        """Обработка текста, нахождение лучшего вопроса и голосовой ответ с использованием TTS."""
        data = request.get_json()

        # Проверяем наличие поля transcript
        transcript = data.get('transcript', None)
        if not transcript:
            return jsonify({"error": "Transcript is required."}), 400

        # Поиск лучшего совпадения
        best_match = find_best_matching_question(transcript)

        if best_match:
            # Генерация аудио ответа с помощью TTS
            answer = best_match['answer']
            try:
                audio_array = tts.tts(text=answer, speaker_wav="video5460965958115940537.wav", language="en")
            except Exception as tts_error:
                return jsonify({"error": f"TTS synthesis failed: {str(tts_error)}"}), 500

            # Преобразование numpy массива в байты (в формате WAV)
            audio_stream = io.BytesIO()
            sf.write(audio_stream, audio_array, 22050, format='WAV')  # Частота дискретизации 22050 Hz
            audio_stream.seek(0)

            # Возвращаем аудио файл как ответ
            return send_file(audio_stream, mimetype='audio/wav', as_attachment=True, download_name='response.wav')

        else:
            return jsonify({"message": "No similar question found."}), 404

    @app.route('/api/face_recognition_greeting', methods=['POST'])
    def face_recognition_greeting():
        """Распознавание лица, приветствие и запись визита."""
        try:
            # Получение файла изображения из запроса
            image_file = request.files.get('image')

            if not image_file:
                return jsonify({"error": "Image file is required."}), 400

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

            # Поиск участника по отпечатку лица
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM participants')
            participants = cursor.fetchall()
            conn.close()

            recognized_participant = None
            for participant in participants:
                stored_fingerprint = participant['face_embedding']
                stored_fingerprint = np.frombuffer(stored_fingerprint, dtype=np.float64)
                distance = np.linalg.norm(stored_fingerprint - face_embedding)
                if distance < 0.6:
                    recognized_participant = participant
                    break

            if recognized_participant is None:
                return jsonify({"message": "No matching participant found."}), 404

            # Приветствие участника с использованием TTS
            greeting_text = f"Hello, {recognized_participant['name']}! Welcome back!"
            try:
                audio_array = tts.tts(text=greeting_text, speaker_wav="video5460965958115940537.wav", language="en")
            except Exception as tts_error:
                return jsonify({"error": f"TTS synthesis failed: {str(tts_error)}"}), 500

            # Преобразование numpy массива в байты (в формате WAV)
            audio_stream = io.BytesIO()
            sf.write(audio_stream, audio_array, 22050, format='WAV')
            audio_stream.seek(0)

            # Запись визита участника в базу данных
            record_visit(recognized_participant['id'])

            # Возвращаем аудио файл как ответ
            return send_file(audio_stream, mimetype='audio/wav', as_attachment=True, download_name='greeting.wav')

        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Возвращаем ошибку как JSON
