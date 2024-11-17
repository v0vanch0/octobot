from flask import Flask
from flask_cors import CORS

from components.routes import register_routes
from components.utils import create_tables
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from components.routes import delete_old_visits, export_visits_to_excel


def schedule_tasks():
    scheduler = BackgroundScheduler()

    # Запланировать ежедневное выполнение задач
    scheduler.add_job(func=perform_daily_tasks, trigger="cron", hour=0, minute=0)
    scheduler.start()


def perform_daily_tasks():
    print(f"Выполнение задач: {datetime.now()}")
    try:
        # Экспорт данных в Excel
        export_visits_to_excel()
        print("Экспорт посещений завершен.")

        # Удаление старых посещений
        delete_old_visits()
        print("Удаление старых посещений завершено.")
    except Exception as e:
        print(f"Ошибка при выполнении задач: {e}")


# Инициализация приложения Flask
app = Flask(__name__)

# Регистрируем маршруты
register_routes(app)

# Создаем таблицы, если они не существуют
create_tables()

if __name__ == '__main__':
    schedule_tasks()
    CORS(app)
    app.run(debug=False, host="0.0.0.0")
