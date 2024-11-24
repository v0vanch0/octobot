// src/QA.js
import React, { useState, useEffect } from 'react';
import { Form, Button, Card, Row, Col, Alert, Table } from 'react-bootstrap';
import axios from 'axios';

const BASE_URL = 'http://192.168.88.221:5000'; // Убедитесь, что этот URL правильный и доступен

function QA() {
  // Состояния для управления вводом и списком QA пар
  const [qaId, setQaId] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [qaList, setQaList] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Функция для создания новой QA пары
  const createQAPair = async () => {
    // Сброс сообщений об ошибках и успехе
    setErrorMessage('');
    setSuccessMessage('');

    if (!question || !answer) {
      setErrorMessage('Пожалуйста, введите и вопрос, и ответ.');
      return;
    }

    try {
      const response = await axios.post(`${BASE_URL}/api/qa`, { question, answer });
      setSuccessMessage(`QA пара успешно создана. Статус код: ${response.status}`);
      // Очистка полей формы
      setQuestion('');
      setAnswer('');
      // Обновление списка QA пар после добавления новой пары
      fetchAllQAPairs();
    } catch (error) {
      if (error.response && error.response.status === 409) {
        setErrorMessage('Участник с таким ответом уже существует.');
      } else if (error.response && error.response.data && error.response.data.error) {
        setErrorMessage(`Ошибка: ${error.response.data.error}`);
      } else {
        setErrorMessage(`Ошибка: ${error.message}`);
      }
    }
  };

  // Функция для получения всех QA пар
  const getAllQAPairs = async () => {
    // Сброс сообщений об ошибках и успехе
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const response = await axios.get(`${BASE_URL}/api/qa`);
      setQaList(response.data.qa || []);
      setSuccessMessage(`Получено ${response.data.qa.length} QA пар. Статус код: ${response.status}`);
    } catch (error) {
      setErrorMessage(`Ошибка: ${error.message}`);
    }
  };

  // Функция для получения конкретной QA пары по ID
  const getQAPair = async () => {
    // Сброс сообщений об ошибках и успехе
    setErrorMessage('');
    setSuccessMessage('');

    if (!qaId) {
      setErrorMessage('Пожалуйста, введите ID QA пары.');
      return;
    }

    try {
      const response = await axios.get(`${BASE_URL}/api/qa/${qaId}`);
      if (response.data.qa) {
        setQaList([response.data.qa]);
        setSuccessMessage(`QA пара с ID ${qaId} успешно получена. Статус код: ${response.status}`);
      } else {
        setErrorMessage('QA пара не найдена.');
      }
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setErrorMessage('QA пара не найдена.');
      } else if (error.response && error.response.data && error.response.data.error) {
        setErrorMessage(`Ошибка: ${error.response.data.error}`);
      } else {
        setErrorMessage(`Ошибка: ${error.message}`);
      }
    }
  };

  // Функция для обновления QA пары по ID
  const updateQAPair = async () => {
    // Сброс сообщений об ошибках и успехе
    setErrorMessage('');
    setSuccessMessage('');

    if (!qaId) {
      setErrorMessage('Пожалуйста, введите ID QA пары для обновления.');
      return;
    }

    if (!question && !answer) {
      setErrorMessage('Пожалуйста, введите хотя бы вопрос или ответ для обновления.');
      return;
    }

    const data = {};
    if (question) data.question = question;
    if (answer) data.answer = answer;

    try {
      const response = await axios.put(`${BASE_URL}/api/qa/${qaId}`, data);
      setSuccessMessage(`QA пара с ID ${qaId} успешно обновлена. Статус код: ${response.status}`);
      // Очистка полей формы
      setQaId('');
      setQuestion('');
      setAnswer('');
      // Обновление списка QA пар после обновления
      fetchAllQAPairs();
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setErrorMessage('QA пара не найдена.');
      } else if (error.response && error.response.data && error.response.data.error) {
        setErrorMessage(`Ошибка: ${error.response.data.error}`);
      } else {
        setErrorMessage(`Ошибка: ${error.message}`);
      }
    }
  };

  // Функция для удаления QA пары по ID
  const deleteQAPair = async () => {
    // Сброс сообщений об ошибках и успехе
    setErrorMessage('');
    setSuccessMessage('');

    if (!qaId) {
      setErrorMessage('Пожалуйста, введите ID QA пары для удаления.');
      return;
    }

    if (!window.confirm(`Вы уверены, что хотите удалить QA пару с ID: ${qaId}?`)) {
      setErrorMessage('Удаление отменено пользователем.');
      return;
    }

    try {
      const response = await axios.delete(`${BASE_URL}/api/qa/${qaId}`);
      setSuccessMessage(`QA пара с ID ${qaId} успешно удалена. Статус код: ${response.status}`);
      // Очистка полей формы
      setQaId('');
      // Обновление списка QA пар после удаления
      fetchAllQAPairs();
    } catch (error) {
      if (error.response && error.response.status === 404) {
        setErrorMessage('QA пара не найдена.');
      } else if (error.response && error.response.data && error.response.data.error) {
        setErrorMessage(`Ошибка: ${error.response.data.error}`);
      } else {
        setErrorMessage(`Ошибка: ${error.message}`);
      }
    }
  };

  // Функция для получения всех QA пар (используется в create, update и delete)
  const fetchAllQAPairs = async () => {
    try {
      const response = await axios.get(`${BASE_URL}/api/qa`);
      setQaList(response.data.qa || []);
    } catch (error) {
      console.error('Ошибка при получении всех QA пар:', error);
      setErrorMessage(`Ошибка при получении всех QA пар: ${error.message}`);
    }
  };

  // Использование useEffect для загрузки всех QA пар при первом рендере
  useEffect(() => {
    getAllQAPairs();
  }, []);

  return (
    <Card>
      <Card.Body>
        <Card.Title>Управление QA</Card.Title>
        {/* Отображение сообщений об ошибках и успехе */}
        {errorMessage && <Alert variant="danger">{errorMessage}</Alert>}
        {successMessage && <Alert variant="success" style={{ whiteSpace: 'pre-wrap' }}>{successMessage}</Alert>}
        <Form>
          <Form.Group as={Row} className="mb-3" controlId="formQaId">
            <Form.Label column sm="2">ID QA пары:</Form.Label>
            <Col sm="10">
              <Form.Control
                type="text"
                placeholder="Введите ID QA пары"
                value={qaId}
                onChange={(e) => setQaId(e.target.value)}
              />
            </Col>
          </Form.Group>

          <Form.Group as={Row} className="mb-3" controlId="formQuestion">
            <Form.Label column sm="2">Вопрос:</Form.Label>
            <Col sm="10">
              <Form.Control
                type="text"
                placeholder="Введите вопрос"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />
            </Col>
          </Form.Group>

          <Form.Group as={Row} className="mb-3" controlId="formAnswer">
            <Form.Label column sm="2">Ответ:</Form.Label>
            <Col sm="10">
              <Form.Control
                type="text"
                placeholder="Введите ответ"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
              />
            </Col>
          </Form.Group>

          <Button variant="primary" className="me-2" onClick={createQAPair}>
            Создать QA пару
          </Button>
          <Button variant="secondary" className="me-2" onClick={getAllQAPairs}>
            Получить Все QA пары
          </Button>
          <Button variant="info" className="me-2" onClick={getQAPair}>
            Получить QA пару
          </Button>
          <Button variant="warning" className="me-2" onClick={updateQAPair}>
            Обновить QA пару
          </Button>
          <Button variant="danger" onClick={deleteQAPair}>
            Удалить QA пару
          </Button>
        </Form>

        {/* Новое отображение всех QA пар с аудио */}
        <Card className="mt-4">
          <Card.Body>
            <Card.Title>Список всех QA пар с аудио</Card.Title>
            {qaList.length > 0 ? (
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Вопрос</th>
                    <th>Ответ</th>
                    <th>Аудио Ответа</th>
                  </tr>
                </thead>
                <tbody>
                  {qaList.map((qa) => (
                    <tr key={qa.id}>
                      <td>{qa.id}</td>
                      <td>{qa.question}</td>
                      <td>{qa.answer}</td>
                      <td>
                        {qa.audio_path ? (
                          <audio controls>
                            <source src={`${BASE_URL}/api/audiofile/${encodeURIComponent(qa.audio_path)}`} type="audio/mp3" />
                            Ваш браузер не поддерживает элемент audio.
                          </audio>
                        ) : (
                          "Нет аудио ответа"
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            ) : (
              <p>QA пары не найдены.</p>
            )}
            {/* Кнопка для обновления списка QA пар */}
            <Button variant="primary" onClick={getAllQAPairs}>
              Обновить QA пары
            </Button>
          </Card.Body>
        </Card>
      </Card.Body>
    </Card>
  );
}

export default QA;
