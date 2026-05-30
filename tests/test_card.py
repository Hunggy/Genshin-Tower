"""Tests for the Card class and card database."""

import copy


def test_card_database_keys_match_name_to_key(gm):
    """All CARD_DATABASE keys must have valid card names in CARD_NAME_TO_KEY."""
    db = gm.CARD_DATABASE
    key_map = gm.CARD_NAME_TO_KEY

    missing = []
    mismatched = []
    for key, card in db.items():
        if card.name not in key_map:
            missing.append((key, card.name))
        elif key_map[card.name] != key:
            mismatched.append((key, card.name, key_map[card.name]))

    assert not missing, f"Cards missing from CARD_NAME_TO_KEY: {missing}"
    assert not mismatched, f"Mismatched keys in CARD_NAME_TO_KEY: {mismatched}"


def test_card_database_no_duplicate_names(gm):
    """No two cards in CARD_DATABASE share the same display name."""
    db = gm.CARD_DATABASE
    seen_names = {}
    for key, card in db.items():
        assert card.name not in seen_names, (
            f"Duplicate card name '{card.name}' in keys {seen_names[card.name]} and {key}"
        )
        seen_names[card.name] = key


def test_copied_card_independent(gm):
    """Copying a card from the database creates an independent instance."""
    original = copy.deepcopy(gm.CARD_DATABASE["STRIKE"])
    copy_card = copy.deepcopy(original)

    copy_card.damage = 99
    copy_card.cost = 0
    copy_card.upgraded = True

    assert original.damage != copy_card.damage, "Original damage was mutated by copy"
    assert original.cost != copy_card.cost, "Original cost was mutated by copy"
    assert not original.upgraded, "Original upgraded flag was mutated by copy"


def test_card_dict_roundtrip_basic(gm):
    """Serializing and deserializing a non-upgraded card preserves its state."""
    original = copy.deepcopy(gm.CARD_DATABASE["DEFEND"])

    data = gm.BattleManager._card_to_dict(None, original)
    restored = gm.BattleManager._card_from_dict(None, data)

    assert restored.base_name == original.base_name
    assert restored.upgraded == original.upgraded
    assert restored.is_marked == original.is_marked
    assert restored.is_temporary == original.is_temporary
    assert restored.cost == original.cost
    assert restored.damage == original.damage
    assert restored.block == original.block
    assert restored.element == original.element
    assert restored.type == original.type


def test_card_dict_roundtrip_upgraded(gm):
    """Upgraded card gets '+' suffix on name after roundtrip (expected behavior)."""
    original = copy.deepcopy(gm.CARD_DATABASE["STRIKE"])
    original.upgraded = True

    data = gm.BattleManager._card_to_dict(None, original)
    restored = gm.BattleManager._card_from_dict(None, data)

    # from_dict adds '+' suffix for upgraded cards
    expected_name = original.base_name + "+"
    assert restored.name == expected_name
    assert restored.upgraded is True
    assert restored.base_name == original.base_name


def test_card_attributes_serialization(gm):
    """All relevant card attributes survive dict roundtrip."""
    card = copy.deepcopy(gm.CARD_DATABASE["HEAVEN_FLAME"])
    card.permanent_dmg_bonus = 7

    data = gm.BattleManager._card_to_dict(None, card)
    restored = gm.BattleManager._card_from_dict(None, data)

    assert restored.permanent_dmg_bonus == card.permanent_dmg_bonus
    assert restored.base_name == card.base_name
    assert restored.hits == card.hits
    assert restored.exhaust == card.exhaust
    assert restored.retain == card.retain


def test_all_card_types_present(gm):
    """CARD_DATABASE contains at least one card of each type."""
    types_found = set()
    for card in gm.CARD_DATABASE.values():
        types_found.add(card.type)

    assert "ATTACK" in types_found
    assert "SKILL" in types_found
    assert "POWER" in types_found


def test_card_name_consistency(gm):
    """CARD_NAME_TO_KEY and CARD_DATABASE form a consistent bidirectional map."""
    db = gm.CARD_DATABASE
    key_map = gm.CARD_NAME_TO_KEY

    # Every card in DB maps to itself via name
    for key, card in db.items():
        assert key_map[card.name] == key

    # Every name in key_map maps to a card in DB
    for name, key in key_map.items():
        assert key in db, f"CARD_NAME_TO_KEY['{name}'] = '{key}' but not in CARD_DATABASE"
        assert db[key].name == name, (
            f"CARD_DATABASE['{key}'].name = '{db[key].name}' but "
            f"CARD_NAME_TO_KEY expects '{name}'"
        )
