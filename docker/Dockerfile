# Используем официальный образ Python 3.10
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . .

# Открываем порт для работы приложения
EXPOSE 5000

# Команда для запуска приложения
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
