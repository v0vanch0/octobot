from fuzzywuzzy import fuzz
from components.models import get_all_qa


def find_best_matching_question(transcript):
    """Ищет лучший соответствующий вопрос в базе данных с использованием нечёткого поиска."""
    # Получаем список всех записей QA из базы данных
    qa_list = get_all_qa()

    best_match = None
    highest_ratio = 0

    # Ищем вопрос с наибольшим совпадением
    for qa in qa_list:
        ratio = fuzz.ratio(qa['question'].lower(), transcript.lower())
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = qa

    # Возвращаем запись вопроса и ответа, если точность выше порога
    return best_match if highest_ratio > 70 else None
