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
  exclude_from_rag: boolean;
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

export interface ThesisMatchDocument {
  document_id: string;
  title: string;
  category_id: string;
  max_score: number;
  avg_score: number;
  chunk_hits: number;
  similarity_pct: number;
  pages_hit: number[];
  risk_level: 'low' | 'moderate' | 'high' | 'very_high';
  common_themes: string[];
  technologies: string[];
  methods: string[];
  approach: string;
  problem_overlap: string;
  llm_analysis: string;
}

export interface ThesisMatchesSummary {
  total_documents_matched: number;
  documents: ThesisMatchDocument[];
}

export interface BatchUploadResult {
  success: boolean;
  filename: string;
  document?: Document;
  error?: string;
}

export interface BatchUploadData {
  results: BatchUploadResult[];
  total: number;
  successful: number;
}

export interface ThesisCheck {
  id: string;
  filename: string;
  file_type: string;
  file_size: number | null;
  checked_by: string;
  checker_name: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  processing_error: string | null;
  originality_score: number | null;
  plagiarism_level: 'low' | 'moderate' | 'high' | 'very_high' | null;
  total_chunks: number;
  flagged_chunks: number;
  matches_summary: ThesisMatchesSummary | null;
  score_threshold: number;
  created_at: string;
  updated_at: string;
}
