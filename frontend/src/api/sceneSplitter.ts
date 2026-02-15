import type { DocumentSummary } from '@/types/models';

const API_BASE = ((import.meta.env.VITE_SCENE_SPLITTER_URL as string | undefined) ?? '/api').replace(/\/$/, '');

export interface DocumentsResponse {
  documents: Array<{
    id: string;
    filename: string;
    file_size?: number | null;
    mime_type?: string | null;
    created_at?: string | null;
    processing_jobs: Array<{
      id: string;
      status: string;
      current_step?: string | null;
    }>;
  }>;
}

export interface UploadResponse {
  job_id: string;
  task_id: string;
  document_id: string;
  status: string;
  message: string;
}

export async function fetchDocuments(): Promise<DocumentSummary[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error(`Failed to fetch documents: ${res.status}`);
  const data = (await res.json()) as DocumentsResponse;
  return data.documents.map((doc) => ({
    id: doc.id,
    filename: doc.filename,
    name: doc.filename,
    fileSize: doc.file_size ?? null,
    mimeType: doc.mime_type ?? null,
    uploadedAt: doc.created_at ?? null,
    processingJobs: doc.processing_jobs.map((j) => ({
      id: j.id,
      status: j.status,
      currentStep: j.current_step ?? null,
    })),
  }));
}

export async function uploadDocument(file: File, startPage = 1, endPage = 999): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('start_page', String(startPage));
  formData.append('end_page', String(endPage));

  const res = await fetch(`${API_BASE}/split-scenes/`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed: ${res.status} ${text}`);
  }

  return (await res.json()) as UploadResponse;
}
