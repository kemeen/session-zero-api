from fastapi import APIRouter
from pydantic import BaseModel
from session_zero_api.database import client

router = APIRouter(
    prefix="/spells"
)

@router.get("/")
def get_spells() -> list[Spell]:
    collection = client.session_zero.spells
    return collection.find()