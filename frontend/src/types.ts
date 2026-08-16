export type Citation = {
  document_id: string;
  filename: string;
  page_number: number;
  chunk_id: string;
  chunk_index: number;
  relevance_score: number;
  snippet: string;
};

export type ChatResponse = {
  answer: string;
  refused: boolean;
  model: string;
  sources: Citation[];
  conversation_id: string | null;
};

export type DocumentSummary = {
  id: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  status: string;
  page_count: number;
  chunk_count: number;
  created_at: string;
};

export type ConversationSummary = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type ConversationMessage = {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | string;
  content: string;
  sources: Citation[];
  created_at: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Citation[];
  refused?: boolean;
};
