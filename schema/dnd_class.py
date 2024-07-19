from pydantic import BaseModel
import pymongo
from sympy import O
from session_zero_api import database as db
from typing import Optional
from bson import ObjectId
from .class_feature import ClassFeature

class HitDice(BaseModel):
    faces: int
    number: int

    def from_mongo(data: dict) -> "HitDice":
        if data is None:
            return HitDice(faces=0, number=0)
        return HitDice(
            faces=data.get("faces"),
            number=data.get("number")
        )

class DnDClass(BaseModel):
    id: Optional[str] = None
    name: str
    proficiencies: list[str]
    sub_class_title: str
    hit_dice: Optional[HitDice] = None
    spellcasting_ability: Optional[str] = None
    features: Optional[list[ClassFeature]] = []

    def from_mongo(data: dict) -> "DnDClass":
        class_info = data["class"][0]
        if class_info is None:
            raise KeyError("class key not found in data")
        if "classFeature" in data:
            features = [ClassFeature.from_mongo(f, str(data.get("_id"))) for f in data.get("classFeature", [])]
        else:
            features = []
        
        return DnDClass(
            id=str(data.get("_id")),
            name=class_info.get("name"),
            proficiencies=class_info.get("proficiency", []),
            sub_class_title=class_info.get("subclassTitle", ""),
            spellcasting_ability=class_info.get("spellcastingAbility"),
            hit_dice=HitDice.from_mongo(class_info.get("hd")),
            features=features
        )


def get_all() -> list[DnDClass]:
    collection = db.client.session_zero.classes
    return [DnDClass.from_mongo(c) for c in collection.find(
        {"class.isSidekick": {"$ne": True}},
        {"class.name": 1, "class.proficiency": 1, "class.subclassTitle": 1, "class.spellcastingAbility": 1, "class.hd": 1}
        ).sort("class.name", pymongo.ASCENDING)]

def get_by_id(class_id: str) -> DnDClass:
    collection = db.client.session_zero.classes
    class_info = collection.find_one({"_id": ObjectId(class_id)})
    return DnDClass.from_mongo(class_info)

def get_by_name(class_name: str) -> DnDClass:
    collection = db.client.session_zero.classes
    class_info = collection.find_one(filter={"class.name": class_name})
    return DnDClass.from_mongo(class_info)

