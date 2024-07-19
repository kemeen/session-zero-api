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
            return ClassFeature(name="", description="")
        
        return ClassFeature(
            dnd_class_id=dnd_class_id,
            name=data.get("name"),
            level=data.get("level")
        )
    
    def get_all() -> list["ClassFeature"]:
collection = db.client.session_zero.classes
        return [ClassFeature.from_mongo(c.get("classFeature"), str(c.get("_id"))) for c in collection.find()]