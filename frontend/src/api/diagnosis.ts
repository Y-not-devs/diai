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
    
    // Fallback mock response for development if backend is not running
    console.log('Falling back to mock response...');
    await new Promise((resolve) => setTimeout(resolve, 1500));
    
    // Simulate a clarifying question first, then a diagnosis
    const isFirstMessage = data.text.length < 20;
    
    if (isFirstMessage) {
      return {
        answer_type: 1,
        text: 'Уточните, пожалуйста, наблюдается ли у пациента повышенное артериальное давление или белок в моче? Это поможет точнее определить диагноз по протоколам.',
      };
    }
    
    return {
      answer_type: 0,
      text: 'Основываясь на предоставленном анамнезе, я проанализировал клинические протоколы РК. Вот наиболее вероятные диагнозы:',
      diagnosis: [
        {
          id: '1',
          diagnosis: 'HELLP-синдром',
          icd_10: 'O14.2',
          confidence: 0.95,
          explanation: 'Совпадение по ключевым симптомам (гемолиз, повышение ферментов печени, тромбоцитопения).',
          protocol_title: 'КЛИНИЧЕСКИЙ ПРОТОКОЛ ДИАГНОСТИКИ И ЛЕЧЕНИЯ HELLP-СИНДРОМ (№177 от 13.01.2023)',
        },
        {
          id: '2',
          diagnosis: 'Преэклампсия',
          icd_10: 'O14.9',
          confidence: 0.65,
          explanation: 'Присутствует артериальная гипертензия, но нет полного спектра признаков HELLP.',
          protocol_title: 'КЛИНИЧЕСКИЙ ПРОТОКОЛ ДИАГНОСТИКИ И ЛЕЧЕНИЯ ПРЕЭКЛАМПСИИ',
        },
      ],
    };
  }
};
