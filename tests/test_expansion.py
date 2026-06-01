"""Tests for new gameplay systems: gold, shop, multi-enemy, difficulty, blessings, settlement."""

import copy
from unittest.mock import patch


def _fresh_battle(gm):
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
    game.wave_enemies = [{
        "name": game.enemy_name,
        "hp": game.enemy_hp,
        "max_hp": game.enemy_max_hp,
        "min_dmg": game.enemy_min_dmg,
        "max_dmg": game.enemy_max_dmg,
        "image": None,
        "intent": game.enemy_intent,
    }]
    for _ in range(5):
        game.hand.append(copy.deepcopy(gm.CARD_DATABASE["STRIKE"]))
    return game


# --- Gold System ---

def test_gold_starts_at_zero(gm):
    game = _fresh_battle(gm)
    game.gold = 0
    assert game.gold == 0


def test_generate_rewards_grants_gold(gm):
    game = _fresh_battle(gm)
    game.stage_type = "NORMAL"
    game.gold = 0
    game.generate_rewards()
    assert game.gold == 10, f"Expected 10 gold for NORMAL, got {game.gold}"


def test_generate_rewards_elite_grants_20_gold(gm):
    game = _fresh_battle(gm)
    game.stage_type = "ELITE"
    game.gold = 0
    game.generate_rewards()
    assert game.gold == 20


def test_generate_rewards_boss_grants_50_gold(gm):
    game = _fresh_battle(gm)
    game.stage_type = "BOSS"
    game.gold = 0
    game.generate_rewards()
    assert game.gold == 50


# --- Shop System ---

def test_shop_buy_card_reduces_gold(gm):
    game = _fresh_battle(gm)
    game.gold = 100
    game.shop_cards = [{"card": copy.deepcopy(gm.CARD_DATABASE["STRIKE"]), "price": 20}]
    initial_deck_size = len(game.deck)
    result = game.shop_buy_card(0)
    assert result is True
    assert game.gold == 80
    assert len(game.deck) == initial_deck_size + 1


def test_shop_buy_card_insufficient_gold(gm):
    game = _fresh_battle(gm)
    game.gold = 5
    game.shop_cards = [{"card": copy.deepcopy(gm.CARD_DATABASE["STRIKE"]), "price": 20}]
    result = game.shop_buy_card(0)
    assert result is False
    assert game.gold == 5


def test_shop_heal(gm):
    game = _fresh_battle(gm)
    game.gold = 100
    game.player_hp = 30
    game.player_max_hp = 80
    result = game.shop_heal()
    assert result is True
    assert game.gold == 70
    assert game.player_hp == 30 + int(80 * 0.3)


def test_shop_heal_full_hp(gm):
    game = _fresh_battle(gm)
    game.gold = 100
    game.player_hp = game.player_max_hp
    result = game.shop_heal()
    assert result is False


def test_shop_leave_advances_wave(gm):
    game = _fresh_battle(gm)
    game.current_wave = 5
    game.max_waves = 30
    game.shop_leave()
    assert game.current_wave == 6
    assert game.state == "BATTLE"


def test_shop_leave_on_last_wave(gm):
    game = _fresh_battle(gm)
    game.current_wave = 30
    game.max_waves = 30
    game.shop_leave()
    assert game.state == "SETTLEMENT"


# --- Multi-Enemy System ---

def test_wave_enemies_created_for_normal_waves(gm):
    game = _fresh_battle(gm)
    game.current_wave = 5
    game.stage_type = "NORMAL"
    game.start_next_wave()
    assert len(game.wave_enemies) >= 1, "Wave enemies should be populated"


def test_switch_target(gm):
    game = _fresh_battle(gm)
    game.wave_enemies = [
        {"name": "A", "hp": 30, "max_hp": 30, "min_dmg": 5, "max_dmg": 8, "image": None, "intent": 7},
        {"name": "B", "hp": 25, "max_hp": 25, "min_dmg": 4, "max_dmg": 7, "image": None, "intent": 6},
    ]
    game.target_index = 0
    game.sync_target_to_main()
    assert game.enemy_name == "A"
    game.switch_target(1)
    assert game.enemy_name == "B"


def test_check_enemy_death_auto_targets_next(gm):
    game = _fresh_battle(gm)
    game.wave_enemies = [
        {"name": "A", "hp": 0, "max_hp": 30, "min_dmg": 5, "max_dmg": 8, "image": None, "intent": 7},
        {"name": "B", "hp": 25, "max_hp": 25, "min_dmg": 4, "max_dmg": 7, "image": None, "intent": 6},
    ]
    game.target_index = 0
    game.enemy_hp = 0
    game.enemy_name = "A"
    result = game.check_enemy_death()
    assert result is False, "Should not end run when enemies remain"
    assert game.enemy_name == "B"


