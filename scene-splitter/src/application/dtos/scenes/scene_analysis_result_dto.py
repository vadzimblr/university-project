from typing import List
import numpy as np
from pydantic import BaseModel

from application.dtos.scenes.scene_statistic_dto import SceneStatisticDto


class SceneAnalysisResultDto(BaseModel):
    scenes: List[str]
    valleys: List[int]
    similarities: np.ndarray
    statistics: List[SceneStatisticDto]
