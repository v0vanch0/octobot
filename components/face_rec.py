import dlib
import numpy as np
from PIL import Image

# Инициализация моделей dlib для детекции лиц и получения эмбеддингов
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("dats/shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dats/dlib_face_recognition_resnet_model_v1.dat")


def extract_face_embedding(image_file):
    """Извлекает цифровой отпечаток лица из изображения."""
    # Загрузка изображения с использованием Pillow
    image = Image.open(image_file)

    # Конвертируем изображение в формат numpy
    image_np = np.array(image)

    # Поиск лиц на изображении
    faces = face_detector(image_np)

    if len(faces) == 0:
        return None

    # Извлекаем ключевые точки лица
    shape = shape_predictor(image_np, faces[0])

    # Получаем эмбеддинг лица
    face_embedding = np.array(face_rec_model.compute_face_descriptor(image_np, shape))

    return face_embedding
