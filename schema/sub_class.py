from pydantic import BaseModel
from typing import Optional
import re
from schema import spell
# from .class_feature import ClassFeature
import session_zero_api as sz

LOGGER = sz.get_logger(__name__)

class SubClass(BaseModel):
    name: str
    short_name: Optional[str] = ""
    spells: Optional[dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]] = {}
    cantrips_progression: Optional[list[int]] = []
    spell_progression: Optional[list[int]] = []
    # features: Optional[list[ClassFeature]] = []

    def from_mongo(data: dict) -> "SubClass":

        spells = parse_spells(data.get("additionalSpells", []))
        LOGGER.info(data.get("className"))

        return SubClass(
            name=data.get("name", ""),
            short_name=data.get("shortName", ""),
            spells=spells,
            cantrips_progression=data.get("cantripProgression", []),
            spell_progression=data.get("spellsKnownProgression", []),
            # features=[ClassFeature.from_mongo(f, parent_id) for f in data.get("subclassFeatures", [])]
        )

    def from_mongo_short(data: dict, subclass: str = "") -> "SubClass":
        LOGGER.info(f"Getting short subclass info on {data.get('className')} subclass {data.get('name')}")
        return SubClass(
            name=data.get("name", ""),
            short_name=data.get("shortName", ""),
        )
    
def parse_spells(data: dict) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:
    
    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}
    
    for spell_data in data:
        spell_state_generic = {}
        group = spell_data.get("name", "")
        if group:
            spell_state_generic["group"] = group
            LOGGER.info(f"Parsing spells in group {group}")

        ability = spell_data.get("ability", "")
        if ability:
            spell_state_generic["ability"] = ability
            LOGGER.info(f"Ability: {ability}")

        resource_name = spell_data.get("resourceName", "")
        if resource_name:
            spell_state_generic["resource_name"] = resource_name
            LOGGER.info(f"resource: {resource_name}")

        for spell_type, spell_items in spell_data.items():
            spell_state = spell_state_generic.copy()
            if spell_type in ["name", "ability", "resourceName"]:
                continue
            if spell_type not in ["innate", "prepared", "known", "expanded"]:
                raise ValueError(f"Unknown spell type: {spell_type}")
            
            if spell_type == "innate":
                spell_state["innate"] = True
                LOGGER.info("Parsing innate spells")
                new_spells = parse_innate_spells(data=spell_items, group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells=new_spells)
                LOGGER.info(spells)
                continue

            if spell_type == "prepared":
                spell_state["prepared"] = True
                LOGGER.info("Adding Preparing spells")
                new_spells = parse_prepared_spells(data=spell_items, group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells=new_spells)
                LOGGER.info(spells)
                continue

            if spell_type == "known":
                spell_state["known"] = True
                LOGGER.info("Adding Known spells")
                new_spells = parse_known_spells(data=spell_items, group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells=new_spells)
                LOGGER.info(spells)
                continue

            if spell_type == "expanded":
                spell_state["expanded"] = True
                LOGGER.info("Expanding spell list")
                new_spells = parse_expanded_spells(data=spell_items, group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells=new_spells)
                LOGGER.info(spells)
                continue

    return spells


def parse_innate_spells(data: dict, group: str, spell_state: dict[str,bool|str]={}) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:
    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}

    for level, level_data in data.items():
        if "name" in level_data:
            group = level_data["name"]

        if isinstance(level_data, list):
            new_spells = get_spells_from_spell_list(spell_names=level_data, group=group, spell_state=spell_state)
            spells = update_spells_dict(spells=spells, new_spells={int(level): new_spells})
            continue
        
        for spell_type, spell_names in level_data.items():

            if spell_type not in ["ritual", "daily", "resource"]:
                LOGGER.exception(f"Unknown spell type: {spell_type}")
                raise ValueError(f"Unknown spell type: {spell_type}")
            
            if spell_type == "resource":
                new_spells = parse_resource_spells(data=spell_names, level=int(level), group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells=new_spells)
                continue

            if spell_type == "daily":
                new_spells = parse_daily_spells(data=spell_names, level=int(level), group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells=new_spells)
                continue
            
            if spell_type == "ritual":
                spell_state["ritual"] = True
                new_spells = parse_ritual_spells(data=spell_names, level=int(level), group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells=new_spells)
                continue
    return spells

