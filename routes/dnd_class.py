from fastapi import APIRouter
from schema import dnd_class

router = APIRouter(prefix="/class")

@router.get("/")
def get_all_classes() -> list[dnd_class.DnDClass]:
    # Logic to retrieve all classes from the database
    return dnd_class.get_all()

@router.get("/id/{class_id}")
def get_class_by_id(class_id: str) -> dnd_class.DnDClass:
    # Logic to retrieve a class from the database
    # using the class_id parameter
    return dnd_class.get_by_id(class_id=class_id)

@router.get("/name/{class_name}")
def get_class_by_name(class_name: str) -> dnd_class.DnDClass:
    # Logic to retrieve a class from the database
    # using the class_name parameter
    return dnd_class.get_by_name(class_name=class_name)

@router.get("/class_detail/")
def get_class_detail(class_name: str, sub_class_short: str) -> dnd_class.DnDClass:
    # Logic to retrieve a class from the database
    # using the class_name and sub_class_name parameters
    return dnd_class.get_class_detail(class_name=class_name, sub_class_short=sub_class_short)