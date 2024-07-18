from schema import race

def main():
    # get all spells as a list of Spell objects
    # all_spells = spells.get_by_school("C")

    # print the name and level of each spell
    max_spells = 5
#     for spell in all_spells[:max_spells]:
#         print(spell)

    # get a single spell by its id
    # spell_id = all_spells[0].id
    # single_spell = spells.get_one(spell_id)
    # print(single_spell)

    # get all spells as a list of SpellLookUp objects
    # all_spell_lookups = spells.get_spell_lookup()
    # for spell_lookup in all_spell_lookups[:max_spells]:
    #     print(spell_lookup)

    # get spells for bards up to level 5
    bard_spells = spell.get_spells_by_class(dnd_class="Bard", sub_class="College of Swords", level=5)
    for spell in bard_spells:
        print(spell)

if __name__ == "__main__":
    main()