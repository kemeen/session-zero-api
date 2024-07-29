from pydantic import BaseModel
from typing import Optional, Union

class ClassFeature(BaseModel):
    name: str
    level: int
    source: str
    srd: bool
    entries: Optional[list[Union[str, dict, list]]] = []

    @staticmethod
    def from_mongo(data: dict) -> "ClassFeature":

        return ClassFeature(
            name=data.get("name", ""),
            level=data.get("level", 0),
            source=data.get("source", "").lower(),
            srd=data.get("srd", False),
            entries=data.get("entries", [])
        )
    @staticmethod
    def from_mongo_short(data: dict) -> "ClassFeature":
        return ClassFeature(
            name=data.get("name", ""),
            level=data.get("level", 0),
            source=data.get("source", "").lower(),
            srd=data.get("srd", False),
            entries=[]
        )
    