from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from session_zero_api import database as db

class SpellSchool(BaseModel):
    id: Optional[str] = None
    short: str
    name: str
    description: str

    def from_mongo(data: dict) -> "SpellSchool":
        return SpellSchool(
            id=str(data.get("_id")),
            short=data.get("short"),
            name=data.get("name"),
            description=data.get("description")
        )

def get_all() -> list[SpellSchool]:
    collection = db.client.session_zero.spell_schools
    schools = [SpellSchool.from_mongo(s) for s in collection.find({}, {"short": 1, "name": 1})]
    return schools

def get_by_id(school_id: str) -> SpellSchool:
    collection = db.client.session_zero.spell_schools
    school = collection.find_one({"_id": ObjectId(school_id)})
    return SpellSchool.from_mongo(school)

def get_by_short(short: str) -> SpellSchool:
    collection = db.client.session_zero.spell_schools
    school = collection.find_one({"short": short})
    return SpellSchool.from_mongo(school)