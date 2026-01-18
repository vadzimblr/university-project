from typing import Protocol

from infrastructure.persistence.repositories.processing_job_repository import ProcessingJobRepository
from infrastructure.persistence.repositories.scene_repository import SceneRepository
from infrastructure.persistence.repositories.outbox_repository import OutboxRepository


class SceneSegmentationUnitOfWork(Protocol):
    processing_job_repository: ProcessingJobRepository
    scene_repository: SceneRepository
    outbox_repository: OutboxRepository

    def __enter__(self) -> "SceneSegmentationUnitOfWork": ...
    def __exit__(self, exc_type, exc, tb) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
