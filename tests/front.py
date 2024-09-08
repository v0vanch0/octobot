import flet as ft
import requests
from pydub import AudioSegment
import io
import os

def main(page: ft.Page):
    page.title = "Octobot Frontend"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # State for audio recording
    recording = ft.Ref[ft.AudioRecorder]()
    is_recording = False

    # Question and answer display
    question_text = ft.Ref[ft.Text]()
    answer_audio = ft.Ref[ft.Audio]()

    # Image upload and processing
    image_upload = ft.Ref[ft.FilePicker]()
    image_preview = ft.Ref[ft.Image]()

    # API endpoints
    process_image_url = 'http://127.0.0.1:5000/process_image'  # Замените на адрес и порт вашего приложения
    ask_question_url = 'http://127.0.0.1:5000/ask_question'   # Замените на адрес и порт вашего приложения

    def process_image_result(e: ft.FilePickerResultEvent):
        if e.files:
            selected_file = e.files[0]
            image_preview.current.src = selected_file.path
            image_preview.current.update()

            # Upload image for face recognition
            files = {'image': open(selected_file.path, 'rb')}
            response = requests.post(process_image_url, files=files)

            if response.status_code == 200:
                page.snack_bar = ft.SnackBar(ft.Text("Изображение обработано!"))
                page.snack_bar.open = True
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {response.text}"))
                page.snack_bar.open = True
                page.update()

    def start_stop_recording():
        nonlocal is_recording
        if not is_recording:
            recording.current.start()
            is_recording = True
            page.snack_bar = ft.SnackBar(ft.Text("Запись начата..."))
            page.snack_bar.open = True
            page.update()
        else:
            recording.current.stop()
            is_recording = False
            page.snack_bar = ft.SnackBar(ft.Text("Запись сохранена"))
            page.snack_bar.open = True
            page.update()

            # Send audio for processing
            send_audio()

    def send_audio():
        audio_path = recording.current.save_to("temp.wav")
        # Convert to mp3
        sound = AudioSegment.from_wav(audio_path)
        sound.export("temp.mp3", format="mp3")

        files = {'audio': open('temp.mp3', 'rb')}
        try:
            response = requests.post(ask_question_url, files=files)
            if response.status_code == 200:
                # Play answer audio
                if response.headers.get('Content-Type') == 'audio/mpeg':
                    answer_audio_data = response.content
                    with open('answer.mp3', 'wb') as f:
                        f.write(answer_audio_data)
                    answer_audio.current.src = 'answer.mp3'
                    answer_audio.current.update()
                else:  # Assuming text response
                    answer_text = response.json()['answer']
                    page.snack_bar = ft.SnackBar(ft.Text(f"Ответ: {answer_text}"))
                    page.snack_bar.open = True
                    page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {response.text}"))
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {str(e)}"))
            page.snack_bar.open = True
            page.update()
        finally:
            # Clean up temp audio files
            os.remove(audio_path)
            if os.path.exists("temp.mp3"):
                os.remove("temp.mp3")

    page.add(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Распознавание лиц", size=20),
                        ft.FilePicker(on_result=process_image_result, ref=image_upload),
                        ft.Image(width=300, height=300, fit=ft.ImageFit.CONTAIN, ref=image_preview),
                    ]
                ),
                ft.Column(
                    [
                        ft.Text("Вопрос-ответ", size=20),
                        ft.ElevatedButton(
                            "Начать/Остановить запись", on_click=start_stop_recording
                        ),
                        ft.AudioRecorder(ref=recording),
                        ft.Text(ref=question_text),
                        ft.Audio(ref=answer_audio, autoplay=True, on_ended=lambda e: answer_audio.current.src = None),
                    ]
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(target=main, view=ft.WEB_BROWSER)