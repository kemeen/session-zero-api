from schema import spells

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
    all_spell_lookups = spells.get_spell_lookup()
    for spell_lookup in all_spell_lookups[:max_spells]:
        print(spell_lookup)

if __name__ == "__main__":
    main()