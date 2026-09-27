export type DocumentRoute = "normal_pdf" | "scanned_pdf" | "table_heavy" | "image" | "docx" | "plain_text";

export interface UploadedDocument {
  id: string;
  user_id: string;
  filename: string;
  route: DocumentRoute;
  page_count: number;
  storage_path: string;
}

export interface Citation {
  filename: string;
  page: number;
  snippet: string;
  confidence: number;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  verified: boolean;
}
