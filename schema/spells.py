from pydantic import BaseModel
from session_zero_api import database as db
from typing import Optional
from bson import ObjectId
from .spell_school import SpellSchool, get_by_short

class CastTime(BaseModel):
    number: int
    unit: str

class Spell(BaseModel):
    id: Optional[str] = None
    name: str
    level: int
    school: Optional[SpellSchool] = None
    times: Optional[list[CastTime]] = []

class SpellLookUp(BaseModel):
    name: str
    classes: list[str]
    sub_classes: list[tuple[str, str]]


def get_all() -> list[Spell]:
    collection = db.client.session_zero.spells
    spell_dicts = collection.find()
    spells = [Spell(id=str(s["_id"]), name=s["name"], level=s["level"]) for s in spell_dicts]
    # spells = [Spell(name=s["name"], level=s["level"]) for s in collection.find()]
    return spells

def get_one(spell_id: str) -> Spell:
    collection = db.client.session_zero.spells
    spell = collection.find_one({"_id": ObjectId(spell_id)})
    school = get_by_short(spell["school"])
    return Spell(
        id=str(spell["_id"]), 
        name=spell["name"], 
        level=spell["level"], 
        school=school,
        times=spell["time"]
        )

def get_by_school(school: str) -> list[Spell]:
    collection = db.client.session_zero.spells
    return [Spell(id=str(s["_id"]), name=s["name"], level=s["level"]) for s in collection.find({"school": school})]

def get_spell_lookup() -> list[SpellLookUp]:
    collection = db.client.session_zero.spell_lookup
    spell_lookups = []
    for entry in collection.find():
        name = entry["name"]
        classes = [c for classes_dict in entry["class"].values() for c in classes_dict] if entry.get("class") else []
        sub_classes = get_sub_classes_from_spell_lookup(entry["subclass"]) if entry.get("subclass") else []
        spell_lookups.append(SpellLookUp(name=name, classes=classes, sub_classes=sub_classes))
    return spell_lookups

def filter_spells(filter_dict: dict) -> list[Spell]:
    collection = db.client.session_zero.spells
    return [Spell(id=str(s["_id"]), name=s["name"], level=s["level"]) for s in collection.find(filter_dict)]

def get_sub_classes_from_spell_lookup(sub_class_dict: dict, allowed_books: list[str]=None) -> list[str]:
    sub_classes = []
    for book, dnd_class in sub_class_dict.items():
        if allowed_books and book not in allowed_books:
            continue
        for dnd_class, dnd_class_dict in dnd_class.items():
            for sub_book, sub_book_dict in dnd_class_dict.items():
                if allowed_books and sub_book not in allowed_books:
                    continue
                for sub_class, sub_class_dict in sub_book_dict.items():
                    sub_classes.append((dnd_class, sub_class_dict["name"]))
    return sub_classes



