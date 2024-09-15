import dlib


class FaceDetector:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()

    def detect_faces(self, image):
        """
        Обнаруживает лица на изображении.

        Args:
            image: Изображение в формате numpy.ndarray.

        Returns:
            Список обнаруженных лиц (объекты dlib.rectangle).
        """
        return self.detector(image, 1)
