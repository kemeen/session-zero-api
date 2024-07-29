from typing import Optional, Protocol, Union
from pydantic import BaseModel

EntryType = Gen

class Entry(Protocol):
    def from_mongo(data: dict, name: str):
        ...

class TextEntry(BaseModel):
    text: str

    @staticmethod
    def from_mongo(text: str) -> "TextEntry":
        return TextEntry(
            text=text
        )

class GroupEntry(BaseModel):
    entries: list[Union["TextEntry", "ListEntry"]]
    name: Optional[str] = None

    @staticmethod
    def from_mongo(data: dict, name: str) -> "GroupEntry":
        return GroupEntry(
            entries=[get_entry(e) for e in data.get("entries", [])]
        )

class ListEntry(BaseModel):
    items: list[TextEntry]
    name: Optional[str] = None

    @staticmethod
    def from_mongo(data: dict, name: str) -> "ListEntry":
        return ListEntry(
            items=[TextEntry.from_mongo(text) for text in data.get("items", [])]
        )
    
def get_entry(data: Union[str,dict]) -> Union[TextEntry, ListEntry]:
    if not isinstance(data, (str,dict)):
        raise TypeError(f"Expected str or dict, got {type(data)}")

    if isinstance(data, str):
        return TextEntry(text=data)
    
    name = data.get("name", "")
    entry_type = data.get("type", "")

    if entry_type == "entries":
        return ListEntry.from_mongo(data=data["entries"], name=name)
    
    if entry_type == "list":
        return ListEntry.from_mongo(data=data, name=name)
    
    raise ValueError(f"Unknown entry type {entry_type}")

def get_entries(data: list[Union[str,dict]]) -> list[Union[TextEntry, ListEntry]]:
    return [get_entry(e) for e in data]