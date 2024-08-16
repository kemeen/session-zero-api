from fastapi import APIRouter
from config.database import character_collection, beast_collection
from api.character import Character

router = APIRouter()

@router.get("/characters/")
async def get_characters():
    characters = [{ "name": doc["name"] } for doc in character_collection.find() if "name" in doc]
    return characters

@router.get("/character/level/{character_name}")
async def get_character_level(character_name: str):
    for character in character_collection.find():
        if character.name == character_name:
            return {"name": character.name, "level": character.character_level}
    return {"message": "Character not found"}

@router.get("/beasts/")
async def get_beasts():
    beasts = [{ "name": doc["name"] } for doc in beast_collection.find() if "name" in doc]
    return beasts


# POST ROUTES
@router.post("/characters/", response_model=Character)
async def create_character(new_character: Character) -> None:
    print(dict(new_character))
    character_collection.insert_one(dict(new_character))
