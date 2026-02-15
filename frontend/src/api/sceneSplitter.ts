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

export interface ScenesResponse {
  job_id: string;
  scenes_count: number;
  scenes: Array<{
    scene_number: number;
    scene_text: string;
    sentence_count: number;
    word_count: number;
    char_count: number;
  }>;
}

export interface SceneSentencesResponse {
  job_id: string;
  scene_number: number;
  sentences: Array<{
    index: number;
    text: string;
  }>;
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

export async function fetchScenes(jobId: string): Promise<ScenesResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/scenes`);
  if (!res.ok) throw new Error(`Failed to fetch scenes: ${res.status}`);
  return (await res.json()) as ScenesResponse;
}

export async function fetchSceneSentences(jobId: string, sceneNumber: number): Promise<SceneSentencesResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/scenes/${sceneNumber}/sentences`);
  if (!res.ok) throw new Error(`Failed to fetch sentences: ${res.status}`);
  return (await res.json()) as SceneSentencesResponse;
}

export async function patchScenes(jobId: string, patches: Array<{ scene_number: number; scene_text: string }>) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/scenes`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenes: patches }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Patch failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function approveJob(jobId: string) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/approve`, {
    method: 'POST',
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Approve failed: ${res.status} ${text}`);
  }
  return res.json();
}
