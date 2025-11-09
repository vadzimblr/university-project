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
from app.repositories.outbox_repository import OutboxRepository
from app.services.context_service import ContextService
from app.services.llm_service import LLMService
from app.utils.database import SessionLocal
from app.events.prompt_extracted_event import PromptExtractedEvent, PreviousContext


class PromptProcessingService:
    def __init__(self):
        self.db: Session = SessionLocal()
        self.story_repo = StoryRepository(self.db)
        self.scene_repo = SceneRepository(self.db)
        self.scene_result_repo = SceneResultRepository(self.db)
        self.outbox_repo = OutboxRepository(self.db)
        self.context_service = ContextService()
        self.llm_service = LLMService()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def process(self, request_data: SceneRequest) -> SceneResponse:
        try:
            start_time = time.time()

            story = self.__create_story_if_not_exists(request_data)

            existing_scene = self.scene_repo.get_by_story_uuid_and_scene_number(
                request_data.story_uuid,
                request_data.scene_number
            )
            
            if existing_scene:
                scene_result = self.scene_result_repo.get_by_scene_id(existing_scene.id)
                if scene_result and scene_result.sd_prompt:
                    self.logger.info(f"Scene {existing_scene.id} already processed, publishing outbox event")
                    
                    enriched_prompt = self.__enrich_prompt_from_scene_result(scene_result)
                    
                    previous_scene = self.__find_previous_scene(request_data, story)
                    
                    self.__publish_prompt_extracted_event(
                        story_uuid=request_data.story_uuid,
                        scene_number=request_data.scene_number,
                        prompt=enriched_prompt,
                        scene_id=existing_scene.id,
                        previous_scene=previous_scene
                    )
                    
                    cached_scene_response = self.__get_scene_response(request_data)
                    if cached_scene_response is not None:
                        return cached_scene_response
            
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

            enriched_prompt = self.__enrich_prompt_with_context(llm_response)
            
            self.__publish_prompt_extracted_event(
                story_uuid=request_data.story_uuid,
                scene_number=request_data.scene_number,
                prompt=enriched_prompt,
                scene_id=new_scene.id,
                previous_scene=previous_scene
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

    def __enrich_prompt_with_context(self, llm_response) -> str:
        parts = []
        
        if llm_response.sd_prompt:
            parts.append(llm_response.sd_prompt)
        
        if llm_response.characters:
            characters_desc = []
            for char in llm_response.characters:
                char_parts = [char.name]
                if char.description:
                    char_parts.append(char.description)
                if char.appearance:
                    char_parts.append(char.appearance)
                characters_desc.append(", ".join(char_parts))
            
            if characters_desc:
                parts.append("Characters: " + "; ".join(characters_desc))
        
        if llm_response.location:
            parts.append(f"Location: {llm_response.location}")
        
        if llm_response.actions:
            actions_str = ", ".join(llm_response.actions) if isinstance(llm_response.actions, list) else llm_response.actions
            parts.append(f"Actions: {actions_str}")
        
        enriched_prompt = ". ".join(parts)
        
        return enriched_prompt
    
    def __enrich_prompt_from_scene_result(self, scene_result: SceneResult) -> str:
        parts = []
        
        if scene_result.sd_prompt:
            parts.append(scene_result.sd_prompt)
        
        if scene_result.characters_data:
            characters_desc = []
            for char in scene_result.characters_data:
                char_parts = [char.get('name', '')]
                if char.get('description'):
                    char_parts.append(char['description'])
                if char.get('appearance'):
                    char_parts.append(char['appearance'])
                characters_desc.append(", ".join(filter(None, char_parts)))
            
            if characters_desc:
                parts.append("Characters: " + "; ".join(characters_desc))
        
        if scene_result.location_data and scene_result.location_data.get('name'):
            location_name = scene_result.location_data['name']
            parts.append(f"Location: {location_name}")
        
        if scene_result.actions:
            parts.append(f"Actions: {scene_result.actions}")
        
        enriched_prompt = ". ".join(parts)
        
        return enriched_prompt
    
    def __publish_prompt_extracted_event(
            self,
            story_uuid: str,
            scene_number: int,
            prompt: str,
            scene_id: int,
            previous_scene
    ):
        try:
            previous_contexts = []
            
            if previous_scene:
                for i in range(min(3, scene_number)):
                    prev_scene_number = scene_number - i - 1
                    if prev_scene_number > 0:
                        prev_scene = self.scene_repo.get_by_story_uuid_and_scene_number(
                            story_uuid, prev_scene_number
                        )
                        if prev_scene:
                            prev_result = self.scene_result_repo.get_by_scene_id(prev_scene.id)
                            if prev_result and prev_result.sd_prompt:
                                previous_contexts.append(
                                    PreviousContext(
                                        story_uuid=story_uuid,
                                        scene_number=prev_scene_number,
                                        prompt=prev_result.sd_prompt
                                    )
                                )
            
            event = PromptExtractedEvent(
                story_uuid=story_uuid,
                scene_number=scene_number,
                prompt=prompt,
                scene_id=scene_id,
                previous_contexts=previous_contexts
            )
            
            self.outbox_repo.create_event(event, session=self.db)
            self.db.commit()
            
            self.logger.info(
                f"Created PromptExtractedEvent in outbox: story_uuid={story_uuid}, "
                f"scene_number={scene_number}"
            )
        except Exception as e:
            self.logger.error(f"Failed to publish PromptExtractedEvent: {e}")

            import traceback
            self.logger.error(traceback.format_exc())

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
