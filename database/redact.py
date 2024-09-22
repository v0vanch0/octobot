import sqlite3

DB_PATH = 'octobot.db'  # Путь к базе данных


def get_db_connection():
    """Устанавливает подключение к базе данных."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def show_participants():
    """Выводит список всех участников."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM participants')
    participants = cursor.fetchall()
    conn.close()

    if participants:
        print("\nУчастники:")
        for participant in participants:
            print(f"ID: {participant['id']}, Имя: {participant['name']}")
    else:
        print("\nВ базе данных нет участников.")


def show_visits():
    """Выводит список всех визитов."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM visits')
    visits = cursor.fetchall()
    conn.close()

    if visits:
        print("\nВизиты:")
        for visit in visits:
            print(f"ID: {visit['id']}, ID участника: {visit['participant_id']}, Время прихода: {visit['arrival_time']}, Время ухода: {visit['departure_time']}")
    else:
        print("\nВ базе данных нет визитов.")


def show_questions_answers():
    """Выводит список всех вопросов и ответов."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM qa')
    qa_entries = cursor.fetchall()
    conn.close()

    if qa_entries:
        print("\nВопросы и ответы:")
        for entry in qa_entries:
            print(f"ID: {entry['id']}, Вопрос: {entry['question']}, Ответ: {entry['answer']}")
    else:
        print("\nВ базе данных нет вопросов и ответов.")


def add_question_answer():
    """Добавляет новый вопрос и ответ в базу данных с циклом для продолжения."""
    while True:
        question = input("Введите вопрос: ").lower()
        answer = input("Введите ответ: ").lower()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO qa (question, answer) VALUES (?, ?)', (question, answer))
        conn.commit()
        conn.close()

        print("\nНовый вопрос-ответ успешно добавлен.")

        # Предложить добавить еще один вопрос или выйти
        more = input("Хотите добавить еще один вопрос? (y/n): ").strip().lower()
        if more != 'y':
            break


def delete_question_answer():
    """Удаляет вопрос-ответ по ID."""
    while True:
        qa_id = input("Введите ID вопроса-ответа для удаления: ")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM qa WHERE id = ?', (qa_id,))
        conn.commit()
        conn.close()

        print(f"\nВопрос-ответ с ID {qa_id} успешно удален.")

        # Предложить удалить еще один вопрос или выйти
        more = input("Хотите удалить еще один вопрос? (y/n): ").strip().lower()
        if more != 'y':
            break


def update_question_answer():
    """Обновляет существующий вопрос и/или ответ с циклом для продолжения."""
    while True:
        qa_id = input("Введите ID вопроса-ответа для обновления: ")
        new_question = input("Введите новый вопрос (оставьте пустым для сохранения старого): ")
        new_answer = input("Введите новый ответ (оставьте пустым для сохранения старого): ")

        conn = get_db_connection()
        cursor = conn.cursor()

        if new_question:
            cursor.execute('UPDATE qa SET question = ? WHERE id = ?', (new_question, qa_id))
        if new_answer:
            cursor.execute('UPDATE qa SET answer = ? WHERE id = ?', (new_answer, qa_id))

        conn.commit()
        conn.close()

        print(f"\nВопрос-ответ с ID {qa_id} успешно обновлен.")

        # Предложить обновить еще один вопрос или выйти
        more = input("Хотите обновить еще один вопрос? (y/n): ").strip().lower()
        if more != 'y':
            break


def show_menu():
    """Показывает меню для управления базой данных."""
    while True:
        print("\nМеню управления базой данных:")
        print("1. Показать участников")
        print("2. Показать визиты")
        print("3. Показать вопросы и ответы")
        print("4. Добавить вопрос-ответ")
        print("5. Удалить вопрос-ответ")
        print("6. Обновить вопрос-ответ")
        print("7. Выход")

        choice = input("Выберите действие (1-7): ")

        if choice == '1':
            show_participants()
        elif choice == '2':
            show_visits()
        elif choice == '3':
            show_questions_answers()
        elif choice == '4':
            add_question_answer()
        elif choice == '5':
            delete_question_answer()
        elif choice == '6':
            update_question_answer()
        elif choice == '7':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Пожалуйста, выберите действие от 1 до 7.")


if __name__ == '__main__':
    show_menu()
