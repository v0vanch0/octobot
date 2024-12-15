// src/Visitors.js
import React, { useState, useEffect } from 'react';
import { Form, Button, Card, Row, Col, Alert, Table } from 'react-bootstrap';
import axios from 'axios';

const BASE_URL = 'http://192.168.88.221:5000'; // Убедитесь, что этот URL правильный и доступен

function Visitors() {
  // Состояния для управления вводом
  const [name, setName] = useState('');
  const [visitorId, setVisitorId] = useState('');
  const [image, setImage] = useState(null);
  const [transcript, setTranscript] = useState('');

  const [selectedFolder, setSelectedFolder] = useState(null);
  const [autoUploadStatus, setAutoUploadStatus] = useState('');


  // Состояния для управления сообщениями и отображением
  const [errorMessage, setErrorMessage] = useState('');
  const [apiResponses, setApiResponses] = useState([]);

  // Состояние для предварительного просмотра изображения и списков данных
  const [imagePreview, setImagePreview] = useState(null);
  const [visitorsList, setVisitorsList] = useState([]);
  const [visitsList, setVisitsList] = useState([]);

  // Обработчик изменения изображения
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setImagePreview(null);
    }
  };

  const handleFolderChange = async (e) => {
    const folder = e.target.files;
    if (folder) {
        setSelectedFolder(folder);
        uploadImagesFromFolder(folder);
    }
  };

  const uploadImagesFromFolder = async (folder) => {
    setAutoUploadStatus('Загрузка началась...');
    const filesArray = Array.from(folder);

    for (const file of filesArray) {
        if (!file.name.match(/\.(jpg|jpeg|png|webp|heic|bmp)$/)) {
            continue;
        }

        const fileNameWithoutExtension = file.name.substring(0, file.name.lastIndexOf('.'));
        const nameParts = fileNameWithoutExtension.split('_');
        if (nameParts.length < 2) {
            continue;
        }

        const name = `${nameParts[1]} ${nameParts[0]}`;
        const formData = new FormData();
        formData.append('name', name);
        formData.append('image', file);

        try {
            await axios.post(`${BASE_URL}/api/add_fingerprint`, formData);
        } catch (error) {
            setAutoUploadStatus(`Ошибка при загрузке файла ${file.name}: ${error.message}`);
        }
    }
    setAutoUploadStatus('Загрузка завершена.');
};



  // Функция для добавления отпечатка
  const addFingerprint = async () => {
    // Сброс сообщений об ошибках
    setErrorMessage('');

    if (!name || !image) {
      setErrorMessage('Пожалуйста, введите имя и выберите изображение.');
      return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('image', image);

    try {
      const response = await axios.post(`${BASE_URL}/api/add_fingerprint`, formData);
      // Добавление ответа в список ответов
      setApiResponses(prev => [...prev, { action: 'Добавить Отпечаток', status: response.status, data: response.data }]);
      // Очистка полей формы
      setName('');
      setImage(null);
      setImagePreview(null);
    } catch (error) {
      if (error.response && error.response.status === 409) {
        setErrorMessage('Отпечаток уже есть.');
      } else if (error.response && error.response.status === 500) {
        setErrorMessage(`Ошибка в коде: ${error.message}`);
      } else {
        setErrorMessage(`Ошибка: ${error.message}`);
      }
      // Добавление ошибки в список ответов
      setApiResponses(prev => [...prev, { action: 'Добавить Отпечаток', status: error.response ? error.response.status : 'N/A', data: error.message }]);
    }
  };

  // Функция для получения списка посетителей
  const getVisitors = async () => {
    setErrorMessage('');

    try {
      const response = await axios.get(`${BASE_URL}/api/visitors`);
      setVisitorsList(response.data.visitors || []);
      setApiResponses(prev => [...prev, { action: 'Получить Посетителей', status: response.status, data: response.data }]);
    } catch (error) {
      setErrorMessage(`Ошибка: ${error.message}`);
      setApiResponses(prev => [...prev, { action: 'Получить Посетителей', status: error.response ? error.response.status : 'N/A', data: error.message }]);
    }
  };

  // Функция для получения посещений по ID участника
  const getVisits = async () => {
    setErrorMessage('');

    if (!visitorId) {
      setErrorMessage('Пожалуйста, введите ID участника.');
      return;
    }

    try {
      const response = await axios.get(`${BASE_URL}/api/visits/${visitorId}`);
      setVisitsList(response.data.visits || []);
      setApiResponses(prev => [...prev, { action: `Получить Посещения (ID: ${visitorId})`, status: response.status, data: response.data }]);
    } catch (error) {
      setErrorMessage(`Ошибка: ${error.message}`);
      setApiResponses(prev => [...prev, { action: `Получить Посещения (ID: ${visitorId})`, status: error.response ? error.response.status : 'N/A', data: error.message }]);
    }
  };

  // Функция для удаления старых посещений
  const deleteOldVisits = async () => {
    setErrorMessage('');

    try {
      const response = await axios.delete(`${BASE_URL}/api/delete_old_visits`);
      setApiResponses(prev => [...prev, { action: 'Удалить Старые Посещения', status: response.status, data: response.data }]);
    } catch (error) {
      setErrorMessage(`Ошибка: ${error.message}`);
      setApiResponses(prev => [...prev, { action: 'Удалить Старые Посещения', status: error.response ? error.response.status : 'N/A', data: error.message }]);
    }
  };

  // Функция для экспорта посещений в Excel
  const exportVisitsToExcel = async () => {
    setErrorMessage('');

    try {
      const response = await axios.get(`${BASE_URL}/api/export_visits_to_excel`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'visits.xlsx');
      document.body.appendChild(link);
      link.click();
      setApiResponses(prev => [...prev, { action: 'Экспортировать Посещения в Excel', status: response.status, data: 'Файл успешно экспортирован.' }]);
    } catch (error) {
      setErrorMessage(`Ошибка: ${error.message}`);
      setApiResponses(prev => [...prev, { action: 'Экспортировать Посещения в Excel', status: error.response ? error.response.status : 'N/A', data: error.message }]);
    }
  };

  // Функция для сравнения отпечатков
  const compareFingerprint = async () => {
    setErrorMessage('');

    if (!image) {
      setErrorMessage('Пожалуйста, выберите изображение.');
      return;
    }

    const formData = new FormData();
    formData.append('image', image);

    try {
      const response = await axios.post(`${BASE_URL}/api/compare_fingerprint`, formData);
      setApiResponses(prev => [...prev, { action: 'Сравнить Отпечаток', status: response.status, data: response.data }]);
    } catch (error) {
      setErrorMessage(`Ошибка: ${error.message}`);
      setApiResponses(prev => [...prev, { action: 'Сравнить Отпечаток', status: error.response ? error.response.status : 'N/A', data: error.message }]);
    }
  };

  // Функция для голосового ответа
  const voiceAnswer = async () => {
    setErrorMessage('');

    if (!transcript) {
      setErrorMessage('Пожалуйста, введите текст запроса.');
      return;
    }

    try {
      const response = await axios.post(`${BASE_URL}/api/voice_answer`, { question: transcript });
      setApiResponses(prev => [...prev, { action: 'Голосовой Ответ', status: response.status, data: response.data }]);
      if (response.data.audio_path) {
        const audioUrl = `${BASE_URL}/api/audiofile/${encodeURIComponent(response.data.audio_path)}`;
        const audio = new Audio(audioUrl);
        audio.play();
      }
    } catch (error) {
      setErrorMessage(`Ошибка: ${error.message}`);
      setApiResponses(prev => [...prev, { action: 'Голосовой Ответ', status: error.response ? error.response.status : 'N/A', data: error.message }]);
    }
  };

  // Функция для приветствия по лицу
  const faceRecognitionGreeting = async () => {
    setErrorMessage('');

    if (!image) {
      setErrorMessage('Пожалуйста, выберите изображение.');
      return;
    }

    const formData = new FormData();
    formData.append('image', image);

    try {
      const response = await axios.post(`${BASE_URL}/api/face_recognition_greeting`, formData);
      setApiResponses(prev => [...prev, { action: 'Приветствие по Лицу', status: response.status, data: response.data }]);
      if (response.data.audio_path) {
        const audioUrl = `${BASE_URL}/api/audiofile/${encodeURIComponent(response.data.audio_path)}`;
        const audio = new Audio(audioUrl);
        audio.play();
      } else if (response.data.message) {
        setApiResponses(prev => [...prev, { action: 'Приветствие по Лицу', status: response.status, data: response.data.message }]);
      }
    } catch (error) {
      setErrorMessage(`Ошибка: ${error.message}`);
      setApiResponses(prev => [...prev, { action: 'Приветствие по Лицу', status: error.response ? error.response.status : 'N/A', data: error.message }]);
    }
  };

  .
  // Функция для очистки таблицы ответов
  const clearApiResponses = () => {
    setApiResponses([]);
  };

  return (
    <Card>
      <Card.Body>
        <Card.Title>Управление Посетителями</Card.Title>
        {/* Отображение сообщений об ошибках */}
        {errorMessage && <Alert variant="danger">{errorMessage}</Alert>}
        
        {/* Раздел для отображения списка посетителей */}
        <Card className="mt-4">
          <Card.Body>
            <Card.Title>Список Посетителей</Card.Title>
            {visitorsList.length > 0 ? (
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Имя</th>
                  </tr>
                </thead>
                <tbody>
                  {visitorsList.map((visitor) => (
                    <tr key={visitor.id}>
                      <td>{visitor.id}</td>
                      <td>{visitor.name}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            ) : (
              <p>Посетители не найдены.</p>
            )}
          </Card.Body>
        </Card>

        {/* Раздел для отображения посещений по ID участника */}
        <Card className="mt-4">
          <Card.Body>
            <Card.Title>Посещения по ID Участника</Card.Title>
            {visitsList.length > 0 ? (
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th>Время Посещения</th>
                  </tr>
                </thead>
                <tbody>
                  {visitsList.map((visit, index) => (
                    <tr key={index}>
                      <td>{new Date(visit.arrival_time).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            ) : (
              <p>Посещения не найдены для этого участника.</p>
            )}
          </Card.Body>
        </Card>

        
        
        {/* Форма для взаимодействия с посетителями */}
        {autoUploadStatus && <Alert variant="info">{autoUploadStatus}</Alert>}
        <Form className="mt-4">
        <Form.Group controlId="formFolder" className="mb-3">
          <Form.Label>Добавить папку участников с изображениями</Form.Label>
          <Form.Control
              type="file"
              webkitdirectory="true"
              directory=""
              multiple
              onChange={handleFolderChange}
          />
        </Form.Group>
        

          <Form.Group as={Row} className="mb-3" controlId="formName">
            <Form.Label column sm="2">Имя:</Form.Label>
            <Col sm="10">
              <Form.Control
                type="text"
                placeholder="Введите имя"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </Col>
          </Form.Group>

          <Form.Group as={Row} className="mb-3" controlId="formVisitorId">
            <Form.Label column sm="2">ID:</Form.Label>
            <Col sm="10">
              <Form.Control
                type="text"
                placeholder="Введите ID участника"
                value={visitorId}
                onChange={(e) => setVisitorId(e.target.value)}
              />
            </Col>
          </Form.Group>

          <Form.Group className="mb-3" controlId="formImage">
            <Form.Label>Выбрать изображение</Form.Label>
            <Form.Control type="file" accept="image/*" onChange={handleImageChange} />
          </Form.Group>

          {/* Предварительный просмотр изображения */}
          {imagePreview && (
            <div className="mb-3">
              <img src={imagePreview} alt="Предварительный просмотр" style={{ maxWidth: '100%', height: 'auto' }} />
            </div>
          )}

          <Form.Group className="mb-3" controlId="formTranscript">
            <Form.Label>Текст запроса</Form.Label>
            <Form.Control
              type="text"
              placeholder="Введите текст запроса"
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
            />
          </Form.Group>

          <Button variant="primary" className="me-2" onClick={addFingerprint}>
            Добавить Отпечаток
          </Button>
          <Button variant="secondary" className="me-2" onClick={compareFingerprint}>
            Сравнить Отпечаток
          </Button>
          <Button variant="success" className="me-2" onClick={voiceAnswer}>
            Голосовой Ответ
          </Button>
          <Button variant="info" className="me-2" onClick={faceRecognitionGreeting}>
            Приветствие по Лицу
          </Button>
          <Button variant="warning" className="me-2" onClick={getVisitors}>
            Получить Посетителей
          </Button>
          <Button variant="dark" className="me-2" onClick={getVisits}>
            Получить Посещения
          </Button>
          <Button variant="danger" className="me-2" onClick={deleteOldVisits}>
            Удалить Старые Посещения
          </Button>
          <Button variant="success" onClick={exportVisitsToExcel}>
            Экспортировать Посещения в Excel
          </Button>
        {/* Раздел для отображения таблицы с ответами API */}
        {apiResponses.length > 0 && (
          <>
            <Table striped bordered hover className="mt-4">
              <thead>
                <tr>
                  <th>Действие</th>
                  <th>Статус Код</th>
                  <th>Ответ</th>
                </tr>
              </thead>
              <tbody>
                {apiResponses.map((resp, index) => (
                  <tr key={index}>
                    <td>{resp.action}</td>
                    <td>{resp.status}</td>
                    <td>
                      {typeof resp.data === 'object' ? (
                        resp.data.audio_path ? (
                          <div>
                            <p>{resp.data.answer || 'Аудио файл доступен ниже:'}</p>
                            <audio controls>
                              <source src={`${BASE_URL}/api/audiofile/${encodeURIComponent(resp.data.audio_path)}`} type="audio/mp3" />
                              Ваш браузер не поддерживает элемент audio.
                            </audio>
                          </div>
                        ) : resp.data.message ? (
                          <p>{resp.data.message}</p>
                        ) : (
                          <pre>{JSON.stringify(resp.data, null, 2)}</pre>
                        )
                      ) : (
                        resp.data
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
            {/* Кнопка для очистки истории ответов */}
            <Button variant="outline-secondary" className="mt-2" onClick={clearApiResponses}>
              Очистить Историю Ответов
            </Button>
          </>
        )}
        </Form>
      </Card.Body>
    </Card>
  );
}

export default Visitors;
