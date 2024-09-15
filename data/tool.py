import sqlite3
from config import QUESTIONS_DATABASE_PATH


def add_question_answer(connection, question, answer):
    """
    Добавляет вопрос и ответ в базу данных.
    """
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO qa (question, answer) VALUES (?, ?)", (question, answer)
    )
    connection.commit()
    print(f"Вопрос '{question}' с ответом '{answer}' успешно добавлен!")


def main():
    """
    Основная функция программы.
    """
    connection = sqlite3.connect("qa.db")

    while True:
        question = input("Введите вопрос (или 'q' для выхода): ")
        if question.lower() == "q":
            break

        answer = input("Введите ответ: ")
        add_question_answer(connection, question, answer)

    connection.close()


if __name__ == "__main__":
    main()
