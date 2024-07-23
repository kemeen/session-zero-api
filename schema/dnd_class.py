from re import sub
from pydantic import BaseModel
import pymongo
from pymongo.collation import Collation
from session_zero_api import database as db
from typing import Optional
from bson import ObjectId
from .class_feature import ClassFeature
from .sub_class import SubClass
import session_zero_api as sz

LOGGER = sz.get_logger(__name__)

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
    sub_classes: Optional[list[SubClass]] = []

    def from_mongo_short(data: dict) -> "DnDClass":
        class_info = data["class"][0]
        if class_info is None:
            LOGGER.exception("class key not found in data")
            raise KeyError("class key not found in data")

        LOGGER.info(f"Getting class info on {class_info.get('name')}")
        return DnDClass(
            id=str(data.get("_id")),
            name=class_info.get("name"),
            proficiencies=class_info.get("proficiency", []),
            sub_class_title=class_info.get("subclassTitle", ""),
            spellcasting_ability=class_info.get("spellcastingAbility"),
            hit_dice=HitDice.from_mongo(class_info.get("hd"))
        )
    
    def from_mongo(data: dict) -> "DnDClass":
        class_info = data["class"][0]
        if class_info is None:
            LOGGER.exception("class key not found in data")
            raise KeyError("class key not found in data")

        LOGGER.info(f"Getting class info on {class_info.get('name')}")
        return DnDClass(
            id=str(data.get("_id")),
            name=class_info.get("name"),
            proficiencies=class_info.get("proficiency", []),
            sub_class_title=class_info.get("subclassTitle", ""),
            spellcasting_ability=class_info.get("spellcastingAbility"),
            hit_dice=HitDice.from_mongo(class_info.get("hd")),
            features=[ClassFeature.from_mongo(f) for f in data.get("classFeature", [])],
            sub_classes=[SubClass.from_mongo_short(s) for s in data.get("subclass")]
        )
    
    def from_mongo_detail(data: dict, subclass: str) -> "DnDClass":
        class_info = data["class"][0]
        if class_info is None:
            LOGGER.exception("class key not found in data")
            raise KeyError("class key not found in data")

        LOGGER.info(f"Getting class info on {class_info.get('name')}")
        return DnDClass(
            id=str(data.get("_id")),
            name=class_info.get("name"),
            proficiencies=class_info.get("proficiency", []),
            sub_class_title=class_info.get("subclassTitle", ""),
            spellcasting_ability=class_info.get("spellcastingAbility"),
            hit_dice=HitDice.from_mongo(class_info.get("hd")),
            features=[ClassFeature.from_mongo(f) for f in data.get("classFeature", [])],
            sub_classes=[SubClass.from_mongo(s) for s in data.get("subclass") if s.get("name", "").lower() == subclass.lower()]
        )

def get_all() -> list[DnDClass]:
    collection = db.client.session_zero.classes
    return [DnDClass.from_mongo_short(c) for c in collection.find(
        {"class.isSidekick": {"$ne": True}},
        {"class.name": 1, "class.proficiency": 1, "class.subclassTitle": 1, "class.spellcastingAbility": 1, "class.hd": 1}
        ).sort("class.name", pymongo.ASCENDING)]

def get_by_id(class_id: str) -> DnDClass:
    collection = db.client.session_zero.classes
    class_info = collection.find_one({"_id": ObjectId(class_id)})
    return DnDClass.from_mongo(class_info)

def get_by_name(class_name: str) -> DnDClass:
    collection = db.client.session_zero.classes
    class_info = collection.find_one(filter={"class.name": class_name}, collation=Collation(locale= "en_US",strength= 1))
    return DnDClass.from_mongo(class_info)

def get_class_detail(class_name: str, sub_class_name: str) -> DnDClass:
    collection = db.client.session_zero.classes
    class_info = collection.find_one({"class.name": class_name}, collation=Collation(locale= "en_US",strength= 2))
    return DnDClass.from_mongo_detail(data=class_info, subclass=sub_class_name)

