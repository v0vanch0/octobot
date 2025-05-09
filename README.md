Скриншот помощника:
![photo_5294024320693169242_w](https://github.com/user-attachments/assets/79cc1322-01b6-4157-a29a-f82a611fe020)
Панель для работы с базой:
![image](https://github.com/user-attachments/assets/9f3ff3fa-986f-4f83-bd56-49d09a1515b9)
## Структура проекта
```
/
├── app.py                    # Основной файл приложения с Flask сервером
├── .gitignore               # Список игнорируемых файлов для git
│
├── audio/                   # Директория для работы с аудио
│   ├── audio_data.json     # База данных аудио-фраз и путей
│   ├── audio_data.py       # Модуль загрузки аудио-данных
│   ├── redactor.py         # GUI-редактор аудио базы
│   └── files/              # Аудио файлы
│
├── components/             # Основные компоненты приложения
│   ├── routes.py          # Маршруты Flask приложения  
│   └── utils.py           # Вспомогательные функции
│
├── database/              # Файлы базы данных
├── dats/                 # Дополнительные данные
├── docker/               # Файлы для контейнеризации
└── examples/             # Примеры использования
```


---

### Подробная инструкция по настройке проекта

Данная инструкция поможет вам правильно настроить рабочее окружение и запустить проект.

#### 1. Клонирование репозитория
Склонируйте репозиторий на локальную машину:
```bash
git clone https://github.com/v0vanch0/octobot.git
cd octobot
```

#### 2. Настройка виртуального окружения (Python Backend)
Рекомендуется использовать виртуальное окружение для установки зависимостей.
```bash
# Создание виртуального окружения (пример для Windows)
python -m venv venv

# Активация виртуального окружения (Windows)
venv\Scripts\activate

# На Linux/Mac:
# source venv/bin/activate
```

#### 3. Установка зависимостей
Установите все необходимые пакеты:
```bash
pip install -r requirements.txt
```

#### 4. Конфигурация проекта
Убедитесь, что все файлы конфигурации находятся в нужных местах:
- Файл `audio/audio_data.json` содержит пути к аудиофайлам. При необходимости обновите пути.
- При использовании Docker, проверьте файлы из директории `docker` и настройте переменные окружения в вашем окружении.

#### 5. Настройка базы данных
При первом запуске приложения таблицы базы данных будут созданы автоматически.
Если требуется ручная настройка, выполните следующие шаги:
- Проверьте настройки подключения в файле `components/utils.py` (или в отдельных конфигурационных файлах, если они имеются).
- Убедитесь, что у вас установлены все необходимые драйверы базы данных.

#### 6. Запуск сервера Flask
Запустите сервер:
```bash
python app.py
```
Сервер будет доступен по адресу http://0.0.0.0:5000

#### 7. Запуск Frontend (Unity)
- Откройте приложение
- Укажите микрофон и камеру для взаимодействия с ассистентом
- Запустите ассистента нажав на кнопку старта
#### 8. Использование редактирования аудиофраз
Для обновления аудиофраз запустите GUI-редактор:
```bash
python audio/redactor.py
```
В редакторе можно добавлять, изменять или удалять записи, после чего данные сохранятся в `audio/audio_data.json`.

#### 9. Дополнительные настройки
- Если вы планируете контейнеризацию проекта, настройте Docker файлы, которые находятся в папке `docker`.
- Для продакшена рекомендуется настроить переменные окружения и использовать настроечные файлы (например, .env).

---
### Взаимодействие между модулями

- **Python Backend**: Предоставляет API и серверные сервисы для работы с распознаванием лиц, голосовым взаимодействием, регистрацией визитов и другими функциями.
- **Unity Frontend**: Интегрирует серверную часть с приложением в Unity, обеспечивая все взаимодействия с пользователем, анимации и управление интерфейсом.
- **3D-арт**: Отвечает за создание и анимацию 3D-моделей для использования в Unity, включая осьминога и элементы окружения.

---

### Цели проекта

1. **Распознавание лиц**: Octobot должен корректно распознавать зарегистрированных пользователей и приветствовать их персонализированными сообщениями.
2. **Голосовое взаимодействие**: Пользователи должны иметь возможность задавать вопросы и получать ответы, которые будут озвучены Octobot с помощью технологий синтеза речи.
3. **Плавный пользовательский опыт**: Система должна обеспечивать интуитивный интерфейс и естественные, плавные анимации осьминога.
4. **Стабильность и надёжность системы**: Серверная часть должна быть способна эффективно обрабатывать запросы и обеспечивать минимальные задержки и высокую стабильность работы.

---

### Лицензия
Проект распространяется под лицензией MIT. Подробности можно найти в файле [LICENSE](LICENSE).

---

## Бизнес-логика приложения Octobot

**Octobot** — это интеллектуальный цифровой ассистент для образовательного центра Octopus, который распознает лица учеников и помогает посетителям получать ответы на вопросы с помощью голосового интерфейса.

---

### Как это работает на практике

1. **Приветствие по имени**:
   - Как только ученик подходит к стенду с Octobot, камера сканирует его лицо.
   - Система сравнивает изображение с базой данных и, если находит совпадение, приветствует ученика по имени.
   - Если лицо не найдено в базе, Octobot предлагает представиться и добавить нового пользователя в систему.

2. **Запись посещений**:
   - Octobot фиксирует время прихода и ухода каждого ученика, создавая записи в базе данных.
   - Администраторы центра могут легко отслеживать посещаемость учеников.

3. **Ответы на вопросы**:
   - Octobot может отвечать на вопросы, задаваемые голосом, используя встроенную базу знаний.
   - Если вопрос не имеет ответа, Octobot может указать, что в данный момент информации нет.

---

### Преимущества использования Octobot

- **Автоматизация процесса записи посещений**: Octobot снимает необходимость ручного ведения учёта посещаемости.
- **Персонализированное взаимодействие**: Ученикам приятно, когда система приветствует их по имени, что создаёт комфортную атмосферу.
- **Полезная статистика**: Возможность анализа посещаемости и других данных.
- **Всегда готов помочь**: Octobot круглосуточно доступен для ответа на вопросы учеников.

---

### Структура базы данных

**1. Таблица `Participants`**:

| Поле               | Тип данных | Описание                                | Ограничения                       |
|--------------------|------------|-----------------------------------------|-----------------------------------|
| `id`               | INTEGER    | Уникальный ID участника                 | PRIMARY KEY, AUTOINCREMENT        |
| `name`             | TEXT       | Имя участника                           | NOT NULL                          |
| `face_embedding`   | BLOB       | "Цифровой отпечаток" лица участника     | NOT NULL                          |

**2. Таблица `Visits`**:

| Поле               | Тип данных | Описание                                | Ограничения                       |
|--------------------|------------|-----------------------------------------|-----------------------------------|
| `id`               | INTEGER    | Уникальный ID записи посещения          | PRIMARY KEY, AUTOINCREMENT        |
| `participant_id`   | INTEGER    | ID участника                            | NOT NULL, FOREIGN KEY (ссылка на `Participants.id`) |
| `arrival_time`     | TEXT       | Время прихода                           |                                   |
| `departure_time`   | TEXT       | Время ухода                             |                                   |

**3. Таблица `QA`**:

| Поле               | Тип данных | Описание                                | Ограничения                       |
|--------------------|------------|-----------------------------------------|-----------------------------------|
| `id`               | INTEGER    | Уникальный ID вопроса                   | PRIMARY KEY, AUTOINCREMENT        |
| `question`         | TEXT       | Текст вопроса                           | NOT NULL                          |
| `answer`           | TEXT       | Текст ответа                            | NOT NULL                          |

**Связи между таблицами**:
- Таблица `Participants` связана с таблицей `Visits` отношением "один ко многим", что позволяет фиксировать множество посещений одного участника.

---

**Octobot** обеспечивает простое, интуитивное взаимодействие с пользователями, значительно упрощая управление процессами в образовательном центре и создавая комфортные условия для учеников.


