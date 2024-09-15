import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def compare_face_embeddings(embedding1, embedding2):
    """
    Сравнивает два эмбеддинга лиц.

    Args:
        embedding1: Первый эмбеддинг лица.
        embedding2: Второй эмбеддинг лица.

    Returns:
        Значение косинусного сходства между эмбеддингами.
    """
    return cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]

def calculate_euclidean_distance(embedding1, embedding2):
    """
    Вычисляет Евклидово расстояние между двумя эмбеддингами лиц.

    Args:
        embedding1: Первый эмбеддинг лица.
        embedding2: Второй эмбеддинг лица.

    Returns:
        Евклидово расстояние между эмбеддингами.
    """
    return np.linalg.norm(embedding1 - embedding2)