from sqlalchemy.orm import Session, joinedload

from app.models.entities.Scene import Scene, scene_characters
from app.models.entities.StoryCharacter import StoryCharacter
from app.models.schemas.internal import Character


class StoryCharacterRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, character: Character, story_uuid: str, first_appeared_scene: int = None) -> StoryCharacter:
        story_character = StoryCharacter(
            story_uuid=story_uuid,
            name=character.name,
            description=character.description,
            first_appeared_scene=first_appeared_scene
        )
        self.db.add(story_character)
        self.db.commit()
        self.db.refresh(story_character)

        return story_character

    def add_character_to_scene(self, character_id: int, scene_id: int):
        insert_stmt = scene_characters.insert().values(
            scene_id=scene_id,
            character_id=character_id
        )
        self.db.execute(insert_stmt)
        self.db.commit()

    def get_by_story_and_name(self, story_uuid: str, name: str) -> type[StoryCharacter] | None:
        return self.db.query(StoryCharacter).filter(
            StoryCharacter.story_uuid == story_uuid,
            StoryCharacter.name == name
        ).first()

    def get_characters_in_scene(self, scene_id: int) -> list[StoryCharacter]:
        scene = self.db.query(Scene).options(joinedload(Scene.characters)).filter(Scene.id == scene_id).first()

        return scene.characters if scene else []

    def create_and_add_to_scene(self, character: Character, scene: Scene) -> StoryCharacter:
        existing_character = self.get_by_story_and_name(scene.story_uuid, character.name)

        if existing_character:
            story_character = existing_character
        else:
            story_character = self.create(
                character=character,
                story_uuid=scene.story_uuid,
                first_appeared_scene=scene.scene_number
            )

        self.add_character_to_scene(story_character.id, scene.id)

        return story_character

    def update_character_description(self, character_id: int, new_description: str) -> type[StoryCharacter] | None:
        character = self.db.query(StoryCharacter).filter(StoryCharacter.id == character_id).first()
        if character:
            character.description = new_description
            self.db.commit()
            self.db.refresh(character)

        return character

    def get_by_story(self, story_uuid: str) -> list[type[StoryCharacter]]:

        return self.db.query(StoryCharacter).filter(
            StoryCharacter.story_uuid == story_uuid
        ).all()
