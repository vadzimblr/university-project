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
