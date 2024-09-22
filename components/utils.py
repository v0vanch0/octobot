import sqlite3
from datetime import datetime


def get_db_connection():
    """Подключение к базе данных SQLite."""
    conn = sqlite3.connect('database/octobot.db')
    conn.row_factory = sqlite3.Row  # Возвращает строки в виде словаря
    return conn


def create_tables():
    """Создает таблицы участников, визитов и вопросов-ответов, если они не существуют и добавляет тестовые данные."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица участников
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            face_embedding TEXT NOT NULL  -- Теперь хранится отпечаток в виде строки
        )
    ''')

    # Таблица визитов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id INTEGER NOT NULL,
            arrival_time TEXT,
            FOREIGN KEY (participant_id) REFERENCES participants (id)
        )
    ''')

    # Таблица вопросов и ответов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS qa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    ''')

    # Добавление тестовых данных, если таблица пуста
    cursor.execute('SELECT COUNT(*) FROM qa')
    if cursor.fetchone()[0] == 0:
        qa_data = [
            ('Как узнать погоду?', 'Вы можете узнать погоду, сказав команду "Узнать погоду".'),
            ('Какая сегодня дата?', 'Сегодняшняя дата выводится по команде "Какая сегодня дата?".'),
            ('Как запустить программу?', 'Запустите программу командой "Запуск программы".')
        ]
        cursor.executemany('INSERT INTO qa (question, answer) VALUES (?, ?)', qa_data)

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
