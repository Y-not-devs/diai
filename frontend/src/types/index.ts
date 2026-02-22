export interface DiagnosisResult {
  id: string;
  diagnosis: string;
  icd_10: string;
  confidence: number; // 0 to 1
  explanation: string;
  protocol_title: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  type: 'text' | 'diagnosis' | 'error';
  content: string;
  diagnoses?: DiagnosisResult[];
  messageId?: number;
  createdAt?: string;
}

export interface BackendRequest {
  user_id: string;
  chat_id: string;
  text: string;
}

export interface BackendResponse {
  answer_type: 0 | 1;
  text: string;
  diagnosis?: DiagnosisResult[];
}

export interface ChatSummary {
  chat_id: string;
  chat_name: string;
  updated_at?: string;
}

export interface ChatsResponse {
  chats: ChatSummary[];
}

export interface ChatMessageApi {
  message_id: number;
  role: 'user' | 'assistant' | 'system';
  text: string;
  created_at?: string;
  answer_type?: 0 | 1;
  diagnosis?: DiagnosisResult[] | null;
}

export interface ChatMessagesResponse {
  messages: ChatMessageApi[];
  has_more: boolean;
  min_message_id?: number;
}
