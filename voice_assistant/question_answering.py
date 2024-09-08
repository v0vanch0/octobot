import spacy
import datetime


class QuestionAnswering:
    def __init__(self, database_connector):
        self.nlp = spacy.load("ru_core_news_sm")
        self.database_connector = database_connector
        self.knowledge_base = {
            "приветствие": ["Привет!", "Здравствуйте!", "Доброе утро!", "Добрый день!", "Добрый вечер!"],
            "прощание": ["До свидания!", "Пока!", "Всего доброго!", "До встречи!"],
            "кто ты": ["Я Octobot, умный помощник образовательного центра Octopus."],
            "что ты умеешь": [
                "Я могу распознавать лица, приветствовать участников, отвечать на вопросы, регистрировать посещения.",
                "Я могу рассказать вам о Octopus, о курсах, о расписании занятий.",
                "Спросите меня, что вам интересно."],
            "где находится туалет": ["Туалет находится на втором этаже."],
            "когда начинается следующий урок": ["Следующий урок начинается через 15 минут.",
                                                "Расписание занятий можно посмотреть на сайте Octopus."],
            "кто сегодня пришел": self.get_participants_who_arrived_today,  # Добавляем функцию для ответа на вопрос
            # ... другие намерения и ответы
        }

    def answer_question(self, question):
        """
        Определяет намерение вопроса и возвращает соответствующий ответ.
        """
        doc = self.nlp(question)
        for ent in doc.ents:
            if ent.label_ == "GREETING":
                return self.knowledge_base["приветствие"][0]  # Выбираем первый ответ из списка
            elif ent.label_ == "FAREWELL":
                return self.knowledge_base["прощание"][0]
        # ... обработка других намерений

        # Поиск ответа в базе данных questions
        db_answer = self.database_connector.get_answer_by_question(question)
        if db_answer:
            return db_answer

        # Поиск ответа в knowledge_base
        for intent, answer in self.knowledge_base.items():
            if intent.lower() in question.lower():
                if callable(answer):  # Проверяем, является ли ответ функцией
                    return answer()  # Вызываем функцию, если это так
                else:
                    return answer[0]  # Возвращаем первый ответ из списка, если это не функция

        return None

    def get_participants_who_arrived_today(self):
        """
        Возвращает список участников, которые пришли сегодня.
        """
        today = datetime.date.today().strftime("%Y-%m-%d")
        visits = self.database_connector.get_daily_visits(today)
        if visits:
            names = [visit['name'] for visit in visits]
            return f"Сегодня пришли: {', '.join(names)}."
        else:
            return "Сегодня пока никто не пришел."
