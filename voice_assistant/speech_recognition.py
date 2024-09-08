import speech_recognition as sr

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recognize_speech(self):
        """
        Распознает речь из аудио.

        Returns:
            Распознанный текст или None, если речь не распознана.
        """
        with sr.Microphone() as source:
            print("Говорите...")
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            print("Вы сказали: " + text)
            return text
        except sr.UnknownValueError:
            print("Не удалось распознать речь")
            return None
        except sr.RequestError as e:
            print("Ошибка сервиса распознавания речи; {0}".format(e))
            return None