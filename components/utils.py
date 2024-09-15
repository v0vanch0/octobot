import sqlite3
from datetime import datetime


def get_db_connection():
    """Подключение к базе данных SQLite."""
    conn = sqlite3.connect('database/octobot.db')
    conn.row_factory = sqlite3.Row  # Возвращает строки в виде словаря
    return conn


def create_tables():
    """Создает таблицы участников и визитов, если они не существуют."""
    conn = get_db_connection()
    cursor = conn.cursor()
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
            participant_id INTEGER,
            arrival_time TEXT NOT NULL,
            departure_time TEXT,
            FOREIGN KEY (participant_id) REFERENCES participants (id)
        )
    ''')
    conn.commit()
    conn.close()


def get_current_time():
    """Возвращает текущее время в виде строки."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def record_visit(participant_id, arrival=True):
    """Записывает время визита участника в базу данных."""
    conn = get_db_connection()
    cursor = conn.cursor()
    current_time = get_current_time()

    if arrival:
        cursor.execute('INSERT INTO visits (participant_id, arrival_time) VALUES (?, ?)',
                       (participant_id, current_time))
    else:
        cursor.execute('UPDATE visits SET departure_time = ? WHERE participant_id = ? AND departure_time IS NULL',
                       (current_time, participant_id))

    conn.commit()
    conn.close()
