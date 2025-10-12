import logging
import sys

from sqlalchemy.orm import Session
from app.models.entities.Scene import Scene
from app.models.schemas.internal import PreviousContext, Character, Location
from app.models.schemas.request import SceneRequest
from app.models.schemas.response import LLMSceneResponse
from app.repositories.scene_repository import SceneRepository
from app.repositories.scene_result_repository import SceneResultRepository
from app.repositories.story_character_repository import StoryCharacterRepository
from app.repositories.story_location_repository import StoryLocationRepository
from app.utils.database import SessionLocal


class ContextService:
    def __init__(self):
        self.db: Session = SessionLocal()
        self.scene_repo = SceneRepository(self.db)
        self.character_repo = StoryCharacterRepository(self.db)
        self.scene_result_repo = SceneResultRepository(self.db)
        self.location_repo = StoryLocationRepository(self.db)
        self.max_characters = 10
        self.max_locations = 5
        self.max_context_length = 2000
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def get_previous_context_by_scene(self, scene: Scene) -> PreviousContext:
        characters = self.character_repo.get_characters_in_scene(scene.id)

        characters_dto = []

        for character in characters:
            characters_dto.append(Character(
                name = character.name,
                description= character.description,
            ))

        location = self.location_repo.get_by_location_id(scene.location_id)
        scene_result = self.scene_result_repo.get_by_scene_id(scene.id)

        return PreviousContext(
            characters=characters_dto,
            location=Location(description =  location.description if location else ""),
            actions=[scene_result.actions if scene_result else ""],
        )

    def save_context_from_llm_response(
        self,
        llm_response: LLMSceneResponse,
        request_data: SceneRequest,
        new_scene: Scene
    ) -> None:
        location = self.location_repo.create_from_location_dto(
            location_dto = Location(description=llm_response.location),
            story_uuid = request_data.story_uuid,
        )
        new_scene = self.db.merge(new_scene)
        new_scene.location_id = location.id
        self.db.flush()
        self.db.commit()

        characters = llm_response.characters

        for character in characters:
            self.character_repo.create_and_add_to_scene(
                character,
                new_scene,
            )

        self.scene_result_repo.create_from_llm_response(
            new_scene.id,
            llm_response
        )
