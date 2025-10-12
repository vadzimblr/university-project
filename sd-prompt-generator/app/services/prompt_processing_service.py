import logging
import sys
import time
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.entities import Story
from app.models.entities.SceneResult import SceneResult
from app.models.schemas.request import SceneRequest
from app.models.schemas.response import LLMSceneResponse, SceneResponse, Location, Character
from app.repositories.scene_repository import SceneRepository
from app.repositories.scene_result_repository import SceneResultRepository
from app.repositories.story_repository import StoryRepository
from app.services.context_service import ContextService
from app.services.llm_service import LLMService
from app.utils.database import SessionLocal


class PromptProcessingService:
    def __init__(self):
        self.db: Session = SessionLocal()
        self.story_repo = StoryRepository(self.db)
        self.scene_repo = SceneRepository(self.db)
        self.scene_result_repo = SceneResultRepository(self.db)
        self.context_service = ContextService()
        self.llm_service = LLMService()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def process(self, request_data: SceneRequest) -> SceneResponse:
        try:
            start_time = time.time()

            story = self.__create_story_if_not_exists(request_data)

            cached_scene_response = self.__get_scene_response(request_data)

            if cached_scene_response is not None:
                return cached_scene_response

            existing_scene = self.scene_repo.get_by_story_uuid_and_scene_number(
                request_data.story_uuid,
                request_data.scene_number
            )
            
            if existing_scene:
                new_scene = existing_scene
                self.logger.info(f"Reusing existing scene {existing_scene.id}")
            else:
                try:
                    new_scene = self.scene_repo.create_from_request(request_data)
                    self.logger.info(f"Created new scene {new_scene.id}")
                except IntegrityError:
                    self.db.rollback()
                    new_scene = self.scene_repo.get_by_story_uuid_and_scene_number(
                        request_data.story_uuid,
                        request_data.scene_number
                    )
                    if not new_scene:
                        raise Exception("Failed to create or retrieve scene")
                    self.logger.info(f"Race condition handled, using scene {new_scene.id}")

            previous_scene = self.__find_previous_scene(request_data, story)

            if previous_scene is not None:
                previous_context = self.context_service.get_previous_context_by_scene(previous_scene)
                self.logger.info(
                    "prompt-processing-service: %s",
                    previous_context.model_dump()
                )

                llm_response = self.llm_service.process_scene(
                    request_data.scene_text,
                    previous_context
                )
            else:
                llm_response = self.llm_service.process_scene(request_data.scene_text, None)

            self.context_service.save_context_from_llm_response(
                llm_response = llm_response,
                request_data = request_data,
                new_scene = new_scene
            )

            processing_time = time.time() - start_time

            return self.__convert_to_scene_response(
                llm_response = llm_response,
                story_uuid = request_data.story_uuid,
                scene_number = request_data.scene_number,
                processing_time = processing_time,
                location_name = None
            )

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=e)


    def __get_scene_response(self, request_data: SceneRequest) -> Optional[SceneResponse]:
        scene = self.scene_repo.get_by_story_uuid_and_scene_number(
            request_data.story_uuid,
            request_data.scene_number
        )

        if scene is None:
            return None

        scene_result: SceneResult | None = self.scene_result_repo.get_by_scene_id(scene.id)
        if scene_result is None:
            return None

        characters = [
            Character(**char_dict) for char_dict in (scene_result.characters_data or [])
        ]

        location = Location(**scene_result.location_data) if scene_result.location_data else Location(
            name="",
            description=""
        )

        actions_text = scene_result.actions or ""

        created_at = scene_result.created_at or datetime.now()
        scene_created = getattr(scene, "created_at", None)
        if scene_created:
            processing_time = (created_at - scene_created).total_seconds()
        else:
            processing_time = 0.0

        return SceneResponse(
            story_uuid=request_data.story_uuid,
            scene_number=request_data.scene_number,
            characters=characters,
            location=location,
            actions=actions_text,
            sd_prompt=scene_result.sd_prompt or "",
            processing_time=processing_time
        )

    def __find_previous_scene(self, request_data: SceneRequest, story: Story):
        previous_scene = None

        if request_data.scene_number < 2:
            return previous_scene

        previous_scene = self.scene_repo.get_by_story_uuid_and_scene_number(
            story.uuid,
            request_data.scene_number - 1
        )

        return previous_scene

    def __create_story_if_not_exists(self, request_data: SceneRequest)->Story:
        story = self.story_repo.get_by_uuid(request_data.story_uuid)

        if story is None:
            story = self.story_repo.create(request_data.story_uuid)

        return story

    def __convert_to_scene_response(
            self,
            llm_response: LLMSceneResponse,
            story_uuid: str,
            scene_number: int,
            processing_time: float,
            location_name: str = None
    ) -> SceneResponse:

        location = Location(
            name=location_name or f"Scene {scene_number}",
            description=llm_response.location
        )

        actions_text = ". ".join(llm_response.actions)

        return SceneResponse(
            story_uuid=story_uuid,
            scene_number=scene_number,
            characters=llm_response.characters,
            location=location,
            actions=actions_text,
            sd_prompt=llm_response.sd_prompt,
            processing_time=processing_time
        )
