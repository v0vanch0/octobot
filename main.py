import json
import os

import nltk
import pyaudio
import requests
import sounddevice as sd
import soundfile as sf
import vosk
from vosk import Model

nltk.download('stopwords')
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=8000,
    input=True,
    frames_per_buffer=8000
)
if not os.path.exists("vosk-model"):
    print("Please download the Vosk model and unpack as 'vosk-model' in the current directory.")
    exit(1)

vosk_model = Model("vosk-model")


def recognize_speech_from_audio(model):
    rec = vosk.KaldiRecognizer(model, 8000)
    print("Нажмите Enter если готовы")
    input()
    print("Скажите что-нибудь")
    while True:
        data = stream.read(8000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            return result.get('text', '')


recognized_speech = recognize_speech_from_audio(vosk_model)
print(f"Recognized text: {recognized_speech}")
url = "http://127.0.0.1:5000/question"
data = {
    "question": recognized_speech
}
headers = {
    "Content-type": "application/json; charset=UTF-8"
}

response = requests.post(url, data=json.dumps(data), headers=headers)

# Получить ответ
print(response.json())
response = response.json()

# Extract data and sampling rate from file
array, smp_rt = sf.read(response['path'], dtype='float32')

# start the playback
sd.play(array, smp_rt)

# Wait until file is done playing
status = sd.wait()

# stop the sound
sd.stop()

# Останавливаем и закрываем поток и PyAudio
stream.stop_stream()
stream.close()
p.terminate()
