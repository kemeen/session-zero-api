from pydantic import BaseModel, Field
from api.attributes import Attributes

class Character(BaseModel):
    name: str = ""
    # classes: list[tuple[str, int]]
    # background: str|None = None
    # race: str|None = None
    # attributes: Attributes|None = None
    # proficiency_bonus: int|None = None
    # proficiencies: list[str] = Field(description="A list of proficiencies that the character has.", default_factory=list)
    # expertise: list[str] = Field(description="A list of proficiencies that the character has expertise in.", default_factory=list)
    # saving_throws: list[str] = Field(description="A list of saving throws that the character is proficient in.", default_factory=list)

    @property
    def character_level(self):
        return sum([level for _, level in self.classes])
    
