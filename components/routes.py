import io
import sqlite3
import numpy as np
from TTS.api import TTS
from flask import request, jsonify, send_file
from components.utils import get_db_connection, record_visit
from components.voice_recognition import find_best_matching_question
import soundfile as sf

tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").cuda().bfloat16()

def register_routes(app):
    """Функция для регистрации маршрутов приложения Flask."""

    @app.route('/api/add_fingerprint', methods=['POST'])
    def add_fingerprint():
        """Добавление нового участника с отпечатком."""
        name = request.json.get('name')
        fingerprint = request.json.get('fingerprint')  # Принимаем массив из 128 чисел

        if not name or not fingerprint:
            return jsonify({"error": "Name and fingerprint are required."}), 400

        if len(fingerprint) != 128:
            return jsonify({"error": "Fingerprint must be an array of 128 numbers."}), 400

        # Преобразуем массив в бинарные данные для хранения
        fingerprint_bytes = np.array(fingerprint, dtype=np.float64).tobytes()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли участник с таким же отпечатком
        cursor.execute('SELECT * FROM participants')
        participants = cursor.fetchall()

        for participant in participants:
            stored_fingerprint = participant['face_embedding']

            # Преобразуем бинарные данные обратно в массив
            stored_fingerprint = np.frombuffer(stored_fingerprint, dtype=np.float64)
            distance = np.linalg.norm(stored_fingerprint - np.array(fingerprint))
            if distance < 0.6:  # Задаем порог для сравнения
                conn.close()
                return jsonify({"message": f"Participant {participant['name']} already exists."}), 409

        # Если участник не найден, добавляем его
        cursor.execute('INSERT INTO participants (name, face_embedding) VALUES (?, ?)', (name, fingerprint_bytes))
        conn.commit()
        conn.close()

        return jsonify({"message": f"Participant {name} added successfully."}), 201

    @app.route('/api/compare_fingerprint', methods=['POST'])
    def compare_fingerprint():
        """Сравнение отпечатков."""
        try:
            fingerprint = request.json.get('fingerprint')  # Принимаем массив из 128 чисел

            if not fingerprint:
                return jsonify({"error": "Fingerprint is required."}), 400

            if len(fingerprint) != 128:
                return jsonify({"error": "Fingerprint must be an array of 128 numbers."}), 400

            fingerprint = np.array(fingerprint, dtype=np.float64)  # Преобразуем в numpy массив для сравнения

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM participants')
            participants = cursor.fetchall()

            recognized_participant = None
            for participant in participants:
                stored_fingerprint = participant['face_embedding']

                # Преобразуем бинарные данные обратно в массив
                stored_fingerprint = np.frombuffer(stored_fingerprint, dtype=np.float64)
                distance = np.linalg.norm(stored_fingerprint - fingerprint)
                if distance < 0.6:  # Задаем порог для сравнения
                    recognized_participant = participant
                    break

            if recognized_participant:
                return jsonify({"message": f"Participant {recognized_participant['name']} recognized."}), 200
            else:
                return jsonify({"message": "No match found."}), 404

            conn.close()

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
            audio_array = tts.tts(text=answer, speaker_wav="video5460965958115940537.wav", language="en")  # Синтезируем голос и получаем numpy массив

            # Преобразуем numpy массив в байты (в формате WAV)
            audio_stream = io.BytesIO()
            sf.write(audio_stream, audio_array, 22050, format='WAV')  # Частота дискретизации 22050 Hz
            audio_stream.seek(0)

            # Возвращаем аудио файл как ответ
            return send_file(audio_stream, mimetype='audio/wav', as_attachment=True, download_name='response.wav')

        else:
            return jsonify({"message": "No similar question found."}), 404
