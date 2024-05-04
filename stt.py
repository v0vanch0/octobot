import pyaudio
import vosk
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize

stemmer = SnowballStemmer("russian")
model = vosk.Model("vosk-model-ru-0.42")  # путь к модели
rec = vosk.KaldiRecognizer(model, 8000)  # дискредитация с чавстотой 8000
p = pyaudio.PyAudio()
stream = p.open(  # "Прямой эфир" голоса
    format=pyaudio.paInt16,
    channels=1,
    rate=8000,
    input=True,
    frames_per_buffer=8000
)
stream.start_stream()


while True:
    data = stream.read(8000)
    if len(data) == 0:
        break
    text = rec.Result() if rec.AcceptWaveform(data) else rec.PartialResult()
    tokens = word_tokenize(text)
    stemmed_words = [stemmer.stem(word) for word in tokens]
    print(stemmed_words)
