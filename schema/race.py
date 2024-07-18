from pydantic import BaseModel
from session_zero_api import database as db
from typing import Optional
from bson import ObjectId

class MovementSpeed(BaseModel):
    walk: int
    swim: Optional[int] = None
    fly: Optional[int] = None
    burrow: Optional[int] = None
    climb: Optional[int] = None

    def from_mongo(data: dict|int) -> "MovementSpeed":
        if isinstance(data, int):
            return MovementSpeed.from_walk(data)
        return MovementSpeed.from_dict(data)

    def from_dict(data: dict) -> "MovementSpeed":
        if data is None:
            return MovementSpeed(walk=0)
        
        walk = data.get("walk")
        for k, v in data.items():
            if v is True:
                data[k] = walk 

        return MovementSpeed(
            walk=data.get("walk"),
            swim=data.get("swim"),
            fly=data.get("fly"),
            burrow=data.get("burrow"),
            climb=data.get("climb")
        )

    def from_walk(walk: int) -> "MovementSpeed":
        return MovementSpeed(
            walk=walk
        )

class RaceAge(BaseModel):
    mature: Optional[int] = 0
    max: Optional[int] = 0

    def from_mongo(data: dict) -> "RaceAge":
        if data is None:
            return RaceAge(mature=0, max=0)
        
        return RaceAge(
            mature=int(data.get("mature", 0)),
            max=int(data.get("max", 0))
        )

class Race(BaseModel):
    id: Optional[str] = None
    name: str
    size: list[str]
    source: str
    traits: list[str]
    speed: MovementSpeed
    age: RaceAge

    def from_mongo(data: dict) -> "Race":
        if data is None:
            raise ValueError("data is None")
        if data.get("traitTags") is None:
            data["traitTags"] = []

        return Race(
            id=str(data.get("_id")),
            name=data.get("name"),
            size=data.get("size", []),
            source=data.get("source"),
            traits=data.get("traitTags", []),
            speed=MovementSpeed.from_mongo(data.get("speed")),
            age=RaceAge.from_mongo(data.get("age"))
        )

def get_all() -> list[Race]:
    collection = db.client.session_zero.races
    races = collection.find({},{"name":1, "size": 1, "source": 1, "speed": 1, "age": 1, "traitTags": 1})
    return [Race.from_mongo(r) for r in races]

def get_by_id(id: str) -> Race:
    collection = db.client.session_zero.races
    collection.find_one({"_id": ObjectId(id)})