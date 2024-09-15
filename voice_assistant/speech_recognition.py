import pyaudio
import wave

from pydub import AudioSegment


class SpeechRecognizer:
    def __init__(self, chunk=1024, format=pyaudio.paInt16, channels=1, rate=44100, record_seconds=5):
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.record_seconds = record_seconds

    def recognize_speech(self):
        """
        Записывает голос и возвращает объект AudioSegment.
        """
        p = pyaudio.PyAudio()

        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        print("Говорите...")
        frames = []
        for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            frames.append(data)

        print("Запись окончена.")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # Сохранение в WAV файл
        wf = wave.open("question.wav", 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Необязательно: вернуть объект AudioSegment, если нужно дальнейшее использование
        return AudioSegment.from_wav("question.wav")
