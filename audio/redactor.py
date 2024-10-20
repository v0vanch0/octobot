import customtkinter as ctk
import pandas as pd
import json
from tkinter import messagebox, filedialog

# Путь к JSON файлу
json_file_path = "audio_data.json"
ctk.set_default_color_theme("green")
# Функция для загрузки JSON файла и преобразования в DataFrame (таблицу)
def load_json_to_dataframe(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        # Преобразуем словарь в DataFrame
        df = pd.DataFrame(list(data.items()), columns=["Фраза", "Путь к аудиофайлу"])
        return df
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка загрузки JSON: {e}")
        return pd.DataFrame()


# Функция для сохранения отредактированной таблицы обратно в JSON
def save_dataframe_to_json(df, json_file):
    try:
        # Преобразуем DataFrame обратно в словарь
        data_dict = dict(zip(df["Фраза"], df["Путь к аудиофайлу"]))
        with open(json_file, 'w', encoding='utf-8') as file:
            json.dump(data_dict, file, ensure_ascii=False, indent=4)
        messagebox.showinfo("Успех", f"Данные успешно сохранены в {json_file}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка сохранения JSON: {e}")


# Основное приложение
class JSONEditorApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Редактор JSON аудиопутей")
        self.geometry("800x500")

        # Конфигурация для адаптивной сетки (layout)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Загружаем данные
        self.df = load_json_to_dataframe(json_file_path)

        # Интерфейс редактирования
        self.create_widgets()

    def create_widgets(self):
        # Таблица для редактирования фраз и путей
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(1, weight=2)
        self.table_frame.grid_columnconfigure(2, weight=1)
        self.table_frame.grid_columnconfigure(3, weight=1)
        self.table_frame.grid_columnconfigure(4, weight=1)

        self.entries = []
        self.buttons = []

        for i, row in self.df.iterrows():
            phrase_label = ctk.CTkLabel(self.table_frame, text=row["Фраза"])
            phrase_label.grid(row=i, column=0, padx=5, pady=5, sticky="w")

            path_entry = ctk.CTkEntry(self.table_frame)
            path_entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            path_entry.insert(0, row["Путь к аудиофайлу"])

            # Кнопка для удаления
            delete_button = ctk.CTkButton(self.table_frame, text="Удалить", command=lambda i=i: self.delete_row(i))
            delete_button.grid(row=i, column=2, padx=5, pady=5)

            # Кнопка для копирования фразы
            copy_phrase_button = ctk.CTkButton(self.table_frame, text="Копировать фразу",
                                               command=lambda phrase=row["Фраза"]: self.copy_to_clipboard(phrase))
            copy_phrase_button.grid(row=i, column=3, padx=5, pady=5)

            # Кнопка для выбора файла
            file_button = ctk.CTkButton(self.table_frame, text="Выбрать файл",
                                        command=lambda entry=path_entry: self.select_file(entry))
            file_button.grid(row=i, column=4, padx=5, pady=5)

            self.entries.append((row["Фраза"], path_entry))
            self.buttons.append((delete_button, copy_phrase_button, file_button))

        # Кнопка для добавления новой строки
        add_button = ctk.CTkButton(self, text="Добавить новую строку", command=self.add_new_row)
        add_button.grid(row=1, column=0, pady=5)

        # Кнопка для сохранения изменений
        save_button = ctk.CTkButton(self, text="Сохранить изменения", command=self.save_changes)
        save_button.grid(row=2, column=0, pady=5)

    def select_file(self, entry):
        # Открытие диалогового окна для выбора файла
        filepath = filedialog.askopenfilename(title="Выберите аудиофайл", filetypes=[("Audio Files", "*.wav *.mp3")])
        if filepath:
            entry.delete(0, "end")
            entry.insert(0, filepath)

    def add_new_row(self):
        # Создание новой строки для ввода новой фразы и пути к аудиофайлу
        new_row_index = len(self.entries)

        phrase_entry = ctk.CTkEntry(self.table_frame, placeholder_text="Новая фраза")
        phrase_entry.grid(row=new_row_index, column=0, padx=5, pady=5, sticky="w")

        path_entry = ctk.CTkEntry(self.table_frame, placeholder_text="Путь к аудиофайлу")
        path_entry.grid(row=new_row_index, column=1, padx=5, pady=5, sticky="ew")

        delete_button = ctk.CTkButton(self.table_frame, text="Удалить",
                                      command=lambda i=new_row_index: self.delete_row(i))
        delete_button.grid(row=new_row_index, column=2, padx=5, pady=5)

        copy_phrase_button = ctk.CTkButton(self.table_frame, text="Копировать фразу",
                                           command=lambda: self.copy_to_clipboard(phrase_entry.get()))
        copy_phrase_button.grid(row=new_row_index, column=3, padx=5, pady=5)

        file_button = ctk.CTkButton(self.table_frame, text="Выбрать файл", command=lambda: self.select_file(path_entry))
        file_button.grid(row=new_row_index, column=4, padx=5, pady=5)

        # Добавляем новую запись в список для последующего сохранения
        self.entries.append((phrase_entry, path_entry))
        self.buttons.append((delete_button, copy_phrase_button, file_button))

    def delete_row(self, index):
        # Удаление строки из интерфейса
        for widget in self.table_frame.grid_slaves(row=index):
            widget.grid_forget()

        # Удаляем запись из списка
        if index < len(self.entries):
            phrase = self.entries[index][0]
            # Если фраза уже в DataFrame, удаляем её
            if isinstance(phrase, str):
                self.df = self.df[self.df["Фраза"] != phrase]
            # Удаляем из списка
            del self.entries[index]
            del self.buttons[index]

    def copy_to_clipboard(self, text):
        # Копирование текста в буфер обмена
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()  # Обновление окна для работы с буфером обмена

    def save_changes(self):
        # Обновляем DataFrame на основе редактированных данных
        for phrase, entry in self.entries:
            phrase_text = phrase.get() if isinstance(phrase, ctk.CTkEntry) else phrase
            path_text = entry.get()
            if phrase_text and path_text:
                # Если это новая строка, добавляем её в DataFrame
                if not self.df[self.df["Фраза"] == phrase_text].empty:
                    self.df.loc[self.df["Фраза"] == phrase_text, "Путь к аудиофайлу"] = path_text
                else:
                    new_row = pd.DataFrame([[phrase_text, path_text]], columns=["Фраза", "Путь к аудиофайлу"])
                    self.df = pd.concat([self.df, new_row], ignore_index=True)

        # Сохраняем в JSON
        save_dataframe_to_json(self.df, json_file_path)


if __name__ == "__main__":
    app = JSONEditorApp()
    app.mainloop()
