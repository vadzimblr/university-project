from dependency_injector import containers, providers

from application.services.scenes.get_scenes_by_job_identifier_service import GetSceneByJobIdentifierService
from infrastructure.persistence.repositories.processing_job_repository import ProcessingJobRepository
from infrastructure.persistence.repositories.scene_repository import SceneRepository
from infrastructure.persistence.session import SessionFactory


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "presentation.api",
            "infrastructure.persistence.repositories",
            "infrastructure.persistence",
        ],
    )

    session_factory = providers.Singleton(SessionFactory)

    session = providers.Factory(
        session_factory
    )

    processing_job_repository = providers.Factory(
        ProcessingJobRepository,
        db_session=session
    )

    scene_repository = providers.Factory(
        SceneRepository,
        db_session=session
    )

    get_scenes_by_job_identifier_service = providers.Factory(
        GetSceneByJobIdentifierService,
        processing_job_repository=processing_job_repository,
        scene_repository=scene_repository,
    )
