from uu import Error
from pydantic import BaseModel
from typing import Optional
from schema import spell
# from .class_feature import ClassFeature
import session_zero_api as sz

LOGGER = sz.get_logger(__name__)

class SubClass(BaseModel):
    name: str
    short_name: Optional[str] = ""
    spells: Optional[dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]] = {}
    # features: Optional[list[ClassFeature]] = []

    def from_mongo(data: dict) -> "SubClass":

        spells = parse_spells(data.get("additionalSpells", []))
        LOGGER.info(data.get("className"))

        return SubClass(
            name=data.get("name"),
            short_name=data.get("shortName", ""),
            spells=spells,
            # features=[ClassFeature.from_mongo(f, parent_id) for f in data.get("subclassFeatures", [])]
        )

    def from_mongo_short(data: dict, subclass: str = "") -> "SubClass":
        LOGGER.info(f"Getting short subclass info on {data.get('className')} subclass {data.get('name')}")
        return SubClass(
            name=data.get("name"),
            short_name=data.get("shortName", ""),
        )
    
def parse_spells(data: dict) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:
    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}
    
    for spell_data in data:
        
        group = spell_data.get("name", "")
        if group:
            LOGGER.info(f"Parsing spells in group {group}" )

        for spell_type, spell_items in spell_data.items():
            if spell_type == "name":
                continue
            if spell_type not in ["innate", "prepared", "known"]:
                raise ValueError(f"Unknown spell type: {spell_type}")
            if spell_type == "innate":
                spells.update(parse_innate_spells(spell_items, group=group))
            if spell_type == "prepared":
                spells.update(parse_prepared_spells(spell_items, group=group))
            if spell_type == "known":
                spells.update(parse_known_spells(spell_items, group=group))
    
    return spells


def parse_innate_spells(data: dict, group: str = "") -> dict[int,list[spell.Spell]]:
    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}

    for level, level_data in data.items():
        if "name" in level_data:
            group = level_data["name"]

        if isinstance(level_data, list):
            spells.update({level: get_spells_from_spell_list(spell_names=level_data, group=group)})
            continue
        
        for spell_type, spell_names in level_data.items():
            
            new_spells = get_spells_from_spell_list(spell_names=spell_names, group=group)
            for s in new_spells["spells"]:
                if spell_type not in ["ritual"]:
                    LOGGER.exception(f"Unknown spell type: {spell_type}")
                    raise ValueError(f"Unknown spell type: {spell_type}")
                s = update_spell_state(s, {"ritual": True, "group": group})
            spells.update({level: new_spells})
    return spells

def update_spell_state(spell: spell.Spell, state: dict) -> spell.Spell:
    if "ritual" in state:
        spell.is_ritual = state["ritual"]
    if "prepared" in state:
        spell.is_prepared = state["prepared"]
    if "innate" in state:
        spell.is_innate = state["innate"]
    if "known" in state:
        spell.is_known = state["known"]
    if "custom" in state:
        spell.is_custom = state["custom"]
    if "group" in state:
        spell.group = state["group"]

    return spell

def parse_prepared_spells(data: dict, group: str= "") -> dict[int,list[spell.Spell]]:
    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}

    for level, level_data in data.items():
        # level_data is asumed to be a list of spell names
        try:
            spells.update({level: get_spells_from_spell_list(spell_names=level_data, group=group)})
        except Error as e:
            LOGGER.exception(level_data)
            raise e
    return spells

def parse_known_spells(data: dict, group: str = "") -> dict[int,list[spell.Spell]]:
    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}

    for level, level_data in data.items():
        if isinstance(level_data, list):
            spells.update({level: get_spells_from_spell_list(spell_names=level_data, group=group)})
            continue
        for spell_type, spell_data in level_data.items():
            if spell_type == "_":
                spells.update({level: get_spells_from_spell_list(spell_names=spell_data, group=group)})
                continue
            raise NotImplementedError(f"Known spells not implemented for dict with key {spell_type}")
            new_spells = get_spells_from_spell_list(spell_names=level_data, group=group)
            for s in new_spells:
                s.group = data.get("name", "")
            spells.extend(new_spells)
    return spells

def get_spells_from_spell_list(spell_names: list[str], group: str = "") -> list[spell.Spell]:
    spells = {"spell_choices":[], "spells":[]}

    for spell_name in spell_names:
        if not isinstance(spell_name, (str, dict)):
            LOGGER.exception(f"Unknown type of spell input: {spell_name}")
            raise ValueError(f"Unknown spell name: {spell_name}")
        
        if isinstance(spell_name, dict):
            if "choose" in spell_name:
                spells["spell_choices"].append(parse_spell_choice(spell_name, group=group))
                continue
            else:
                LOGGER.exception(f"Unknown type of spell input: {spell_name}")
                raise ValueError(f"Unknown spell name: {spell_name}")
        if isinstance(spell_name, str):
            s = parse_spell_name(spell_name)
            spells["spells"].append(s)
            continue
        LOGGER.exception(f"Unknown type of spell input: {spell}")
        raise TypeError(f"Unknown type of spell input: {spell_name}")
    return spells

def parse_spell_name(spell_name: str, group: str = "") -> spell.Spell:

    split_name = spell_name.split("#")
    if len(split_name) > 1:
        s = spell.get_by_name(name=split_name[0])
        if split_name[1] != "c":
            LOGGER.exception(f"Unknown spell identifier: {split_name[1]}")
            raise ValueError(f"Unknown spell identifier: {split_name[1]}")
        s = update_spell_state(s, {"custom": True, "group": group})
    else:
        custom = spell_name.endswith("|")
        if custom:
            spell_name = spell_name[:-1]
        s = spell.get_by_name(name=spell_name)
        s = update_spell_state(s, {"group": group, "custom": custom})
    return s

def parse_spell_choice(data: dict, group: str = "") -> spell.SpellChoice:
    """
    {'choose': 'level=0;1;2;3'}
    "level=0|class=Druid"
    
    """

    choices_data = data.get("choose").split("|")
    choices = {}
    for choice in choices_data:
        key, value = choice.split("=")
        choices[key] = value.split(";")
    
    return spell.SpellChoice(
        levels=[int(level) for level in choices.get("level", [])],
        schools=choices.get("school", []),
        classes=choices.get("class", []),
        group=group
    )
