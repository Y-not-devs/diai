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
  role: 'user' | 'assistant';
  type: 'text' | 'diagnosis';
  content: string;
  diagnoses?: DiagnosisResult[];
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
