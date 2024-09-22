import sqlite3
import numpy as np
from components.utils import get_db_connection


# Модель участника (пользователя)
def add_participant(name, fingerprint):
    """Добавление нового участника в таблицу participants."""
    fingerprint_str = ','.join(map(str, fingerprint))  # Преобразуем массив в строку
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO participants (name, face_embedding)
        VALUES (?, ?)
    ''', (name, fingerprint_str))
    conn.commit()
    conn.close()


def get_participant_by_fingerprint(fingerprint):
    """Получение участника по отпечатку."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM participants')
    participants = cursor.fetchall()

    recognized_participant = None
    fingerprint = np.array(fingerprint)

    for participant in participants:
        stored_fingerprint = np.fromstring(participant['face_embedding'], sep=',')
        distance = np.linalg.norm(stored_fingerprint - fingerprint)
        if distance < 0.6:  # Задаем порог для сравнения
            recognized_participant = participant
            break

    conn.close()
    return recognized_participant


def get_all_participants():
    """Получение всех участников."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM participants')
    participants = cursor.fetchall()
    conn.close()
    return participants


# Модель визита участника
def add_visit(participant_id, arrival_time):
    """Добавление нового визита участника."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO visits (participant_id, arrival_time)
        VALUES (?, ?)
    ''', (participant_id, arrival_time))
    conn.commit()
    conn.close()


def update_departure_time(participant_id, departure_time):
    """Обновление времени ухода участника."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE visits
        SET departure_time = ?
        WHERE participant_id = ? AND departure_time IS NULL
    ''', (departure_time, participant_id))
    conn.commit()
    conn.close()


def get_ongoing_visit(participant_id):
    """Получение текущего визита участника."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM visits
        WHERE participant_id = ? AND departure_time IS NULL
    ''', (participant_id,))
    visit = cursor.fetchone()
    conn.close()
    return visit


# Модель вопрос-ответ (QA)
def add_qa_entry(question, answer):
    """Добавление новой записи вопрос-ответ."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO qa (question, answer)
        VALUES (?, ?)
    ''', (question, answer))
    conn.commit()
    conn.close()


def get_qa_by_id(qa_id):
    """Получение записи вопрос-ответ по ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM qa WHERE id = ?', (qa_id,))
    qa_entry = cursor.fetchone()
    conn.close()
    return qa_entry


def get_all_qa():
    """Получение всех записей вопрос-ответ."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM qa')
    qa_entries = cursor.fetchall()
    conn.close()
    return qa_entries
