from uuid import UUID

from application.dtos.scenes.scene_segmentation_result_dto import SceneSegmentationResultDto
from application.services.scenes.scene_analysis_service import SceneAnalysisService
from application.services.scenes.scene_segmentation_unit_of_work_protocol import SceneSegmentationUnitOfWork
from application.services.text.abstract_text_extractor import AbstractFileTextExtractor
from domain.entities.scene import Scene
from domain.events.job_completed_event import JobCompletedEvent
from domain.events.scene_saved_event import SceneSavedEvent
from domain.events.scenes_batch_saved_event import ScenesBatchSavedEvent
from domain.exceptions.processing_jobs.processing_job_not_found_exception import ProcessingJobNotFoundException


class SceneSegmentationUseCase:
    def __init__(
        self,
        unit_of_work: SceneSegmentationUnitOfWork,
        text_extractor: AbstractFileTextExtractor,
        scene_analysis_service: SceneAnalysisService
    ):
        self.unit_of_work = unit_of_work
        self.text_extractor = text_extractor
        self.scene_analysis_service = scene_analysis_service

    def execute(
        self,
        job_id: str,
        file_bytes: bytes,
        start_page: int,
        end_page: int
    ) -> SceneSegmentationResultDto:
        with self.unit_of_work as uow:
            try:
                job = uow.processing_job_repository.get_by_id(job_id)
                if not job:
                    raise ProcessingJobNotFoundException(search_criteria="identifier", value=job_id)

                uow.processing_job_repository.update_status(
                    job_id,
                    "extracting",
                    "text_extraction"
                )

                extracted_text = self.text_extractor.extract(file_bytes, start_page, end_page)
                if not extracted_text.strip():
                    raise ValueError("No text extracted from PDF file")

                uow.processing_job_repository.update_status(
                    job_id,
                    "splitting",
                    "scene_splitting"
                )

                analysis = self.scene_analysis_service.analyze(extracted_text)
                scene_ids = []
                for index, (scene_text, stats) in enumerate(zip(analysis.scenes, analysis.statistics)):
                    scene = Scene(
                        processing_job_id=job.id,
                        scene_number=index + 1,
                        scene_text=scene_text,
                        sentence_count=stats.sentence_count,
                        word_count=stats.word_count,
                        char_count=stats.char_count,
                        start_sentence_idx=None,
                        end_sentence_idx=None,
                        boundary_confidence=None
                    )
                    uow.scene_repository.add(scene, commit=False)
                    scene_ids.append(scene.id)

                    scene_saved_event = SceneSavedEvent(
                        scene_number=scene.scene_number,
                        document_id=job.document_id,
                        scene_text=scene.scene_text,
                        scene_id=scene.id,
                        job_id=UUID(job_id),
                        word_count=scene.word_count,
                        char_count=scene.char_count
                    )
                    uow.outbox_repository.create_event(scene_saved_event, commit=False)

                batch_saved_event = ScenesBatchSavedEvent(
                    job_id=UUID(job_id),
                    document_id=job.document_id,
                    scene_ids=scene_ids,
                    total_count=len(scene_ids)
                )
                uow.outbox_repository.create_event(batch_saved_event, commit=False)

                job_completed_event = JobCompletedEvent(
                    job_id=UUID(job_id),
                    document_id=job.document_id,
                    total_scenes=len(scene_ids)
                )
                uow.outbox_repository.create_event(job_completed_event, commit=False)

                uow.processing_job_repository.update_status(
                    job_id,
                    "completed",
                    "finalization",
                    commit=False
                )
                uow.commit()

                return SceneSegmentationResultDto(
                    scenes_count=len(scene_ids),
                    text_length=len(extracted_text)
                )
            except Exception as exc:
                uow.rollback()
                uow.processing_job_repository.update_status(
                    job_id,
                    "failed",
                    error_message=str(exc),
                    commit=False
                )
                uow.commit()
                raise
