from sqlalchemy.orm import Session, sessionmaker

from infrastructure.persistence.repositories.processing_job_repository import ProcessingJobRepository
from infrastructure.persistence.repositories.scene_repository import SceneRepository
from infrastructure.persistence.repositories.outbox_repository import OutboxRepository


class SceneSegmentationUnitOfWork:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
        self.session: Session | None = None
        self.processing_job_repository: ProcessingJobRepository | None = None
        self.scene_repository: SceneRepository | None = None
        self.outbox_repository: OutboxRepository | None = None

    def __enter__(self) -> "SceneSegmentationUnitOfWork":
        self.session = self.session_factory()
        self.processing_job_repository = ProcessingJobRepository(self.session)
        self.scene_repository = SceneRepository(self.session)
        self.outbox_repository = OutboxRepository(self.session)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type:
            self.rollback()
        if self.session:
            self.session.close()

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()
