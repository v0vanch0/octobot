from gtts import gTTS
import os

class TextToSpeech:
    def __init__(self, language='ru'):
        self.language = language

    def speak(self, text):
        """
        Синтезирует речь из текста и воспроизводит ее.

        Args:
            text: Текст для синтеза речи.
        """
        tts = gTTS(text=text, lang=self.language)
        tts.save("temp.mp3")
        os.system("mpg123 temp.mp3")
        os.remove("temp.mp3")