def parse_resource_spells(data: dict, level: int, group: str, spell_state: dict[str,bool|str]={}) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:
    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}
    
    for amount, spell_names in data.items():
        spell_state["resource_amount"] = amount
        new_spells = get_spells_from_spell_list(spell_names=spell_names, group=group, spell_state=spell_state)
        spells = update_spells_dict(spells=spells, new_spells={level: new_spells})
    
    return spells


def parse_daily_spells(data: dict, level: int, group: str, spell_state: dict[str,bool|str]={}) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:
    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}

    for uses, spell_names in data.items():

        if not isinstance(spell_names, list):
            LOGGER.exception(f"Daily spells not implemented for dict with key {uses}")
            raise NotImplementedError(f"Daily spells not implemented for dict with key {uses}")        

        spell_state["daily_uses"] = uses
        new_spells = get_spells_from_spell_list(spell_names=spell_names, group=group, spell_state=spell_state)
        spells = update_spells_dict(spells=spells, new_spells={level: new_spells})
        continue

    return spells

def parse_ritual_spells(data: list[str|dict], level: int, group: str, spell_state: dict[str,bool|str]={}) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:

    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}
    new_spells = get_spells_from_spell_list(spell_names=data, group=group, spell_state=spell_state)
    spells = update_spells_dict(spells=spells, new_spells={level: new_spells})

    return spells


def parse_prepared_spells(data: dict, group: str, spell_state: dict[str,bool|str]={}) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:

    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}

    for level, level_data in data.items():
        # level_data is asumed to be a list of spell names
        if not isinstance(level_data, list):
            LOGGER.exception(f"Prepared spells not implemented for dict with key {level}")
            raise NotImplementedError(f"Prepared spells not implemented for dict with key {level}")        

        new_spells = get_spells_from_spell_list(spell_names=level_data, group=group, spell_state=spell_state)
        spells = update_spells_dict(spells=spells, new_spells={int(level): new_spells})
    return spells

def parse_known_spells(data: dict, group: str, spell_state: dict[str,bool|str]={}) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:
    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}

    for level, level_data in data.items():
        if isinstance(level_data, list):
            new_spells = get_spells_from_spell_list(spell_names=level_data, group=group, spell_state=spell_state)
            spells = update_spells_dict(spells=spells, new_spells={int(level): new_spells})
            continue

        for spell_type, spell_data in level_data.items():

            if spell_type not in  ["_", "daily"]:
                LOGGER.exception(f"Known spells not implemented for dict with key {spell_type}")
                raise NotImplementedError(f"Known spells not implemented for dict with key {spell_type}")

            if spell_type == "_":
                new_spells = get_spells_from_spell_list(spell_names=spell_data, group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells={int(level): new_spells})
                continue

            if spell_type == "daily":
                new_spells = parse_daily_spells(data=spell_data, level=int(level), group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells=new_spells)
                continue

    return spells

def parse_expanded_spells(data: dict, group: str, spell_state: dict[str,bool|str]={}) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:

    spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]] = {}

    for level, level_data in data.items():
        if "name" in level_data:
            group = level_data["name"]

        if level.startswith("s") and len(level) == 2:
            level = 1

        if isinstance(level_data, list):
            new_spells = get_spells_from_spell_list(spell_names=level_data, group=group, spell_state=spell_state)
            spells = update_spells_dict(spells=spells, new_spells={int(level): new_spells})
            continue

        for spell_type, spell_names in level_data.items():
            if spell_type == "all":
                if isinstance(spell_names, str):
                    spell_names = [{"choose": spell_names}]
                new_spells = get_spells_from_spell_list(spell_names=spell_names, group=group, spell_state=spell_state)
                spells = update_spells_dict(spells=spells, new_spells={int(level): new_spells})
                continue

            LOGGER.exception(f"Expanded spells not implemented for dict with key {spell_type}")
            raise NotImplementedError(f"Expanded spells not implemented for dict with key {spell_type}")

    return spells

