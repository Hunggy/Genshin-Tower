"""Tests for save/load serialization roundtrip."""

import copy
from unittest.mock import patch


def _fresh_manager(gm):
    """Create a BattleManager with mock-safe defaults for save/load tests."""
    with patch.object(gm.resources, 'load_enemy_image', return_value=None):
        game = gm.BattleManager()
    game.state = "BATTLE"
    game.selected_mode = "NORMAL"
    game.is_endless = False
    game.current_wave = 5
    game.current_loop = 0
    game.player_hp = 45
    game.player_max_hp = 80
    game.energy = 2
    game.base_energy = 3
    game.player_block = 5
    game.strength = 2
    game.enemy_hp = 30
    game.enemy_max_hp = 50
    game.enemy_intent = 8
    game.enemy_vulnerable_turns = 1
    game.bloom_cores = 2
    game.turn_count = 3
    game.cards_played_this_turn = 2
    game.total_reactions = 4
    game.grass_buff = True
    game.maya_active = True
    game.pyro_damage_bonus = 3
    game.relics = ["BlizzardStrayer"]
    game.powers = ["無限迴路"]
    game.obtained_rewards = set()
    game.deck = [copy.deepcopy(gm.CARD_DATABASE["STRIKE"])]
    game.hand = [copy.deepcopy(gm.CARD_DATABASE["DEFEND"]), copy.deepcopy(gm.CARD_DATABASE["HEAVEN_FLAME"])]
    game.discard = [copy.deepcopy(gm.CARD_DATABASE["PIERCE"])]
    game.exhaust_pile = []
    game.owned_cards = []
    return game


def test_save_to_dict_produces_dict(gm):
    """save_to_dict returns a flat dict with expected top-level keys."""
    game = _fresh_manager(gm)
    data = game.save_to_dict()

    assert isinstance(data, dict)
    assert data.get("version") == gm.SAVE_VERSION
    assert "state" in data
    assert "player" in data
    assert "enemy" in data
    assert "battle" in data
    assert "deck" in data
    assert "hand" in data
    assert "discard" in data
    assert "exhaust_pile" in data
    assert "powers" in data
    assert "relics" in data


def test_save_load_preserves_player_stats(gm):
    """Roundtrip of save/load preserves core player stats."""
    game = _fresh_manager(gm)
    data = game.save_to_dict()

    game2 = _fresh_manager(gm)
    game2.load_from_dict(data)

    assert game2.player_hp == game.player_hp
    assert game2.player_max_hp == game.player_max_hp
    assert game2.energy == game.energy
    assert game2.base_energy == game.base_energy
    assert game2.player_block == game.player_block
    assert game2.strength == game.strength
    assert game2.pyro_damage_bonus == game.pyro_damage_bonus


def test_save_load_preserves_enemy_state(gm):
    """Roundtrip preserves enemy HP, intent, and status effects."""
    game = _fresh_manager(gm)
    data = game.save_to_dict()

    game2 = _fresh_manager(gm)
    game2.load_from_dict(data)

    assert game2.enemy_hp == game.enemy_hp
    assert game2.enemy_max_hp == game.enemy_max_hp
    assert game2.enemy_intent == game.enemy_intent
    assert game2.enemy_vulnerable_turns == game.enemy_vulnerable_turns
    assert game2.bloom_cores == game.bloom_cores


def test_save_load_preserves_progress(gm):
    """Roundtrip preserves wave, mode, and turn data."""
    game = _fresh_manager(gm)
    data = game.save_to_dict()

    game2 = _fresh_manager(gm)
    game2.load_from_dict(data)

    assert game2.current_wave == game.current_wave
    assert game2.selected_mode == game.selected_mode
    assert game2.is_endless == game.is_endless
    assert game2.turn_count == game.turn_count
    assert game2.cards_played_this_turn == game.cards_played_this_turn
    assert game2.total_reactions == game.total_reactions


def test_save_load_preserves_deck_hand_discard(gm):
    """Roundtrip preserves card names and upgrade states in all piles."""
    game = _fresh_manager(gm)
    # Upgrade one card for testing
    game.hand[0].upgraded = True

    data = game.save_to_dict()

    game2 = _fresh_manager(gm)
    game2.load_from_dict(data)

    assert len(game2.deck) == len(game.deck)
    assert len(game2.hand) == len(game.hand)
    assert len(game2.discard) == len(game.discard)

    # Check upgraded card restored correctly
    assert game2.hand[0].upgraded is True
    assert game2.hand[0].base_name == game.hand[0].base_name


def test_save_load_preserves_mechanics(gm):
    """Roundtrip preserves special mechanic flags."""
    game = _fresh_manager(gm)
    data = game.save_to_dict()

    game2 = _fresh_manager(gm)
    game2.load_from_dict(data)

    assert game2.grass_buff == game.grass_buff
    assert game2.maya_active == game.maya_active


def test_save_load_preserves_relics_and_powers(gm):
    """Roundtrip preserves relics and active powers."""
    game = _fresh_manager(gm)
    data = game.save_to_dict()

    game2 = _fresh_manager(gm)
    game2.load_from_dict(data)

    assert game2.relics == game.relics
    assert game2.powers == game.powers


def test_save_version_field_present(gm):
    """Save data always includes a version number for migration support."""
    game = _fresh_manager(gm)
    data = game.save_to_dict()

    assert "version" in data
    assert isinstance(data["version"], int)
    assert data["version"] >= 1
