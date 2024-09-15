from flask import Flask

from components.routes import register_routes
from components.utils import create_tables

# Инициализация приложения Flask
app = Flask(__name__)

# Регистрируем маршруты
register_routes(app)

# Создаем таблицы, если они не существуют
create_tables()

if __name__ == '__main__':
    app.run(debug=True)
