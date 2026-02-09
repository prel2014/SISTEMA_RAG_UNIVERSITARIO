export interface ChatMessage {
  id: string;
  conversation_id: string;
  user_id: string;
  role: 'user' | 'assistant';
  content: string;
  source_documents: SourceDocument[];
  created_at: string;
  feedback?: number;
}

export interface SourceDocument {
  document_id: string;
  title: string;
  page: number;
  preview: string;
  score: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  category_id?: string;
}

export interface Conversation {
  conversation_id: string;
  last_message_at: string;
  preview: string;
}

export interface FeedbackRequest {
  chat_history_id: string;
  rating: 1 | -1;
  comment?: string;
}
