from pydantic import BaseModel
from typing import List

class SceneSplitResponse(BaseModel):
    scenes: List[str]
