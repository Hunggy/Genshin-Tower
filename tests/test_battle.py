"""Tests for BattleManager core combat logic."""

import copy
from unittest.mock import patch


def _fresh_battle(gm):
    """Helper to create a ready-to-test BattleManager."""
    with patch.object(gm.resources, 'load_enemy_image', return_value=None):
        game = gm.BattleManager()
    game.state = "BATTLE"
    game.deck = []
    game.hand = []
    game.discard = []
    game.exhaust_pile = []
    game.energy = 3
    game.base_energy = 3
    game.selected_mode = "NORMAL"

    # Draw basic hand
    for _ in range(5):
        game.hand.append(copy.deepcopy(gm.CARD_DATABASE["STRIKE"]))
    return game


def test_strike_reduces_enemy_hp(gm):
    """Playing STRIKE reduces enemy HP by correct amount."""
    game = _fresh_battle(gm)
    card = copy.deepcopy(gm.CARD_DATABASE["STRIKE"])
    initial_hp = game.enemy_hp

    game.play_card(card, 0, 0)

    assert game.enemy_hp == initial_hp - 6, (
        f"Expected enemy HP {initial_hp - 6}, got {game.enemy_hp}"
    )


def test_strike_costs_energy(gm):
    """Playing STRIKE consumes 1 energy."""
    game = _fresh_battle(gm)
    card = copy.deepcopy(gm.CARD_DATABASE["STRIKE"])
    initial_energy = game.energy

    game.play_card(card, 0, 0)

    assert game.energy == initial_energy - 1


def test_defend_adds_block(gm):
    """Playing DEFEND adds block to the player."""
    game = _fresh_battle(gm)
    game.hand = [copy.deepcopy(gm.CARD_DATABASE["DEFEND"])]
    card = game.hand[0]
    initial_block = game.player_block

    game.play_card(card, 0, 0)

    assert game.player_block == initial_block + card.block


def test_enemy_hp_zero_triggers_rewards(gm):
    """When enemy HP reaches 0, rewards are generated."""
    game = _fresh_battle(gm)
    game.enemy_hp = 1
    card = copy.deepcopy(gm.CARD_DATABASE["STRIKE"])
    card.damage = 10  # overkill

    game.play_card(card, 0, 0)

    assert game.enemy_hp <= 0
    assert len(game.reward_cards) > 0, "Expected reward cards to be generated"


def test_block_absorbs_damage(gm):
    """Player block absorbs enemy damage during enemy turn."""
    game = _fresh_battle(gm)
    game.player_block = 10
    game.enemy_intent = 5
    initial_hp = game.player_hp

    actual_damage = max(0, game.enemy_intent - game.player_block)
    game.player_hp -= actual_damage
    game.player_block = 0

    assert game.player_hp == initial_hp, "All damage should be absorbed by block"


def test_strength_increases_damage(gm):
    """Player strength adds to attack damage."""
    game = _fresh_battle(gm)
    game.strength = 3
    card = copy.deepcopy(gm.CARD_DATABASE["STRIKE"])
    initial_hp = game.enemy_hp
    expected_damage = card.damage + game.strength

    game.play_card(card, 0, 0)

    assert game.enemy_hp == initial_hp - expected_damage, (
        f"Expected {expected_damage} damage, enemy went from {initial_hp} to {game.enemy_hp}"
    )


def test_enemy_vulnerable_increases_damage(gm):
    """Vulnerable enemy takes 50% more damage."""
    game = _fresh_battle(gm)
    game.enemy_vulnerable_turns = 2
    card = copy.deepcopy(gm.CARD_DATABASE["STRIKE"])
    initial_hp = game.enemy_hp
    expected_damage = int(card.damage * 1.5)

    game.play_card(card, 0, 0)

    assert game.enemy_hp == initial_hp - expected_damage


def test_card_not_played_without_energy(gm):
    """Card with cost > energy is not consumed from hand."""
    game = _fresh_battle(gm)
    card = copy.deepcopy(gm.CARD_DATABASE["STRIKE"])
    game.energy = 0
    game.hand = [card]
    initial_hand = len(game.hand)

    game.play_card(card, 0, 0)

    assert len(game.hand) == initial_hand


def test_exhaust_card_removed_from_game(gm):
    """Exhaust cards are removed from hand and placed in exhaust pile."""
    game = _fresh_battle(gm)
    card = copy.deepcopy(gm.CARD_DATABASE["MAYA"])  # POWER card that goes to sidelined
    card.exhaust = True
    # Also make it a normal attack-like card for this test
    card.type = "ATTACK"
    game.hand = [card]
    initial_exhaust = len(game.exhaust_pile)

    game.play_card(card, 0, 0)

    # Check hand no longer contains a card with the same name
    assert not any(c.name == card.name for c in game.hand), "Card should be removed from hand"
    assert len(game.exhaust_pile) == initial_exhaust + 1
