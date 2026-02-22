import {
  BackendRequest,
  BackendResponse,
  ChatsResponse,
  ChatMessagesResponse,
} from '../types';

// Замените URL на адрес вашего Python-бэкенда
const API_BASE_URL = 'http://localhost:8001/api';

const buildUrl = (path: string, params?: Record<string, string | number | undefined>) => {
  const url = new URL(`${API_BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    });
  }
  return url.toString();
};

export const getChats = async (userId: string): Promise<ChatsResponse> => {
  const response = await fetch(buildUrl('/chats', { user_id: userId }));
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
};

export const getChatMessages = async (
  chatId: string,
  limit: number,
  beforeId?: number,
): Promise<ChatMessagesResponse> => {
  const response = await fetch(
    buildUrl('/chat_messages', {
      chat_id: chatId,
      limit,
      before_id: beforeId,
    }),
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
};

export const sendMessageToBackend = async (data: BackendRequest): Promise<BackendResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat_message`, {
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
