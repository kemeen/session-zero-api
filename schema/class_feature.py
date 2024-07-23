from pydantic import BaseModel

class ClassFeature(BaseModel):
    name: str
    level: int

    def from_mongo(data: dict) -> "ClassFeature":
        if data is None:
            raise ValueError("data for class feature is None!")
        
        return ClassFeature(
            name=data.get("name"),
            level=data.get("level")
        )
    