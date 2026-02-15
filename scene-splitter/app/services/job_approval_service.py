from typing import List
from sqlalchemy.orm import Session

from app.models import Scene
from app.repositories.processing_job_repository import ProcessingJobRepository
from app.repositories.outbox_repository import OutboxRepository
from app.events import SceneSavedEvent, ScenesBatchSavedEvent, JobCompletedEvent
from app.models.enums import ProcessingStatus, ProcessingStep


class JobApprovalError(Exception):
    """Base class for job approval related errors."""


class JobNotFoundError(JobApprovalError):
    pass


class JobAlreadyApprovedError(JobApprovalError):
    pass


class JobNotReadyError(JobApprovalError):
    pass


class ScenesMissingError(JobApprovalError):
    pass


class JobApprovalService:
    def __init__(self, session: Session):
        self.session = session
        self.job_repo = ProcessingJobRepository(session)
        self.outbox_repo = OutboxRepository(session)

    def approve(self, job_id: str) -> dict:
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise JobNotFoundError(f"Job {job_id} not found")

        if job.status == ProcessingStatus.APPROVED or job.status == "approved":
            raise JobAlreadyApprovedError(f"Job {job_id} already approved")

        if job.status not in {ProcessingStatus.READY_FOR_REVIEW, "ready-for-review"}:
            raise JobNotReadyError(f"Job {job_id} is not ready for approval")

        scenes: List[Scene] = (
            self.session.query(Scene)
            .filter(Scene.processing_job_id == job.id)
            .order_by(Scene.scene_number)
            .all()
        )

        if not scenes:
            raise ScenesMissingError(f"Job {job_id} has no scenes to publish")

        for scene in scenes:
            event = SceneSavedEvent(
                scene_number=scene.scene_number,
                document_id=job.document_id,
                scene_text=scene.scene_text,
                scene_id=scene.id,
                job_id=job.id,
                word_count=scene.word_count,
                char_count=scene.char_count,
            )
            self.outbox_repo.create_event(event=event, session=self.session)

        batch_event = ScenesBatchSavedEvent(
            job_id=job.id,
            document_id=job.document_id,
            scene_ids=[scene.id for scene in scenes],
            total_count=len(scenes),
        )
        self.outbox_repo.create_event(event=batch_event, session=self.session)

        completed_event = JobCompletedEvent(
            job_id=job.id,
            document_id=job.document_id,
            total_scenes=len(scenes),
        )
        self.outbox_repo.create_event(event=completed_event, session=self.session)

        self.session.commit()

        self.job_repo.update_status(job_id, ProcessingStatus.APPROVED, ProcessingStep.FINALIZATION)

        return {
            "job_id": str(job.id),
            "status": ProcessingStatus.APPROVED,
            "events_created": True,
            "scenes_count": len(scenes),
        }
