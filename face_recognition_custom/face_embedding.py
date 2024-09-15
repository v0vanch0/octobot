import dlib
import numpy as np


class FaceEmbedder:
    def __init__(self, shape_predictor_path, face_recognition_model_path):
        self.shape_predictor = dlib.shape_predictor(shape_predictor_path)
        self.face_rec_model = dlib.face_recognition_model_v1(face_recognition_model_path)

    def get_face_embedding(self, image, face_rect):
        """
        Извлекает эмбеддинг лица.

        Args:
            image: Изображение в формате numpy.ndarray.
            face_rect: Объект dlib.rectangle, описывающий область лица.

        Returns:
            Эмбеддинг лица в виде numpy.ndarray.
        """
        shape = self.shape_predictor(image, face_rect)
        return np.array(self.face_rec_model.compute_face_descriptor(image, shape))
