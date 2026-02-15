export type SceneStatus = 'pending' | 'approved' | 'generating' | 'ready' | 'error';

export interface ProcessingJobRef {
  id: string;
  status: string;
  currentStep?: string | null;
}

export interface DocumentSummary {
  id: string;
  filename: string;
  name?: string;
  fileSize?: number | null;
  mimeType?: string | null;
  uploadedAt?: string | null;
  processingJobs: ProcessingJobRef[];
  pagesCount?: number | null;
}

export interface Scene {
  id: string;
  index: number;
  sceneNumber: number;
  title?: string;
  text: string;
  status?: SceneStatus;
  sentenceCount?: number;
}

export interface Illustration {
  id: string;
  sceneId: string;
  imageUrl: string;
  createdAt: string;
  promptPreview?: string;
}
