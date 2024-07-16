from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from session_zero_api import database as db

class SpellSchool(BaseModel):
    id: Optional[str] = None
    short: str
    name: str
    description: str
    # spells: list[str] = []
    # spells: list[Spell] = []

def get_all() -> list[SpellSchool]:
    collection = db.client.session_zero.spell_schools
    schools = [SpellSchool(id=str(s["_id"]), short=s["short"], name=s["name"], description=s["description"]) for s in collection.find()]
    return schools

def get_one(school_id: str) -> SpellSchool:
    collection = db.client.session_zero.spell_schools
    school = collection.find_one({"_id": ObjectId(school_id)})
    return SpellSchool(id=str(school["_id"]), short=school["short"], name=school["name"], description=school["description"])

def get_by_short(short: str) -> SpellSchool:
    collection = db.client.session_zero.spell_schools
    school = collection.find_one({"short": short})
    return SpellSchool(id=str(school["_id"]), short=school["short"], name=school["name"], description=school["description"])