def get_spells_from_spell_list(spell_names: list[str|dict], group: str, spell_state: dict[str,bool|str]={}) -> dict[str,list[spell.Spell]|list[spell.SpellChoice]]:
    spells = {"spell_choices":[], "spells":[]}

    for spell_name in spell_names:
        if not isinstance(spell_name, (str, dict)):
            LOGGER.exception(f"Unknown type of spell input: {spell_name}")
            raise ValueError(f"Unknown spell name: {spell_name}")
        
        if isinstance(spell_name, dict):
            if "choose" in spell_name or "all" in spell_name:
                spells["spell_choices"].append(parse_spell_choice(spell_name, group=group, spell_state=spell_state))
                continue
            else:
                LOGGER.exception(f"Unknown type of spell input: {spell_name}")
                raise ValueError(f"Unknown spell name: {spell_name}")
            
        if isinstance(spell_name, str):
            s = parse_spell_name(spell_name, group=group, spell_state=spell_state)
            spells["spells"].append(s)
            continue
        
        LOGGER.exception(f"Unknown type of spell input: {spell}")
        raise TypeError(f"Unknown type of spell input: {spell_name}")
    return spells

def parse_spell_name(spell_name: str, group: str, spell_state: dict[str,bool|str]={}) -> spell.Spell:
    pattern = re.compile(r"(?P<spell_name>[/'\w\s]+)\|?(?P<source>\w+)?#?(?P<complication>c)?")
    match = pattern.match(spell_name)

    if match is None:
        LOGGER.exception(f"Unknown spell name format: {spell_name}")
        raise ValueError(f"Unknown spell name format: {spell_name}")
    
    name = match.group("spell_name")
    source = match.group("source").lower() if match.group("source") else ""
    complication = match.group("complication").lower() if match.group("complication") else ""
    LOGGER.info(f"Getting spell {name} with source {source} and complication {complication}")

    try:
        s = spell.get_by_name(name=name)
    except ValueError:
        LOGGER.exception(f"Spell not found with name: {spell_name}")
        raise ValueError(f"Spell not found with name: {spell_name}")
    spell_state.update({"custom": complication == "c", "group": group, "source": source})
    s = update_spell_state(s, spell_state)
    return s

def parse_spell_choice(data: dict, group: str, spell_state: dict[str,bool|str]={}) -> spell.SpellChoice:
    return spell.SpellChoice.from_mongo(data=data, group=group)

def update_spells_dict(spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]], new_spells: dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]) -> dict[int,dict[str,list[spell.Spell]|list[spell.SpellChoice]]]:
    for level, level_data in new_spells.items():
        if level in spells:
            for spell_type, spell_list in level_data.items():
                if spell_type in spells[level]:
                    spells[level][spell_type].extend(spell_list)
                else:
                    spells[level][spell_type] = spell_list
        else:
            spells[level] = level_data
    return spells

def update_spell_state(spell: spell.Spell, state: dict) -> spell.Spell:
    LOGGER.info(f"Updating spell {spell.name} with state {state}")
    if "ritual" in state:
        spell.is_ritual = state["ritual"]
    if "prepared" in state:
        spell.is_prepared = state["prepared"]
    if "innate" in state:
        spell.is_innate = state["innate"]
    if "known" in state:
        spell.is_known = state["known"]
    if "expanded" in state:
        spell.is_expanded = state["expanded"]
    if "custom" in state:
        spell.is_custom = state["custom"]
    if "group" in state:
        spell.group = state["group"]
    if "daily_uses" in state:
        spell.daily_uses = int(state["daily_uses"])
    if "ability" in state:
        spell.ability = state["ability"]
    if "resource_name" in state:
        spell.resource_name = state["resource_name"]
    if "resource_amount" in state:
        spell.resource_amount = int(state["resource_amount"])
    if "source" in state and state["source"]:
        spell.source = state["source"].lower()

    return spell
