export type SceneStatus = 'pending' | 'approved' | 'generating' | 'ready' | 'error';

export interface Document {
  id: string;
  name: string;
  pagesCount: number;
  uploadedAt: string;
}

export interface Scene {
  id: string;
  index: number;
  title?: string;
  text: string;
  startIdx: number;
  endIdx: number;
  status: SceneStatus;
}

export interface Illustration {
  id: string;
  sceneId: string;
  imageUrl: string;
  createdAt: string;
  promptPreview?: string;
}
