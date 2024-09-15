import sqlite3
import numpy as np
from flask import request, jsonify
from components.face_rec import extract_face_embedding
from components.utils import get_db_connection, record_visit
from components.voice_recognition import find_best_matching_question  # Добавляем импорт

def register_routes(app):
    """Функция для регистрации маршрутов приложения Flask."""

    @app.route('/api/recognize', methods=['POST'])
    def recognize_face_route():
        """Распознавание лица и регистрация визита."""
        file = request.files['image']
        face_embedding = extract_face_embedding(file)

        if face_embedding is None:
            return jsonify({"error": "No face found."}), 400

        # Поиск участника по эмбеддингу
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM participants')
        participants = cursor.fetchall()

        recognized_participant = None
        for participant in participants:
            db_embedding = np.frombuffer(participant['face_embedding'], dtype=np.float64)
            distance = np.linalg.norm(db_embedding - face_embedding)

            if distance < 0.6:
                recognized_participant = participant
                break

        if recognized_participant:
            participant_id = recognized_participant['id']
            cursor.execute('SELECT * FROM visits WHERE participant_id = ? AND departure_time IS NULL',
                           (participant_id,))
            ongoing_visit = cursor.fetchone()

            if ongoing_visit:
                # Если участник уходит
                record_visit(participant_id, arrival=False)
                response = {
                    "message": f"{recognized_participant['name']} left.",
                    "status": "departure"
                }
            else:
                # Если участник приходит
                record_visit(participant_id, arrival=True)
                response = {
                    "message": f"{recognized_participant['name']} arrived.",
                    "status": "arrival"
                }
        else:
            response = {"message": "No match found."}

        conn.close()
        return jsonify(response), 200

    @app.route('/api/add_participant', methods=['POST'])
    def add_participant():
        """Добавление нового участника в базу данных с проверкой на дубликаты."""
        if 'image' not in request.files:
            return jsonify({"error": "No image provided."}), 400

        file = request.files['image']
        name = request.form.get('name')

        if not file or not name:
            return jsonify({"error": "Name and image are required."}), 400

        face_embedding = extract_face_embedding(file)

        if face_embedding is None:
            return jsonify({"error": "No face found in the image."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Проверяем, существует ли участник с таким же эмбеддингом
        cursor.execute('SELECT * FROM participants')
        participants = cursor.fetchall()

        for participant in participants:
            db_embedding = np.frombuffer(participant['face_embedding'], dtype=np.float64)
            distance = np.linalg.norm(db_embedding - face_embedding)

            if distance < 0.6:
                conn.close()
                return jsonify({"message": f"Participant {participant['name']} already exists."}), 409

        # Если участник не найден, добавляем его
        embedding_bytes = sqlite3.Binary(face_embedding.tobytes())
        cursor.execute('INSERT INTO participants (name, face_embedding) VALUES (?, ?)', (name, embedding_bytes))
        conn.commit()
        conn.close()

        return jsonify({"message": f"Participant {name} added successfully."}), 201

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
