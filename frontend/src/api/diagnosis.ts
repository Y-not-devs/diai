import { Message, DiagnosisResult } from '../types';

// Mock API call for now
export const sendMessageToAI = async (history: Message[]): Promise<Message> => {
  console.log('Sending history to AI:', history);
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 1500));

  const userMessages = history.filter(m => m.role === 'user');
  
  // Mock logic: if it's the first message, ask a clarifying question.
  // Otherwise, return the final diagnosis.
  if (userMessages.length === 1) {
    return {
      id: Date.now().toString(),
      role: 'assistant',
      type: 'text',
      content: 'Уточните, пожалуйста, наблюдается ли у пациента повышенное артериальное давление или белок в моче? Это поможет точнее определить диагноз по протоколам.',
    };
  }

  return {
    id: Date.now().toString(),
    role: 'assistant',
    type: 'diagnosis',
    content: 'Основываясь на предоставленном анамнезе, я проанализировал клинические протоколы РК. Вот наиболее вероятные диагнозы:',
    diagnoses: [
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
};
