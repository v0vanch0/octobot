import os

from flask import Flask, request, jsonify
from face_recognition_custom import FaceDetector, FaceEmbedder, face_recognition_utils
from database import DatabaseConnector
from voice_assistant import SpeechRecognizer, TextToSpeech, QuestionAnswering
import cv2
import numpy as np
import time
import io
from pydub import AudioSegment
from gtts import gTTS

# Инициализация компонентов
face_detector = FaceDetector()
face_embedder = FaceEmbedder("models/shape_predictor_68_face_landmarks.dat",
                             "models/dlib_face_recognition_resnet_model_v1.dat")
database_connector = DatabaseConnector()
speech_recognizer = SpeechRecognizer()
text_to_speech = TextToSpeech()

# Передаем database_connector в QuestionAnswering
question_answering = QuestionAnswering(database_connector)

app = Flask(__name__)


def register_new_user(face_embedding):
    """
    Регистрирует нового пользователя с использованием голосового ввода.
    """
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        text_to_speech.speak("Здравствуйте! Я вас не знаю. Пожалуйста, назовите ваше имя.")
        name_audio = speech_recognizer.recognize_speech()
        if name_audio:
            name = name_audio.strip()
            text_to_speech.speak(f"Вы сказали: {name}. Верно?")
            confirmation_audio = speech_recognizer.recognize_speech()
            if confirmation_audio and "да" in confirmation_audio.lower():
                # Сохраняем информацию о новом участнике в базе данных
                participant_id = database_connector.add_participant(name, face_embedding)
                text_to_speech.speak(f"Спасибо, {name}! Вы успешно зарегистрированы.")
                return True
            else:
                text_to_speech.speak("Пожалуйста, попробуйте еще раз.")
        else:
            text_to_speech.speak("Извините, я не расслышал ваше имя. Пожалуйста, попробуйте еще раз.")
        attempts += 1
    text_to_speech.speak("Извините, превышено максимальное количество попыток. Попробуйте позже.")
    return False


@app.route('/process_image', methods=['POST'])
def process_image():
    """
    Обрабатывает изображение с камеры и распознает лица.
    """
    global recognized_participant  # Use the global variable
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image_file = request.files['image']
    # Преобразование image_file в numpy.ndarray
    nparr = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    faces = face_detector.detect_faces(image)

    for face in faces:
        face_embedding = face_embedder.get_face_embedding(image, face)
        participant = database_connector.get_participant_by_face_embedding(face_embedding)

        if participant:
            recognized_participant = participant['name']
            # Участник найден
            # Проверяем, была ли уже зарегистрирована запись о приходе за сегодня
            cursor = database_connector.get_participants_db().cursor()  # Использование g
            cursor.execute('''
                SELECT COUNT(*) 
                FROM visits 
                WHERE participant_id = ? 
                AND arrival_time LIKE ?
            ''', (participant['id'], time.strftime("%Y-%m-%d%") + "%"))

            arrival_count_today = cursor.fetchone()[0]

            if arrival_count_today == 0:
                # Регистрация прихода
                database_connector.register_participant_arrival(participant['id'])
                text_to_speech.speak(f"Здравствуйте, {participant['name']}!")

            # Проверяем, была ли уже зарегистрирована запись об уходе за сегодня и был ли приход
            cursor.execute('''
                SELECT COUNT(*) 
                FROM visits 
                WHERE participant_id = ? 
                AND departure_time LIKE ?
            ''', (participant['id'], time.strftime("%Y-%m-%d%") + "%"))

            departure_count_today = cursor.fetchone()[0]

            if arrival_count_today > departure_count_today:
                # Регистрация ухода
                database_connector.register_participant_departure(participant['id'])
                text_to_speech.speak(f"До свидания, {participant['name']}!")

        else:
            # Участник не найден
            register_new_user(face_embedding)

    return jsonify({'message': 'Image processed'}), 200


@app.route('/ask_question', methods=['POST'])
def ask_question():
    """
    Обрабатывает вопрос от пользователя, получая аудио на вход.
    """
    # Check if the post request has the file part
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio provided'}), 400

    if 'participant' not in request.form:
        return jsonify({'error': 'Participant name not provided'}), 400

    audio_file = request.files['audio']
    participant_name = request.form['participant']

    # Save the audio file temporarily
    audio_file.save(os.path.join(os.getcwd(), "temp.wav"))

    # Add a delay (adjust if needed)
    time.sleep(1)  # Wait for 1 second

    # Convert the audio file
    sound = AudioSegment.from_wav("temp.wav")
    sound.export("temp.mp3", format="mp3")
    time.sleep(1)
    # Process the audio with speech_recognizer
    try:
        question = speech_recognizer.recognize_speech_from_file("temp.mp3").strip()
    except Exception as e:
        return jsonify({'error': 'Error processing audio', 'details': str(e)}), 500
    finally:
        # Delete temporary files
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")
        if os.path.exists("temp.mp3"):
            os.remove("temp.mp3")

    print(f"Распознанный вопрос: {question}")  # Вывод вопроса для отладки
    if participant_name:  # Используем имя из request.form
        question = f"{participant_name} спрашивает: {question}"

    answer = question_answering.answer_question(question)
    print(f"Найденный ответ: {answer}")  # Вывод ответа для отладки

    if answer:
        # Сохраняем ответ в виде mp3 файла
        tts = gTTS(text=answer, lang='ru')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp.read(), 200, {'Content-Type': 'audio/mpeg'}
    else:
        return jsonify({'error': 'Answer not found'}), 404  # Возвращаем JSON с ошибкой


if __name__ == '__main__':

    # Регистрация функций для работы с базами данных
    app.teardown_appcontext(database_connector.close_db)

    app.run(debug=True, host='0.0.0.0')