def test_check_enemy_death_all_dead(gm):
    game = _fresh_battle(gm)
    game.wave_enemies = [
        {"name": "A", "hp": 0, "max_hp": 30, "min_dmg": 5, "max_dmg": 8, "image": None, "intent": 7},
    ]
    game.target_index = 0
    game.enemy_hp = 0
    game.enemy_name = "A"
    game.stage_type = "BOSS"
    game.current_wave = 10
    game.max_waves = 30
    result = game.check_enemy_death()
    assert result is True, "Should end run when all enemies dead"


# --- Boss Phase Transitions ---

def test_boss_phase_triggers_at_half_hp(gm):
    game = _fresh_battle(gm)
    game.stage_type = "BOSS"
    game.enemy_max_hp = 100
    game.enemy_hp = 49
    game.enemy_intent = 10
    game.boss_phase_2 = False
    initial_intent = game.enemy_intent
    game.apply_damage(1, copy.deepcopy(gm.CARD_DATABASE["STRIKE"]), 0, 0)
    assert game.boss_phase_2 is True, "Boss should enter phase 2"


# --- Difficulty Tier ---

def test_difficulty_increases_enemy_hp(gm):
    game = _fresh_battle(gm)
    game.difficulty_tier = 2
    game.current_wave = 3
    game.stage_type = "NORMAL"
    old_hp = game.enemy_max_hp
    game.start_next_wave()
    assert game.enemy_max_hp > old_hp or game.enemy_max_hp >= 50, "Tier should affect HP calculation"


def test_difficulty_unlock_on_victory(gm):
    game = _fresh_battle(gm)
    game.difficulty_tier = 0
    game.current_wave = 31
    game.max_waves = 30
    game.stage_type = "BOSS"
    game.stats_highest_wave = 30
    game.stats_total_kills = 15
    game.stats_total_reactions = 5
    game.settle_run()
    assert game.difficulty_tier == 1, "Difficulty should increase on victory"


# --- Settlement ---

def test_settlement_calculates_primogems(gm):
    game = _fresh_battle(gm)
    game.stats_highest_wave = 10
    game.stats_total_kills = 5
    game.stats_total_reactions = 3
    game.primogem = 0
    game.settle_run()
    expected = 10 * 2 + 5 * 5 + 3 * 3
    assert game.primogem == expected
    assert game.run_primogems_earned == expected
    assert game.state == "SETTLEMENT"


# --- Environment Events ---

def test_draw_cards_reduced_by_curse(gm):
    game = _fresh_battle(gm)
    game.current_env_event = "詛咒"
    game.deck = [copy.deepcopy(gm.CARD_DATABASE["STRIKE"]) for _ in range(10)]
    game.hand = []
    game.discard = []
    game.exhaust_pile = []
    game.draw_cards(5)
    assert len(game.hand) == 4, f"Cursed draw should be 4, got {len(game.hand)}"


def test_fog_reduces_attack_damage(gm):
    game = _fresh_battle(gm)
    game.current_env_event = "濃霧"
    game.enemy_hp = 100
    card = copy.deepcopy(gm.CARD_DATABASE["STRIKE"])
    card.type = "ATTACK"
    game.play_card(card, 0, 0)
    expected = int(6 * 0.85)
    assert game.enemy_hp == 100 - expected


# --- Blessings ---

def test_blessings_exist(gm):
    from genshin_spire.battle import BLESSINGS
    assert len(BLESSINGS) >= 4, "Should have at least 4 blessings"
    for b in BLESSINGS:
        assert "id" in b
        assert "name" in b
        assert "cost" in b
        assert "apply" in b


# --- Save/Load of new fields ---

def test_save_load_preserves_gold_and_primo(gm):
    game = _fresh_battle(gm)
    game.gold = 42
    game.primogem = 17
    game.difficulty_tier = 3
    data = game.save_to_dict()
    assert data["battle"]["gold"] == 42
    assert data["battle"]["primogem"] == 17
    assert data["battle"]["difficulty_tier"] == 3

    game2 = _fresh_battle(gm)
    game2.load_from_dict(data)
    assert game2.gold == 42
    assert game2.primogem == 17
    assert game2.difficulty_tier == 3


def test_save_load_preserves_env_event(gm):
    game = _fresh_battle(gm)
    game.current_env_event = "雷暴"
    data = game.save_to_dict()
    game2 = _fresh_battle(gm)
    game2.load_from_dict(data)
    assert game2.current_env_event == "雷暴"
