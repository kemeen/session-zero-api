from fastapi import APIRouter
from schema import race


router = APIRouter(
    prefix="/races"
)

@router.get("/")
def get_all() -> list[race.Race]:
    return race.get_all()

# router to return a race by id
@router.get("/id/{id}")
def get_by_id(id: int) -> race.Race:
    return race.get_by_id(id)