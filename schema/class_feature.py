from pydantic import BaseModel
from session_zero_api import database as db
from typing import Optional
from bson import ObjectId

class ClassFeature(BaseModel):
    name: str
    level: int
    dnd_class_id: str

    def from_mongo(data: dict, dnd_class_id: str) -> "ClassFeature":
        if data is None:
            raise ValueError("data for class feature is None!")
        
        return ClassFeature(
            dnd_class_id=dnd_class_id,
            name=data.get("name"),
            level=data.get("level")
        )
    