export interface GeneratedImageResponse {
  story_uuid: string;
  scene_number: number;
  image: {
    id: number | string;
    bucket: string;
    object_name: string;
    size: number;
    created_at?: string | null;
    prompt_id?: string | null;
    prompt_text?: string | null;
    url: string;
    expires_in?: number;
  };
}

const API_BASE = ((import.meta.env.VITE_IMAGE_GENERATOR_URL as string | undefined) ?? '/image-generator').replace(/\/$/, '');

export async function fetchSceneImage(
  storyUuid: string,
  sceneNumber: number,
  options: { expiresSeconds?: number; signal?: AbortSignal } = {},
): Promise<GeneratedImageResponse | null> {
  const params = new URLSearchParams();
  if (options.expiresSeconds) params.set('expires_seconds', String(options.expiresSeconds));

  const res = await fetch(
    `${API_BASE}/stories/${encodeURIComponent(storyUuid)}/scenes/${sceneNumber}/image${params.toString() ? `?${params}` : ''}`,
    { signal: options.signal },
  );

  if (res.status === 404) return null;
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Image fetch failed: ${res.status} ${text}`);
  }
  return (await res.json()) as GeneratedImageResponse;
}
