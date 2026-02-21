from dependency_injector import containers, providers

from application.services.scenes.get_scenes_by_job_identifier_service import GetSceneByJobIdentifierService
from application.services.scenes.scene_analysis_service import SceneAnalysisService
from application.services.scenes.scene_segmentation_use_case import SceneSegmentationUseCase
from application.services.scenes.scene_statistics_calculator import BasicSceneStatisticsCalculator
from application.services.scenes.sequential_scene_splitter import SequentialSceneSplitter
from application.services.text.cosine_similarity_analyzer import CosineSimilarityAnalyzer
from application.services.text.pdf_extractor import PdfExtractor
from application.services.text.regex_text_normalizer import RegexTextNormalizer
from application.services.text.russian_sentence_tokenizer import RussianSentenceTokenizer
from application.services.text.sentence_transformer_embedder import SentenceTransformerEmbedder
from infrastructure.persistence.repositories.document_repository import DocumentRepository
from infrastructure.persistence.repositories.outbox_repository import OutboxRepository
from infrastructure.persistence.repositories.processing_job_repository import ProcessingJobRepository
from infrastructure.persistence.repositories.scene_repository import SceneRepository
from infrastructure.persistence.session import SessionFactory
from infrastructure.persistence.unit_of_work import SceneSegmentationUnitOfWork


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            "presentation.api",
            "infrastructure.persistence.repositories",
            "infrastructure.persistence",
            "infrastructure.celery.tasks",
        ],
    )

    session_factory = providers.Singleton(SessionFactory)

    session = providers.Factory(
        session_factory
    )

    document_repository = providers.Factory(
        DocumentRepository,
        db_session=session
    )

    processing_job_repository = providers.Factory(
        ProcessingJobRepository,
        db_session=session
    )

    scene_repository = providers.Factory(
        SceneRepository,
        db_session=session
    )

    outbox_repository = providers.Factory(
        OutboxRepository,
        db_session=session
    )

    get_scenes_by_job_identifier_service = providers.Factory(
        GetSceneByJobIdentifierService,
        processing_job_repository=processing_job_repository,
        scene_repository=scene_repository,
    )

    text_normalizer = providers.Factory(RegexTextNormalizer)
    sentence_tokenizer = providers.Factory(RussianSentenceTokenizer)
    text_embedder = providers.Singleton(SentenceTransformerEmbedder)
    similarity_analyzer = providers.Factory(CosineSimilarityAnalyzer)
    scene_splitter = providers.Factory(SequentialSceneSplitter)

    scene_statistics_calculator = providers.Factory(
        BasicSceneStatisticsCalculator,
        tokenizer=sentence_tokenizer
    )

    scene_analysis_service = providers.Factory(
        SceneAnalysisService,
        normalizer=text_normalizer,
        tokenizer=sentence_tokenizer,
        embedder=text_embedder,
        similarity_analyzer=similarity_analyzer,
        scene_splitter=scene_splitter,
        stats_calculator=scene_statistics_calculator
    )

    text_extractor = providers.Factory(PdfExtractor)

    scene_segmentation_unit_of_work = providers.Factory(
        SceneSegmentationUnitOfWork,
        session_factory=session_factory
    )

    scene_segmentation_use_case = providers.Factory(
        SceneSegmentationUseCase,
        unit_of_work=scene_segmentation_unit_of_work,
        text_extractor=text_extractor,
        scene_analysis_service=scene_analysis_service
    )
