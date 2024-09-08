import sqlite3
import pickle
import numpy as np
from face_recognition_custom import face_recognition_utils
import time
from config import DATABASE_PATH, QUESTIONS_DATABASE_PATH # Импортируем пути к базам данных
from flask import g  # Импортируем g из Flask

class DatabaseConnector:
    def __init__(self):
        self.participants_db_path = DATABASE_PATH
        self.questions_db_path = QUESTIONS_DATABASE_PATH

    def get_participants_db(self):
        """
        Возвращает соединение с базой данных participants.
        Создает новое соединение, если оно не существует в g.
        """
        if 'participants_db' not in g:
            g.participants_db = sqlite3.connect(self.participants_db_path)
            self.create_participants_tables(g.participants_db)
        return g.participants_db

    def get_questions_db(self):
        """
        Возвращает соединение с базой данных questions.
        Создает новое соединение, если оно не существует в g.
        """
        if 'questions_db' not in g:
            g.questions_db = sqlite3.connect(self.questions_db_path)
            self.create_questions_tables(g.questions_db)
        return g.questions_db

    def close_db(self, exception=None):
        """
        Закрывает соединения с базами данных.
        """
        db = g.pop('participants_db', None)
        if db is not None:
            db.close()
        db = g.pop('questions_db', None)
        if db is not None:
            db.close()

    def create_participants_tables(self, connection):
        """
        Создает таблицы Participants и Visits.
        """
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                face_embedding BLOB NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id INTEGER NOT NULL,
                arrival_time TEXT,
                departure_time TEXT,
                FOREIGN KEY (participant_id) REFERENCES participants (id)
            )
        ''')
        connection.commit()

    def create_questions_tables(self, connection):
        """
        Создает таблицу qa.
        """
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        ''')
        connection.commit()

    def add_participant(self, name, face_embedding):
        """
        Добавляет нового участника в базу данных.
        """
        cursor = self.participants_connection.cursor()
        cursor.execute('''
            INSERT INTO participants (name, face_embedding)
            VALUES (?, ?)
        ''', (name, pickle.dumps(face_embedding)))
        self.participants_connection.commit()
        return cursor.lastrowid

    def get_participant_by_face_embedding(self, face_embedding, threshold=0.6):
        """
        Получает информацию об участнике по эмбеддингу лица.

        Args:
            face_embedding: Эмбеддинг лица.
            threshold: Порог схожести для определения совпадения лиц.

        Returns:
            Словарь с информацией об участнике или None, если участник не найден.
        """
        cursor = self.participants_connection.cursor()
        cursor.execute("SELECT * FROM participants")
        rows = cursor.fetchall()

        for row in rows:
            stored_embedding = pickle.loads(row[2])
            similarity = face_recognition_utils.compare_face_embeddings(face_embedding, stored_embedding)
            if similarity >= threshold:
                return {
                    'id': row[0],
                    'name': row[1]
                }

        return None

    def register_participant_arrival(self, participant_id):
        """
        Регистрирует время прихода участника.

        Args:
            participant_id: Идентификатор участника.
        """
        cursor = self.participants_connection.cursor()
        arrival_time = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO visits (participant_id, arrival_time)
            VALUES (?, ?)
        ''', (participant_id, arrival_time))
        self.participants_connection.commit()

    def register_participant_departure(self, participant_id):
        """
        Регистрирует время ухода участника.

        Args:
            participant_id: Идентификатор участника.
        """
        cursor = self.participants_connection.cursor()
        departure_time = time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            UPDATE visits 
            SET departure_time = ?
            WHERE participant_id = ? 
            AND departure_time IS NULL  -- Обновляем только последнюю запись без времени ухода
        ''', (departure_time, participant_id))
        self.participants_connection.commit()

    def get_daily_visits(self, date=None):
        """
        Получает информацию о посещениях за день.

        Args:
            date: Дата в формате YYYY-MM-DD. Если не указана, используется текущая дата.

        Returns:
            Список словарей с информацией о посещениях за день.
        """
        if date is None:
            date = time.strftime("%Y-%m-%d")

        cursor = self.participants_connection.cursor()
        cursor.execute('''
            SELECT p.name, v.arrival_time, v.departure_time
            FROM visits v
            JOIN participants p ON v.participant_id = p.id
            WHERE v.arrival_time LIKE ?
        ''', (date + "%",))

        visits = []
        for row in cursor.fetchall():
            visits.append({
                'name': row[0],
                'arrival_time': row[1],
                'departure_time': row[2]
            })
        return visits

    def add_question_answer(self, question, answer):
        """
        Добавляет новый вопрос и ответ в базу данных questions.
        """
        cursor = self.get_questions_db().cursor() # Исправлено: используем g
        cursor.execute('''
            INSERT INTO questions (question, answer)
            VALUES (?, ?)
        ''', (question, answer))
        self.get_questions_db().commit() # Исправлено: используем g

    def get_all_questions_and_answers(self):
        """
        Получает все вопросы и ответы из базы данных qa.

        Returns:
            Словарь, где ключи - вопросы, а значения - ответы.
        """
        cursor = self.get_questions_db().cursor() # Исправлено: используем g
        cursor.execute("SELECT question, answer FROM qa")
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}

    def get_answer_by_question(self, question):
        """
        Получает ответ на вопрос из базы данных questions.

        Args:
            question: Вопрос.

        Returns:
            Ответ на вопрос или None, если вопрос не найден.
        """
        cursor = self.get_questions_db().cursor() # Исправлено: используем g
        cursor.execute('''
            SELECT answer 
            FROM qa
            WHERE question = ?
        ''', (question,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return None