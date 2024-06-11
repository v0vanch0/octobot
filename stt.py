import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QMessageBox,
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import requests
import json
import pyaudio
import vosk


class AudioRecorder(QThread):
    signal_audio_data = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.model = vosk.Model("vosk-model")
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8000,
        )

    def run(self):
        while self.running:
            data = self.stream.read(8000)
            result = self.model.transcribe(data)
            if result:
                json_result = json.loads(result)
                text = json_result.get("text", "")
                self.signal_audio_data.emit(text)

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()


class VoiceAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Голосовой помощник")
        self.setWindowIcon(QIcon("icon.png"))

        self.label_question = QLabel("Говорите:")
        self.line_edit_question = QLineEdit()
        self.line_edit_question.setReadOnly(True)
        self.button_ask = QPushButton("Задать вопрос")
        self.label_answer = QLabel()
        self.label_answer.setAlignment(Qt.AlignCenter)
        self.media_player = QMediaPlayer()

        layout = QVBoxLayout()
        layout.addWidget(self.label_question)
        layout.addWidget(self.line_edit_question)
        layout.addWidget(self.button_ask)
        layout.addWidget(self.label_answer)
        self.setLayout(layout)

        self.button_ask.clicked.connect(self.send_question)

        self.audio_recorder = AudioRecorder()
        self.audio_recorder.signal_audio_data.connect(self.update_question)
        self.audio_recorder.start()

    def send_question(self):
        question = self.line_edit_question.text()
        if question:
            try:
                response = requests.post('http://127.0.0.1:5000/question', json={'question': question})
                if response.status_code == 200:
                    data = response.json()
                    self.label_answer.setText(data.get('answer', 'Ошибка получения ответа'))
                    self.play_audio(data.get('path', None))
                else:
                    self.label_answer.setText(f'Ошибка: {response.status_code}')
            except requests.exceptions.RequestException as e:
                self.label_answer.setText(f'Ошибка соединения: {e}')
        else:
            QMessageBox.warning(self, "Ошибка", "Введите вопрос.")

    def update_question(self, text):
        self.line_edit_question.setText(text)

    def play_audio(self, path):
        if path:
            url = f"http://127.0.0.1:5000/{path}"
            self.media_player.setMedia(QMediaContent(QUrl(url)))
            self.media_player.play()

    def closeEvent(self, event):
        self.audio_recorder.stop()
        self.audio_recorder.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    voice_assistant = VoiceAssistant()
    voice_assistant.show()
    sys.exit(app.exec_())
