
import requests
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from playsound import playsound
import threading

BASE_URL = 'http://localhost:5000'


class APITestApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("API Test Application")
        self.geometry("900x700")
        ctk.set_default_color_theme("green")
        # Создание основных фреймов
        self.create_widgets()

    def create_widgets(self):
        # Верхний фрейм для заголовка
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", pady=10)

        header_label = ctk.CTkLabel(header_frame, text="API Тестовое Приложение", font=("Arial", 24))
        header_label.pack()

        # Основной фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Левый фрейм для кнопок и ввода
        control_frame = ctk.CTkFrame(main_frame, width=200)
        control_frame.pack(side="left", fill="y", padx=(0, 10))

        # Правый фрейм для отображения результатов
        self.display_frame = ctk.CTkFrame(main_frame)
        self.display_frame.pack(side="left", fill="both", expand=True)

        # Элементы управления
        self.create_controls(control_frame)

    def create_controls(self, parent):
        # Поле для ввода имени
        self.name_entry = ctk.CTkEntry(parent, placeholder_text="Введите имя")
        self.name_entry.pack(pady=5)

        # Кнопка для выбора изображения
        self.image_path = None
        select_image_button = ctk.CTkButton(parent, text="Выбрать изображение", command=self.select_image)
        select_image_button.pack(pady=5)

        # Кнопки для тестов
        ctk.CTkButton(parent, text="Добавить Отпечаток", command=self.add_fingerprint_test).pack(pady=5)
        ctk.CTkButton(parent, text="Сравнить Отпечаток", command=self.compare_fingerprint_test).pack(pady=5)
        ctk.CTkButton(parent, text="Голосовой Ответ", command=self.voice_answer_test).pack(pady=5)
        ctk.CTkButton(parent, text="Приветствие по Лицу", command=self.face_recognition_greeting_test).pack(pady=5)

        # Поле для ввода текста запроса
        self.transcript_entry = ctk.CTkEntry(parent, placeholder_text="Введите текст запроса")
        self.transcript_entry.pack(pady=5)

    def select_image(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png")]
        filepath = filedialog.askopenfilename(title="Выбрать изображение", filetypes=filetypes)
        if filepath:
            self.image_path = filepath

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
        text_widget = ctk.CTkTextbox(self.display_frame, width=600, height=200)
        text_widget.insert("0.0", text)
        text_widget.configure(state="disabled")
        text_widget.pack(pady=10)

    def play_audio_from_path(self, audio_path):
        # Воспроизведение аудиофайла по предоставленному пути
        if audio_path and os.path.exists(audio_path):
            threading.Thread(target=playsound, args=(audio_path,), daemon=True).start()
        else:
            self.display_text(f"Файл не найден по пути: {audio_path}")

    def add_fingerprint_test(self):
        self.clear_display()

        name = self.name_entry.get()
        if not name:
            self.display_text("Пожалуйста, введите имя.")
            return

        if not self.image_path:
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

        result_text = f"Статус код: {response.status_code}"
        try:
            result_text += f"Ответ: {response.json()}"
        except requests.exceptions.JSONDecodeError:
            result_text += "Ответ сервера не является JSON."

        self.display_text(result_text)

    def compare_fingerprint_test(self):
        self.clear_display()

        if not self.image_path:
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

        result_text = f"Статус код: {response.status_code}"
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
        data = {"transcript": transcript}

        try:
            response = requests.post(url, json=data)
        except Exception as e:
            self.display_text(f"Ошибка при подключении к серверу: {e}")
            return

        result_text = f"Статус код: {response.status_code}"

        try:
            response_data = response.json()
            if 'audio_path' in response_data:
                result_text += "Аудио ответ будет воспроизведен."
                audio_path = response_data['audio_path']
                self.play_audio_from_path(audio_path)
            else:
                result_text += f"Ответ: {response_data}"
        except requests.exceptions.JSONDecodeError:
            result_text += "Ответ сервера не является JSON."

        self.display_text(result_text)

    def face_recognition_greeting_test(self):
        self.clear_display()

        if not self.image_path:
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

        result_text = f"Статус код: {response.status_code}"

        try:
            response_data = response.json()
            if 'audio_path' in response_data:
                result_text += "Аудио приветствие будет воспроизведено."
                audio_path = response_data['audio_path']
                self.play_audio_from_path(audio_path)
            else:
                result_text += f"Ответ: {response_data}"
        except requests.exceptions.JSONDecodeError:
            result_text += "Ответ сервера не является JSON."

        self.display_text(result_text)


if __name__ == '__main__':
    app = APITestApp()
    app.mainloop()
