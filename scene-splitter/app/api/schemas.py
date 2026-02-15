from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ScenePatchPayload(BaseModel):
    scene_number: int = Field(..., ge=1, description="Номер сцены для обновления")
    scene_text: str = Field(..., description="Новый текст сцены")


class ScenePatchRequest(BaseModel):
    scenes: List[ScenePatchPayload]


class SceneResponse(BaseModel):
    scene_id: UUID
    scene_number: int
    scene_text: str
    sentence_count: int
    word_count: int
    char_count: int
    start_sentence_idx: Optional[int]
    end_sentence_idx: Optional[int]
    boundary_confidence: Optional[float]


class ScenePatchResponse(BaseModel):
    job_id: UUID
    scenes: List[SceneResponse]


class SceneMergeRequest(BaseModel):
    scene_numbers: List[int] = Field(
        ...,
        description="Номера сцен для объединения (минимум 2, только подряд).",
    )


class SceneMergeResponse(BaseModel):
    job_id: UUID
    scenes: List[SceneResponse]


# --- documents listing ---
class ProcessingJobRef(BaseModel):
    id: UUID
    status: str
    current_step: Optional[str]


class DocumentItem(BaseModel):
    id: UUID
    filename: str
    file_size: Optional[int]
    mime_type: Optional[str]
    created_at: Optional[str]
    processing_jobs: List[ProcessingJobRef]


class DocumentsResponse(BaseModel):
    documents: List[DocumentItem]


# --- scene sentences ---
class SceneSentence(BaseModel):
    index: int = Field(..., description="Порядковый номер предложения в сцене (с 1)")
    text: str


class SceneSentencesResponse(BaseModel):
    job_id: UUID
    scene_number: int
    sentences: List[SceneSentence]
