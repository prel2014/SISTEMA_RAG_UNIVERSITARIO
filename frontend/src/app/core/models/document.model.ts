export interface Document {
  id: string;
  title: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  category_id: string | null;
  category: Category | null;
  uploaded_by: string;
  processing_status: 'pending' | 'processing' | 'completed' | 'failed';
  processing_error: string | null;
  chunk_count: number;
  created_at: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon: string;
  color: string;
  is_active: boolean;
  document_count: number;
}

export interface RagConfig {
  chunk_size: number;
  chunk_overlap: number;
  top_k: number;
  score_threshold: number;
  temperature: number;
  num_ctx: number;
  llm_model: string;
  embedding_model: string;
}

export interface DashboardStats {
  total_users: number;
  total_documents: number;
  total_conversations: number;
  total_messages: number;
  feedback_rate: number;
}
