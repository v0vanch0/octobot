import os
import threading
import tkinter.ttk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import requests
import simpleaudio as sa
from PIL import Image, ImageTk

BASE_URL = 'http://localhost:5000'


class APITestApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("API Test Application")
        self.geometry("1000x800")
        ctk.set_default_color_theme("green")
        self.create_widgets()

    def create_visitors_tab(self, parent):
        ctk.CTkLabel(parent, text="Управление Посетителями", font=("Arial", 18)).pack(pady=10)

        entry_frame = ctk.CTkFrame(parent)
        entry_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(entry_frame, text="Имя:", width=80).grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ctk.CTkEntry(entry_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(entry_frame, text="ID:", width=80).grid(row=1, column=0, padx=5, pady=5)
        self.visitor_id_entry = ctk.CTkEntry(entry_frame)
        self.visitor_id_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkButton(parent, text="Выбрать изображение", command=self.select_image).pack(pady=5)
        ctk.CTkButton(parent, text="Добавить Отпечаток", command=self.add_fingerprint_test).pack(pady=5)
        ctk.CTkButton(parent, text="Получить Посетителей", command=self.get_visitors_test).pack(pady=5)
        ctk.CTkButton(parent, text="Получить Посещения", command=self.get_visits_test).pack(pady=5)
        ctk.CTkButton(parent, text="Удалить Старые Посещения", command=self.delete_old_visits_test).pack(pady=5)
        ctk.CTkButton(parent, text="Экспортировать в Excel", command=self.export_visits_to_excel_test).pack(pady=5)

    def create_qa_tab(self, parent):
        ctk.CTkLabel(parent, text="Управление QA", font=("Arial", 18)).pack(pady=10)

        entry_frame = ctk.CTkFrame(parent)
        entry_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(entry_frame, text="ID QA пары:", width=80).grid(row=0, column=0, padx=5, pady=5)
        self.qa_id_entry = ctk.CTkEntry(entry_frame)
        self.qa_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(entry_frame, text="Вопрос:", width=80).grid(row=1, column=0, padx=5, pady=5)
        self.question_entry = ctk.CTkEntry(entry_frame)
        self.question_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(entry_frame, text="Ответ:", width=80).grid(row=2, column=0, padx=5, pady=5)
        self.answer_entry = ctk.CTkEntry(entry_frame)
        self.answer_entry.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkButton(parent, text="Создать QA пару", command=self.create_qa_test).pack(pady=5)
        ctk.CTkButton(parent, text="Получить Все QA пары", command=self.get_all_qa_test).pack(pady=5)
        ctk.CTkButton(parent, text="Получить QA пару", command=self.get_qa_test).pack(pady=5)
        ctk.CTkButton(parent, text="Обновить QA пару", command=self.update_qa_test).pack(pady=5)
        ctk.CTkButton(parent, text="Удалить QA пару", command=self.delete_qa_test).pack(pady=5)

    def create_widgets(self):
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", pady=10)

        header_label = ctk.CTkLabel(header_frame, text="API Тестовое Приложение", font=("Arial", 24))
        header_label.pack()

        # Создание TabView для разделения функционала
        tab_view = ctk.CTkTabview(self, width=900, height=700)
        tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка для управления посетителями
        visitors_tab = tab_view.add("Посетители")
        self.create_visitors_tab(visitors_tab)

        # Вкладка для управления QA
        qa_tab = tab_view.add("Вопросы и Ответы")
        self.create_qa_tab(qa_tab)

        # Общая область вывода
        self.display_frame = ctk.CTkScrollableFrame(self, width=900, height=200)
        self.display_frame.pack(fill="x", expand=True, padx=10, pady=10)

    def create_controls(self, parent):
        # Поля ввода для участников
        ctk.CTkLabel(parent, text="Управление Посетителями", font=("Arial", 16)).pack(pady=10)

        self.name_entry = ctk.CTkEntry(parent, placeholder_text="Введите имя")
        self.name_entry.pack(pady=5)

        self.visitor_id_entry = ctk.CTkEntry(parent, placeholder_text="Введите ID участника")
        self.visitor_id_entry.pack(pady=5)

        select_image_button = ctk.CTkButton(parent, text="Выбрать изображение", command=self.select_image)
        select_image_button.pack(pady=5)

        # Кнопки для CRUD операций с участниками
        ctk.CTkButton(parent, text="Добавить Отпечаток", command=self.add_fingerprint_test).pack(pady=5)
        ctk.CTkButton(parent, text="Сравнить Отпечаток", command=self.compare_fingerprint_test).pack(pady=5)
        ctk.CTkButton(parent, text="Голосовой Ответ", command=self.voice_answer_test).pack(pady=5)
        ctk.CTkButton(parent, text="Приветствие по Лицу", command=self.face_recognition_greeting_test).pack(pady=5)
        ctk.CTkButton(parent, text="Получить Посетителей", command=self.get_visitors_test).pack(pady=5)
        ctk.CTkButton(parent, text="Получить Посещения", command=self.get_visits_test).pack(pady=5)
        ctk.CTkButton(parent, text="Удалить Старые Посещения", command=self.delete_old_visits_test).pack(pady=5)
        ctk.CTkButton(parent, text="Экспортировать Посещения в Excel", command=self.export_visits_to_excel_test).pack(
            pady=5)

        # Разделение для QA
        tkinter.ttk.Separator(parent).pack(fill="x", pady=10)

        # Поля ввода для QA
        ctk.CTkLabel(parent, text="Управление QA", font=("Arial", 16)).pack(pady=10)

        self.qa_id_entry = ctk.CTkEntry(parent, placeholder_text="Введите ID QA пары")
        self.qa_id_entry.pack(pady=5)

        self.question_entry = ctk.CTkEntry(parent, placeholder_text="Введите вопрос")
        self.question_entry.pack(pady=5)

        self.answer_entry = ctk.CTkEntry(parent, placeholder_text="Введите ответ")
        self.answer_entry.pack(pady=5)

        # Кнопки для CRUD операций с QA
        ctk.CTkButton(parent, text="Создать QA пару", command=self.create_qa_test).pack(pady=5)
        ctk.CTkButton(parent, text="Получить Все QA пары", command=self.get_all_qa_test).pack(pady=5)
        ctk.CTkButton(parent, text="Получить QA пару", command=self.get_qa_test).pack(pady=5)
        ctk.CTkButton(parent, text="Обновить QA пару", command=self.update_qa_test).pack(pady=5)
        ctk.CTkButton(parent, text="Удалить QA пару", command=self.delete_qa_test).pack(pady=5)

        self.transcript_entry = ctk.CTkEntry(parent, placeholder_text="Введите текст запроса")
        self.transcript_entry.pack(pady=5)

    def select_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png")]
        filepath = filedialog.askopenfilename(title="Выбрать изображение", filetypes=filetypes)
        if filepath:
            self.image_path = filepath
            self.display_image(self.image_path)

    def clear_display(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()

    def display_image(self, image_path):
        image = Image.open(image_path)
        image.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(image)
        img_label = ctk.CTkLabel(self.display_frame, image=photo)
        img_label.image = photo
        img_label.pack(pady=10)

    def display_text(self, text):
        text_widget = ctk.CTkTextbox(self.display_frame, wrap="word")
        text_widget.insert("0.0", text)
        text_widget.configure(state="disabled")
        text_widget.pack(padx=10, pady=10, fill="both", expand=True)

    # Методы для CRUD операций с участниками (посетителями)
    def get_visitors_test(self):
        """Тестирование получения всех посетителей."""
        self.clear_display()
        self.display_text("Запрос списка посетителей")

        url = f'{BASE_URL}/api/visitors'

        try:
            response = requests.get(url)
            result_text = f"Статус код: {response.status_code}\n\n"
            try:
                visitors = response.json().get("visitors", [])
                for visitor in visitors:
                    result_text += f"ID: {visitor['id']}, Имя: {visitor['name']}\n"
            except requests.exceptions.JSONDecodeError:
                result_text += "Ответ сервера не является JSON."
            self.display_text(result_text)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")

    def delete_old_visits_test(self):
        """Тестирование удаления старых посещений."""
        self.clear_display()
        self.display_text("Запрос на удаление старых посещений")

        url = f'{BASE_URL}/api/delete_old_visits'

        try:
            response = requests.delete(url)
            result_text = f"Статус код: {response.status_code}\n\n"
            try:
                response_data = response.json()
                result_text += f"Ответ: {response_data}"
            except requests.exceptions.JSONDecodeError:
                result_text += "Ответ сервера не является JSON."
            self.display_text(result_text)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")

    def handle_api_response(self, response):
        """Обработка ответов API."""
        result_text = f"Статус код: {response.status_code}\n\n"
        try:
            response_data = response.json()
            result_text += f"Ответ: {response_data}"
        except requests.exceptions.JSONDecodeError:
            result_text += "Ответ сервера не является JSON."
        self.display_text(result_text)

    def export_visits_to_excel_test(self):
        """Тестирование экспорта посещений через API."""

        url = f'{BASE_URL}/api/export_visits_to_excel'

        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel файлы", "*.xlsx")],
                    title="Сохранить как"
                )
                if filepath:
                    with open(filepath, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    self.display_text(f"Файл сохранен: {filepath}")
            else:
                self.handle_api_response(response)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")

    def export_visits_to_excel_test(self):
        """Тестирование экспорта посещений в Excel."""
        self.clear_display()
        self.display_text("Запрос на экспорт посещений в Excel")

        url = f'{BASE_URL}/api/export_visits_to_excel'

        try:
            response = requests.get(url)
            result_text = f"Статус код: {response.status_code}\n\n"
            try:
                response_data = response.json()
                result_text += f"Ответ: {response_data}"
            except requests.exceptions.JSONDecodeError:
                result_text += "Ответ сервера не является JSON."
            self.display_text(result_text)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")

    def get_visits_test(self):
        """Тестирование получения посещений конкретного участника."""
        self.clear_display()

        participant_id = self.visitor_id_entry.get()
        if not participant_id:
            self.display_text("Пожалуйста, введите ID участника.")
            return

        self.display_text(f"Запрос посещений для участника с ID: {participant_id}")

        url = f'{BASE_URL}/api/visits/{participant_id}'

        try:
            response = requests.get(url)
            result_text = f"Статус код: {response.status_code}\n\n"
            try:
                data = response.json()
                if "visits" in data:
                    for visit in data["visits"]:
                        result_text += f"Время прибытия: {visit['arrival_time']}\n"
                else:
                    result_text += f"Ответ: {data}"
            except requests.exceptions.JSONDecodeError:
                result_text += "Ответ сервера не является JSON."
            self.display_text(result_text)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")

    def play_audio_from_path(self, audio_path):
        # Воспроизведение аудиофайла по предоставленному пути
        if audio_path and os.path.exists(audio_path):
            def play_audio():
                wave_obj = sa.WaveObject.from_wave_file(audio_path)
                play_obj = wave_obj.play()
                play_obj.wait_done()  # Дождаться завершения воспроизведения

            threading.Thread(target=play_audio, daemon=True).start()
        else:
            self.display_text(f"Файл не найден по пути: {audio_path}")

    def add_fingerprint_test(self):
        self.clear_display()

        name = self.name_entry.get()
        if not name:
            self.display_text("Пожалуйста, введите имя.")
            return

        if not hasattr(self, 'image_path'):
            self.display_text("Пожалуйста, выберите изображение.")
            return

        self.display_text(f"Добавление нового участника: {name}")
        self.display_image(self.image_path)

        url = f'{BASE_URL}/api/add_fingerprint'
        files = {'image': open(self.image_path, 'rb')}
        data = {'name': name}

        try:
            response = requests.post(url, files=files, data=data)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")
            return

        result_text = f"Статус код: {response.status_code}\n\n"
        try:
            result_text += f"Ответ: {response.json()}"
        except requests.exceptions.JSONDecodeError:
            result_text += "Ответ сервера не является JSON."

        self.display_text(result_text)

    def compare_fingerprint_test(self):
        self.clear_display()

        if not hasattr(self, 'image_path'):
            self.display_text("Пожалуйста, выберите изображение.")
            return

        self.display_text("Сравнение отпечатка лица")
        self.display_image(self.image_path)

        url = f'{BASE_URL}/api/compare_fingerprint'
        files = {'image': open(self.image_path, 'rb')}

        try:
            response = requests.post(url, files=files)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")
            return

        result_text = f"Статус код: {response.status_code}\n\n"
        try:
            result_text += f"Ответ: {response.json()}"
        except requests.exceptions.JSONDecodeError:
            result_text += "Ответ сервера не является JSON."

        self.display_text(result_text)

    def voice_answer_test(self):
        self.clear_display()

        transcript = self.transcript_entry.get()
        if not transcript:
            self.display_text("Пожалуйста, введите текст запроса.")
            return

        self.display_text("Тестирование голосового ответа")

        url = f'{BASE_URL}/api/voice_answer'
        data = {"question": transcript}

        try:
            response = requests.post(url, json=data)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")
            return

        result_text = f"Статус код: {response.status_code}\n\n"

        try:
            response_data = response.json()
            if 'audio_path' in response_data:
                result_text += f"Аудио ответ будет воспроизведен. Путь: {response_data['audio_path']}"
                audio_path = response_data['audio_path']
                self.play_audio_from_path(audio_path)
            else:
                result_text += f"Ответ: {response_data}"
        except requests.exceptions.JSONDecodeError:
            result_text += "Ответ сервера не является JSON."

        self.display_text(result_text)

    def face_recognition_greeting_test(self):
        self.clear_display()

        if not hasattr(self, 'image_path'):
            self.display_text("Пожалуйста, выберите изображение.")
            return

        self.display_text("Тестирование приветствия по лицу")
        self.display_image(self.image_path)

        url = f'{BASE_URL}/api/face_recognition_greeting'
        files = {'image': open(self.image_path, 'rb')}

        try:
            response = requests.post(url, files=files)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")
            return

        result_text = f"Статус код: {response.status_code}\n\n"

        try:
            response_data = response.json()
            if 'audio_path' in response_data:
                result_text += "Аудио приветствие будет воспроизведено."
                audio_path = response_data['audio_path']
                self.play_audio_from_path(audio_path)
            elif 'message' in response_data:
                # Отображаем сообщение, если посетитель уже посетил сегодня
                result_text += f"Ответ: {response_data['message']}"
            else:
                result_text += f"Ответ: {response_data}"
        except requests.exceptions.JSONDecodeError:
            result_text += "Ответ сервера не является JSON."

        self.display_text(result_text)

    # Методы для CRUD операций с QA

    def create_qa_test(self):
        """Тестирование создания новой QA пары."""
        self.clear_display()

        question = self.question_entry.get()
        answer = self.answer_entry.get()

        if not question or not answer:
            self.display_text("Пожалуйста, введите и вопрос, и ответ.")
            return

        self.display_text(f"Создание новой QA пары:\nВопрос: {question}\nОтвет: {answer}")

        url = f'{BASE_URL}/api/qa'
        data = {'question': question, 'answer': answer}

        try:
            response = requests.post(url, json=data)
            result_text = f"Статус код: {response.status_code}\n\n"
            try:
                response_data = response.json()
                result_text += f"Ответ: {response_data}"
            except requests.exceptions.JSONDecodeError:
                result_text += "Ответ сервера не является JSON."
            self.display_text(result_text)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")

    def get_all_qa_test(self):
        """Тестирование получения всех QA пар."""
        self.clear_display()
        self.display_text("Запрос всех QA пар")

        url = f'{BASE_URL}/api/qa'

        try:
            response = requests.get(url)
            result_text = f"Статус код: {response.status_code}\n\n"
            try:
                qa_list = response.json().get("qa", [])
                for qa in qa_list:
                    result_text += f"ID: {qa['id']}\nВопрос: {qa['question']}\nОтвет: {qa['answer']}\n\n"
            except requests.exceptions.JSONDecodeError:
                result_text += "Ответ сервера не является JSON."
            self.display_text(result_text)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")

    def get_qa_test(self):
        """Тестирование получения конкретной QA пары по ID."""
        self.clear_display()

        qa_id = self.qa_id_entry.get()
        if not qa_id:
            self.display_text("Пожалуйста, введите ID QA пары.")
            return

        self.display_text(f"Запрос QA пары с ID: {qa_id}")

        url = f'{BASE_URL}/api/qa/{qa_id}'

        try:
            response = requests.get(url)
            result_text = f"Статус код: {response.status_code}\n\n"
            try:
                data = response.json()
                if "qa" in data:
                    qa = data["qa"]
                    result_text += f"ID: {qa['id']}\nВопрос: {qa['question']}\nОтвет: {qa['answer']}"
                else:
                    result_text += f"Ответ: {data}"
            except requests.exceptions.JSONDecodeError:
                result_text += "Ответ сервера не является JSON."
            self.display_text(result_text)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")

    def update_qa_test(self):
        """Тестирование обновления QA пары по ID."""
        self.clear_display()

        qa_id = self.qa_id_entry.get()
        question = self.question_entry.get()
        answer = self.answer_entry.get()

        if not qa_id:
            self.display_text("Пожалуйста, введите ID QA пары для обновления.")
            return

        if not question and not answer:
            self.display_text("Пожалуйста, введите хотя бы вопрос или ответ для обновления.")
            return

        self.display_text(f"Обновление QA пары с ID: {qa_id}\nНовые значения:\nВопрос: {question}\nОтвет: {answer}")

        url = f'{BASE_URL}/api/qa/{qa_id}'
        data = {}
        if question:
            data['question'] = question
        if answer:
            data['answer'] = answer

        try:
            response = requests.put(url, json=data)
            result_text = f"Статус код: {response.status_code}\n\n"
            try:
                response_data = response.json()
                result_text += f"Ответ: {response_data}"
            except requests.exceptions.JSONDecodeError:
                result_text += "Ответ сервера не является JSON."
            self.display_text(result_text)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")

    def delete_qa_test(self):
        """Тестирование удаления QA пары по ID."""
        self.clear_display()

        qa_id = self.qa_id_entry.get()

        if not qa_id:
            self.display_text("Пожалуйста, введите ID QA пары для удаления.")
            return

        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить QA пару с ID: {qa_id}?")
        if not confirm:
            self.display_text("Удаление отменено пользователем.")
            return

        self.display_text(f"Удаление QA пары с ID: {qa_id}")

        url = f'{BASE_URL}/api/qa/{qa_id}'

        try:
            response = requests.delete(url)
            result_text = f"Статус код: {response.status_code}\n\n"
            try:
                response_data = response.json()
                result_text += f"Ответ: {response_data}"
            except requests.exceptions.JSONDecodeError:
                result_text += "Ответ сервера не является JSON."
            self.display_text(result_text)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")


if __name__ == '__main__':
    app = APITestApp()
    app.mainloop()
