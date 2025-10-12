from pydantic import BaseModel
from typing import List

class Character(BaseModel):
    name: str
    description: str

class Location(BaseModel):
    description: str

class PreviousContext(BaseModel):
    characters: List[Character]
    location: Location
    actions: List[str]
