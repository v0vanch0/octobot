import os
import requests
from voice_assistant import SpeechRecognizer, TextToSpeech

# API endpoint for asking questions
ask_question_url = 'http://127.0.0.1:5000/ask_question'

# Initialize components
speech_recognizer = SpeechRecognizer()
text_to_speech = TextToSpeech()

def main():
    """Main function of the console application."""
    while True:
        # Запрос на запись вопроса
        participant_name = input("Введите ваше имя: ")
        input("Нажмите Enter для записи вопроса...")
        question_audio = speech_recognizer.recognize_speech()  # Вызов функции
        if not question_audio:
            print("Ошибка распознавания. Попробуйте еще раз.")
            continue

        print(f"Вы спросили: ...")  # Не печатаем объект AudioSegment

        # Отправка аудио вопроса на backend
        files = {'audio': open('question.wav', 'rb')}
        data = {'participant': participant_name}

        try:
            response = requests.post(ask_question_url, files=files, data=data)
        except requests.exceptions.RequestException as e:
            print(f"Ошибка соединения: {e}")
            continue
        finally:
            try:
                os.remove("question.wav") # Remove the temporary file
            except:
                print("Сделать!")

        # Handle backend response
        if response.status_code == 200:
            # Play audio answer
            if response.headers.get('Content-Type') == 'audio/mpeg':
                with open('answer.mp3', 'wb') as f:
                    f.write(response.content)
                os.system("start answer.mp3")  # Play on Windows
                os.remove("answer.mp3")
            else:
                print(f"Ответ: {response.text}")
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()