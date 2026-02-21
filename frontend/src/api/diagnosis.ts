import { BackendRequest, BackendResponse } from '../types';

// Замените URL на адрес вашего Python-бэкенда
const API_URL = 'http://localhost:8000/api/chat'; 

export const sendMessageToBackend = async (data: BackendRequest): Promise<BackendResponse> => {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending message to backend:', error);
    throw error; // Пробрасываем ошибку дальше, чтобы обработать в App.tsx
  }
};
