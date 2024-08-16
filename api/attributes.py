from pydantic import BaseModel

class Attributes(BaseModel):
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

#TODO implement functions or static methods to generate attribute sets