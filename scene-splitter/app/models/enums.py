from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    EXTRACTING = "extracting"
    SPLITTING = "splitting"
    READY_FOR_REVIEW = "ready-for-review"
    APPROVED = "approved"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingStep(str, Enum):
    UPLOAD = "upload"
    TEXT_EXTRACTION = "text_extraction"
    SCENE_SPLITTING = "scene_splitting"
    FINALIZATION = "finalization"
