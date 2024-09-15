import os          #подключаем библтотеку операционной системы
import cv2         #подключаем библтотеку для обработки фото
import dlib        #подключаем библиотеку с готовыми нейросетями для поиска лица и лэндмарок и дескрипторов на нем
import PIL         #подключаем библиотеку для работы с растровой графики

from matplotlib.pyplot import imshow

import numpy as np #подключаем библиотеку для работы с массивами

predictor_path= 'models/shape_predictor_68_face_landmarks.dat'  #присваивает переменной путь к файлу, в котором хранится
                                                        #нейросеть, которая ищет лэндмарки
face_rec_path= 'models/dlib_face_recognition_resnet_model_v1.dat'  #присваивает переменной путь к файлу, в котором хранится

detector = dlib.get_frontal_face_detector() #присваивает переменной функцию, из библтотеки dlib,
                                            #которая находит количество лиц и их координаты на фото
sp = dlib.shape_predictor(predictor_path)   #присваивает переменной функцию, из библтотеки dlib,
                                            #которая находит лэндмарки на фото
facerec = dlib.face_recognition_model_v1(face_rec_path)  #присваивает переменной функцию, из библтотеки dlib,
                                                        #которая находит, дескрипторы на фото
habib = cv2.imread("habib.jpg")
habib = cv2.resize(habib, (420, 420))
habib_dets = detector(habib, 1)

for k, d in enumerate(habib_dets):  # цикл по лицам на фото и их координатам
    habib_shape = sp(habib, d)  # добавляет в массив координаты лэндмарок

print(habib_shape)
