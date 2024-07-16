from fastapi import APIRouter
from schema import spell


router = APIRouter(
    prefix="/spells"
)

@router.get("/name")
def get_spells_by_name(name: str, source: str) -> spell.Spell:
    return spell.get_by_name(name=name, source=source)

@router.get("/class_and_level")
def get_spells_by_class_and_level(class_name: str, sub_class: str, level: int) -> list[spell.Spell]:
    return spell.get_spells_by_class(dnd_class=class_name, sub_class=sub_class, level=level)

@router.get("/")
def get_spells() -> list[spell.Spell]:
    return spell.get_all()