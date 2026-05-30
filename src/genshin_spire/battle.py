import random
import copy
import pygame

from .config import (
    SCREEN_W, SCREEN_H, SAVE_VERSION, ELEMENT_COUNTERS
)
from .resources import (
    load_enemy_image, scale_enemy,
    get_ui_font, font_main, font_desc, font_hp, font_big,
    character_images, element_icons, energy_image, shield_image, kirby_image,
    background_menu, background_battle, background_victory, particles,
)
from .card import Card, CARD_DATABASE, CARD_NAME_TO_KEY, RELIC_DATABASE
from .animation import AnimationManager, FloatText, FlashScreen, ShakeScreen
from .audio import play_bgm


class BattleManager:
    def __init__(self):
        # 基礎狀態
        self.state = "STARTUP"
        self.alpha = 0
        self.fullscreen = False
        self.volume = 0.5

        # 波次與無盡模式
        self.is_endless = False
        self.endless_loop_count = 0
        self.current_wave = 1
        self.max_waves = 30

        # 玩家基礎數值
        self.player_max_hp = 50
        self.player_hp = 50
        self.player_block = 0
        self.base_energy = 3
        self.energy = 3

        # 戰鬥日誌
        self.battle_log = []
        self.show_battle_log = True  # 預設顯示

        # 統計數據
        self.stats_total_cards_played = 0
        self.stats_total_damage_dealt = 0
        self.stats_total_damage_taken = 0
        self.stats_highest_wave = 1
        self.stats_total_kills = 0
        self.stats_total_turns = 0
        self.stats_total_reactions = 0

        # 成就系統
        self.unlocked_achievements = set()
        self.current_save_slot = 1
        self.show_slot_select = False
        self.slot_select_action = "LOAD"

        self.enemy_max_hp = 80
        self.enemy_hp = 80
        self.enemy_min_dmg = 7
        self.enemy_max_dmg = 12
        self.enemy_intent = 0
        self.enemy_name = "基礎雜兵"
        self.enemy_image = load_enemy_image(self.enemy_name)
        self.stage_type = "NORMAL"
        self.selected_mode = "NORMAL"
        self.previous_battle_state = None

        # 牌組相關
        self.deck = []
        self.hand = []
        self.discard = []
        self.exhaust_pile = []          # 本場戰鬥中已消耗的牌（波次間會併回牌庫）
        self.sidelined_power_cards = [] # 本輪已激活的能力牌實例（暫時不可抽）
        self.owned_cards = []           # 已獲得的所有牌實例（升級介面用）
        self.reward_cards = []
        self.selected_reward = None
        self.show_deck = False
        self.deck_scroll = 0
        self.max_deck_scroll = 0
        self.is_dragging_deck_scroll = False
        self.deck_sort_mode = "TYPE" # "TYPE" 或 "COST"

        # 強化界面滾動狀態
        self.upgrade_scroll = 0
        self.max_upgrade_scroll = 0
        self.is_dragging_upgrade_scroll = False
        self.show_mechanics_guide = False
        self.mechanics_scroll = 0
        self.turn_count = 0
        self.max_hand = 5
        self.obtained_rewards = []
        self.modified_cards = []

        # 特殊狀態與能力
        self.powers = []
        self.powers_with_group = {}  # 記錄每個功能牌激活時的波次組
        self.relics = []
        self.strength = 0
        self.next_turn_energy = 0
        self.attack_played_count = 0

        # 敵人狀態
        self.enemy_dot_turns = 0
        self.enemy_dot_damage = 0
        self.enemy_stun_turns = 0
        self.enemy_petrify_turns = 0
        self.enemy_frozen = False
        self.enemy_frozen_turns = 0
        self.enemy_wet = False
        self.enemy_wet_turns = 0
        self.enemy_vulnerable_turns = 0
        self.enemy_poison_turns = 0
        self.enemy_intent_type = "ATTACK"
        self.enemy_hit_shield = 0
        self.enemy_shield_element = "None"
        self.enemy_charge_turns = 0
        self.enemy_charge_max = 4
        self.enemy_scaling_strength = 0
        self.enemy_thorns = 0
        self.bloom_cores = 0

        # 交互機制狀態
        self.reactions_this_turn = 0
        self.cards_played_this_turn = 0
        self.control_resistance = 0
        self.control_count_this_turn = 0
        self.enemy_stance = "ATTACK"
        self.enemy_stance_enabled = False  # 僅部分精英/BOSS 擁有節奏姿態

        # 玩家狀態
        self.maya_active = False
        self.maya_turns = 0
        self.grass_buff = False
        self.pyro_damage_bonus = 0

        # 其他
        self.anim_queue = []
        self.jump_progress = 0
        self.animation_tick = 0       # 動態模型動畫計時器
        self.previous_state = "MAIN_MENU" # 用於從設置界面返回
        self.pending_relic = None
        self.pending_upgrade = False
        self.flash_enabled = True
        self.infinite_mode = False
        self.current_character = list(character_images.keys())[0] if character_images else "Default"
        self.selection_mode = None
        self.selection_source_card = None

        # 執行一次重置確保所有狀態正確
        self.reset_game()

    def reset_state(self):
        """將所有遊戲數據重置，但不影響物件本身的結構"""
        self.state = "MAIN_MENU"
        self.player_hp = self.player_max_hp
        self.energy = self.base_energy
        self.player_block = 0
        self.deck = []
        self.hand = []
        self.discard = []
        self.powers = []
        self.relics = []
        self.strength = 0
        self.next_turn_energy = 0
        self.attack_played_count = 0
        self.turn_count = 0
        self.current_wave = 1
        self.obtained_rewards = []
        self.is_endless = False
        self.endless_loop_count = 0

        # 重置敵人狀態
        self.enemy_hp = self.enemy_max_hp
        self.enemy_dot_turns = 0
        self.enemy_dot_damage = 0
        self.enemy_stun_turns = 0
        self.enemy_petrify_turns = 0
        self.enemy_frozen = False
        self.enemy_frozen_turns = 0
        self.enemy_wet = False
        self.enemy_vulnerable_turns = 0
        self.enemy_poison_turns = 0
        self.enemy_intent_type = "ATTACK"
        self.enemy_hit_shield = 0
        self.enemy_shield_element = "None"
        self.enemy_charge_turns = 0
        self.enemy_charge_max = 4
        self.enemy_scaling_strength = 0
        self.enemy_thorns = 0
        self.bloom_cores = 0
        self.control_resistance = 0  # 控制抗性层数
        self.control_count_this_turn = 0  # 本回合控制次数

        # 重置玩家狀態
        self.maya_active = False
        self.grass_buff = False
        self.pyro_damage_bonus = 0
        self.anim_queue = []

    def _log(self, msg):
        """追加戰鬥日誌，保留最近 50 條"""
        self.battle_log.append(msg)
        if len(self.battle_log) > 50:
            self.battle_log.pop(0)

    def check_achievements(self):
        """檢查並觸發成就"""
        ACHIEVEMENTS = {
            "first_blood":    ("初露鋒芒", lambda g: g.stats_total_kills >= 1),
            "wave_5":         ("五層突破", lambda g: g.current_wave >= 5),
            "wave_10":        ("十層突破", lambda g: g.current_wave >= 10),
            "wave_20":        ("二十層突進", lambda g: g.current_wave >= 20),
            "wave_30":        ("登頂", lambda g: g.current_wave >= 30),
            "no_damage":      ("無傷", lambda g: g.player_hp == g.player_max_hp and g.current_wave >= 5),
            "endless_1":      ("無盡探索者", lambda g: g.is_endless and g.endless_loop_count >= 1),
            "reactions_10":   ("元素新手", lambda g: g.stats_total_reactions >= 10),
            "reactions_50":   ("元素大師", lambda g: g.stats_total_reactions >= 50),
            "cards_100":      ("卡牌收藏家", lambda g: g.stats_total_cards_played >= 100),
            "damage_500":     ("重砲手", lambda g: g.stats_total_damage_dealt >= 500),
        }
        for key, (name, cond) in ACHIEVEMENTS.items():
            if key not in self.unlocked_achievements and cond(self):
                self.unlocked_achievements.add(key)
                self.anim_queue.append(("status_enemy", f"成就解鎖：{name}!", 640, 200))

    def reset_game(self):
        """完全重置遊戲到初始狀態"""
        vol = getattr(self, 'volume', 0.5)

        self.player_max_hp = 50
        self.player_hp = 50
        self.player_block = 0
        self.base_energy = 3
        self.energy = 3

        self.enemy_max_hp = 80
        self.enemy_hp = 80
        self.enemy_min_dmg = 7
        self.enemy_max_dmg = 12
        self.enemy_intent = 0
        self.enemy_name = "基礎雜兵"
        self.enemy_image = load_enemy_image(self.enemy_name)
        self.stage_type = "NORMAL"
        self.selected_mode = "NORMAL"
        self.previous_battle_state = None

        self.current_wave = 1
        self.max_waves = 30
        self.is_endless = False
        self.endless_loop_count = 0

        self.deck = []
        self.hand = []
        self.discard = []
        self.exhaust_pile = []
        self.sidelined_power_cards = []
        self.owned_cards = []
        self.reward_cards = []
        self.selected_reward = None
        self.show_deck = False
        self.show_mechanics_guide = False
        self.mechanics_scroll = 0
        self.obtained_rewards = []
        self.modified_cards = []
        self.powers = []
        self.relics = []
        self.discovery_cards = []  # 每兩回合三選一的卡池
        self.discovery_select_count = 1  # 灵光一闪需要选择的数量
        self.discovery_selected = []  # 灵光一闪已选择的卡牌
        self.selected_cards = []  # 通用选择模式已选择的卡牌
        self.cards_played_this_turn = 0 # 本回合已打出的卡牌數
        self.reactions_this_turn = 0    # 本回合觸發的反應次數
        self.enemy_stance = "ATTACK"
        self.enemy_stance_enabled = False

        self.turn_count = 0
        self.max_hand = 10  # 增加手牌上限到 10，防止靈光一閃或技能抽牌被丟棄
        self.anim_queue = []
        self.jump_progress = 0
        self.animation_tick = 0

        # 敵人狀態
        self.enemy_wet_turns = 0
        self.enemy_dot_turns = 0
        self.enemy_dot_damage = 0
        self.enemy_stun_turns = 0
        self.enemy_petrify_turns = 0
        self.enemy_frozen = False
        self.enemy_frozen_turns = 0
        self.enemy_wet = False
        self.enemy_vulnerable_turns = 0
        self.enemy_poison_turns = 0
        self.bloom_cores = 0

        # 玩家狀態
        self.maya_active = False
        self.grass_buff = False
        self.pyro_damage_bonus = 0
        self.strength = 0
        self.next_turn_energy = 0
        self.attack_played_count = 0
        self.control_resistance = 0
        self.control_count_this_turn = 0

        self.pending_relic = None
        self.pending_upgrade = False
        self.battle_log = []
        self.show_battle_log = True
        self.stats_total_cards_played = 0
        self.stats_total_damage_dealt = 0
        self.stats_total_damage_taken = 0
        self.stats_highest_wave = 1
        self.stats_total_kills = 0
        self.stats_total_turns = 0
        self.stats_total_reactions = 0
        self.unlocked_achievements = set()
        self.current_save_slot = 1
        self.show_slot_select = False
        self.slot_select_action = "LOAD"
        self.state = "MAIN_MENU"

        self.volume = vol
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volume)

    def start_endless_mode(self):
        """啟動無盡模式"""
        self.is_endless = True
        self.endless_loop_count = 1
        self.max_waves = 30 # 每 30 波視為一輪
        self.current_wave = 1
        play_bgm(self.volume, is_endless=True)
        self.start_next_wave()

    def increase_difficulty(self):
        """提升無限模式的難度加成"""
        self.anim_queue.append(("status_enemy", "難度攀升！怪物變得更強了", 640, 400))
        # 額外小獎勵：回滿血
        self.player_hp = self.player_max_hp
        self.anim_queue.append(("heal_player", self.player_max_hp, 250, SCREEN_H - 350))

    def apply_mode_modifiers(self, mode_name):
        self.selected_mode = mode_name
        self.is_endless = False  # 預設為非無限模式
        play_bgm(self.volume, is_endless=False)
        self.deck = []
        for _ in range(3): self.deck.append(copy.deepcopy(CARD_DATABASE["STRIKE"]))
        self.deck.append(copy.deepcopy(CARD_DATABASE["HYDRO_BLADE"]))
        for _ in range(4): self.deck.append(copy.deepcopy(CARD_DATABASE["DEFEND"]))
        self.deck.append(copy.deepcopy(CARD_DATABASE["PIERCE"]))
        self.deck.append(copy.deepcopy(CARD_DATABASE["IRON_WALL"]))

        self.owned_cards = list(self.deck)
        if mode_name == "ENDLESS":
            self.start_endless_mode()
            return

        if mode_name == "BURST":
            self.base_energy = 4
            self.energy = 4
            for card in self.deck:
                if card.base_damage > 0:
                    card.damage = card.base_damage + 5
                    if card.custom_desc:
                        card.custom_desc = "無雙!" + card.custom_desc
                    else:
                        card.custom_desc = f"無雙!造成 {card.damage} 傷害"

        elif mode_name == "HARD":
            self.enemy_max_hp = 120
            self.enemy_hp = 120
            self.enemy_min_dmg += 6
            self.enemy_max_dmg += 6

        elif mode_name == "TEST":
            self.current_wave = 1
            self.max_waves = 1
            self.enemy_max_hp = 10
            self.enemy_hp = 10
            self.enemy_min_dmg = 1
            self.enemy_max_dmg = 1
            self.relics.append({"id": "BlizzardStrayer", "name": "冰風迷途的留戀", "color": (100, 200, 255)})
            self.relics.append({"id": "CrimsonWitch", "name": "熾烈的炎之魔女", "color": (255, 100, 50)})
            self.pyro_damage_bonus = 3

        random.shuffle(self.deck)
        self.turn_count = 1
        self.enemy_stance_enabled = False
        self.roll_enemy_intent()
        self.cards_played_this_turn = 0
        self.reactions_this_turn = 0
        self.state = "BATTLE"
        self.draw_cards(5)
        self.refresh_target_mark()

    def _register_owned_card(self, card):
        self.owned_cards.append(card)

    def _active_power_name(self, card):
        return card.base_name + ("+" if card.upgraded else "")

    def _consolidate_combat_piles(self):
        """將手牌、棄牌、消耗堆併回牌庫，避免波次間卡牌遺失。"""
        self.deck.extend(c for c in self.hand if not getattr(c, "is_temporary", False))
        self.deck.extend(c for c in self.discard if not getattr(c, "is_temporary", False))
        self.deck.extend(c for c in self.exhaust_pile if not getattr(c, "is_temporary", False))
        self.hand.clear()
        self.discard.clear()
        self.exhaust_pile.clear()

    def _dispose_played_card(self, card):
        if not card.exhaust:
            self.discard.append(card)
        else:
            self.exhaust_pile.append(card)

    def _card_from_template(self, base_name, upgraded=False):
        key = CARD_NAME_TO_KEY.get(base_name)
        if not key:
            return None
        template = CARD_DATABASE.get(key)
        if not template:
            return None
        new_card = copy.deepcopy(template)
        if upgraded:
            new_card.upgrade()
        return new_card

    def _sync_power_entry_for_card(self, card):
        """升級能力牌後，同步 powers / powers_with_group 中的名稱。"""
        if card.type != "POWER":
            return
        new_name = self._active_power_name(card)
        base = card.base_name
        for old_name in (base, base + "+"):
            if old_name in self.powers:
                self.powers[self.powers.index(old_name)] = new_name
                break
        for old_name in list(self.powers_with_group.keys()):
            if old_name in (base, base + "+"):
                self.powers_with_group[new_name] = self.powers_with_group.pop(old_name)
                break

    def _power_base_name(self, power_name):
        return power_name[:-1] if power_name.endswith("+") else power_name

    def _has_active_power(self, base_name):
        return base_name in self.powers or (base_name + "+") in self.powers

    def _strip_temporary_cards(self):
        """移除造物主工坊等產生的臨時牌，避免殘留或洗入牌庫。"""
        for pile in (self.hand, self.deck, self.discard, self.exhaust_pile):
            pile[:] = [c for c in pile if not getattr(c, "is_temporary", False)]

    def _clear_power_effect(self, base_power_name):
        """能力牌本輪結束：清除 buff 並移除 powers 登記（含升級前後名稱）。"""
        for name in (base_power_name, base_power_name + "+"):
            while name in self.powers:
                self.powers.remove(name)
            self.powers_with_group.pop(name, None)

        if base_power_name == "造物主工坊":
            self._strip_temporary_cards()
        elif base_power_name == "净善摄位":
            self.maya_active = False
            self.grass_buff = False
            self.maya_turns = 0

    def configure_stance_buff(self, wave):
        """節奏大師：僅 BOSS / 部分精英具備進攻·防禦交替"""
        self.enemy_stance_enabled = (
            self.stage_type in ("BOSS", "FINAL_BOSS") or wave in (15, 25)
        )
        if self.enemy_stance_enabled:
            self.enemy_stance = self.get_stance_for_turn(1)
            self.anim_queue.append((
                "status_enemy",
                "特殊機制【節奏大師】已啟動",
                SCREEN_W - 400, SCREEN_H * 0.12,
            ))
        else:
            self.enemy_stance = "ATTACK"

    def get_stance_for_turn(self, turn):
        """回合 1-2 進攻、3-4 防禦，每兩回合切換一次"""
        return "ATTACK" if ((max(1, turn) - 1) // 2) % 2 == 0 else "DEFEND"

    def get_stance_status_text(self):
        if not self.enemy_stance_enabled:
            return None
        if self.enemy_stance == "ATTACK":
            return "當前狀態：【進攻姿態】意圖傷害 +50%"
        return "當前狀態：【防禦姿態】每回合回復 10 生命"

    def get_stance_preview_text(self):
        if not self.enemy_stance_enabled:
            return None
        next_stance = self.get_stance_for_turn(self.turn_count + 1)
        if next_stance == self.enemy_stance:
            return None
        label = "進攻" if next_stance == "ATTACK" else "防禦"
        return f"下回合預告：將切換至【{label}姿態】"

    def update_enemy_stance(self, announce=False):
        if not self.enemy_stance_enabled:
            return self.enemy_stance
        new_stance = self.get_stance_for_turn(self.turn_count)
        if new_stance != self.enemy_stance:
            self.enemy_stance = new_stance
            if announce:
                msg = "姿態切換：進攻姿態" if new_stance == "ATTACK" else "姿態切換：防禦姿態"
                self.anim_queue.append(("status_enemy", msg, SCREEN_W - 400, SCREEN_H * 0.15))
        return self.enemy_stance

    def roll_enemy_intent(self):
        self.enemy_intent = random.randint(self.enemy_min_dmg, self.enemy_max_dmg)
        if self.enemy_stance_enabled and self.enemy_stance == "ATTACK":
            self.enemy_intent = int(self.enemy_intent * 1.5)

    def apply_stance_defend_heal(self):
        if not self.enemy_stance_enabled:
            return
        if self.enemy_stance == "DEFEND" and self.enemy_hp > 0:
            before = self.enemy_hp
            self.enemy_hp = min(self.enemy_max_hp, self.enemy_hp + 10)
            healed = self.enemy_hp - before
            if healed > 0:
                self.anim_queue.append(("status_enemy", f"防禦修復 +{healed}", SCREEN_W - 400, SCREEN_H * 0.3))

    def refresh_target_mark(self):
        """每回合隨機標記一張手牌，打出時額外 15 真實傷害"""
        for c in self.hand:
            c.is_marked = False
        if self.hand:
            random.choice(self.hand).is_marked = True

    def apply_true_damage(self, amount):
        if amount <= 0 or self.enemy_hp <= 0:
            return
        self.enemy_hp = max(0, self.enemy_hp - amount)
        self.anim_queue.append(("true_damage", amount, SCREEN_W - 400, SCREEN_H * 0.4))
        if self.enemy_hp <= 0:
            self.enemy_hp = 0
            self.anim_queue.append(("enemy_death",))
            self.generate_rewards()

    def trigger_target_mark(self, card):
        if not getattr(card, "is_marked", False):
            return
        card.is_marked = False
        self.apply_true_damage(15)

    def get_control_resistance_multiplier(self):
        """获取控制抗性系数"""
        if self.control_resistance == 0:
            return 1.0  # 100% 效果
        elif self.control_resistance == 1:
            return 0.8  # 80% 效果
        elif self.control_resistance == 2:
            return 0.6  # 60% 效果
        elif self.control_resistance == 3:
            return 0.4  # 40% 效果
        else:
            return 0.2  # 20% 效果（最小）

    def get_enemy_type_multiplier(self):
        """获取敌人类型系数"""
        if self.current_wave >= 10 and self.current_wave % 5 == 0:
            return 0.5  # BOSS: 50% 效果
        elif self.current_wave >= 10:
            return 0.75  # 精英：75% 效果
        else:
            return 1.0  # 普通：100% 效果

    def can_apply_control(self):
        """检查是否可以施加控制"""
        # 普通敌人：每回合最多 2 次控制
        if self.current_wave < 10:
            return self.control_count_this_turn < 2
        # 精英敌人：每回合最多 2 次控制
        elif self.current_wave % 5 != 0:
            return self.control_count_this_turn < 2
        # BOSS：每回合最多 1 次控制
        else:
            return self.control_count_this_turn < 1

    def _add_reaction(self, msg, y=0.28):
        self.reactions_this_turn += 1
        self.stats_total_reactions += 1
        self.anim_queue.append(("status_enemy", msg, SCREEN_W - 400, SCREEN_H * y))

    def reaction_electrocharged(self):
        """感電：雷+潮濕，+2易傷，不消耗潮濕"""
        if not self.enemy_wet:
            return False
        self._add_reaction("感電！")
        self.enemy_vulnerable_turns = max(self.enemy_vulnerable_turns, 2)
        return True

    def reaction_crystallize(self, block_bonus=10):
        """結晶：岩+潮濕，玩家獲得護甲"""
        if not self.enemy_wet:
            return False
        self.player_block += block_bonus
        self._add_reaction(f"結晶！+{block_bonus}盾")
        return True

    def reaction_swirl(self, intent_reduce=0.15):
        """擴散：風+潮濕，降低敵人當前意圖"""
        if not self.enemy_wet:
            return False
        self.enemy_intent = max(1, int(self.enemy_intent * (1 - intent_reduce)))
        self._add_reaction("風擴散！意圖降低")
        return True

    def draw_cards(self, num):
        for _ in range(num):
            if len(self.hand) >= self.max_hand:
                break
            if not self.deck:
                if self.discard or self.exhaust_pile:
                    self.deck.extend(self.discard)
                    self.deck.extend(self.exhaust_pile)
                    self.discard.clear()
                    self.exhaust_pile.clear()
                    random.shuffle(self.deck)
            if self.deck:
                card = self.deck.pop()
                if card.base_name == "雷霆连击":
                    card.permanent_dmg_bonus += 1
                self.hand.append(card)

    def play_card(self, card, start_x, start_y):
        if self.energy >= card.cost:
            self.cards_played_this_turn += 1 # 增加連擊計數
            self.stats_total_cards_played += 1
            self._log(f"打出 {card.name}")

            # 1. 記錄打出牌前的波次與無盡輪次
            prev_wave = self.current_wave
            prev_loop = self.endless_loop_count

            self.trigger_target_mark(card)

            # 2. 判斷：如果狀態改變，或者無盡模式下進入了新輪次(代表Boss被真傷擊殺)，則中斷結算
            if self.state not in ("BATTLE", "SELECT_CARD") or self.current_wave != prev_wave or self.endless_loop_count != prev_loop:
                return True

            card_name = card.base_name

            # --- 處理卡牌類型邏輯 ---
            if card.type == "POWER":
                # 如果卡牌已升级，使用带"+"后缀的名称
                power_name = card_name + "+" if card.upgraded else card_name
                self.powers.append(power_name)
                # 計算當前波次屬於哪一組 (每5波一組)
                current_group = (self.current_wave - 1) // 5 + 1
                self.powers_with_group[power_name] = current_group
                self.hand.remove(card)
                self.sidelined_power_cards.append(card)
                self.energy -= card.cost
                self.anim_queue.append(("status_enemy", f"激活: {card.name}", 250, SCREEN_H - 350))

                if card_name == "净善摄位":
                    self.maya_active = True
                    self.grass_buff = True
                    # 检查是否是升级版本，升级后持续两回合
                    if card.upgraded:
                        self.maya_turns = 2
                    else:
                        self.maya_turns = 1
                return True

            # --- 處理攻擊牌通用加成 ---
            final_damage = card.damage
            if card.type == "ATTACK":
                self.attack_played_count += 1
                final_damage += self.strength
                # 未升级的无限回路：每打出3张攻击牌抽1张技能牌
                if "無限迴路" in self.powers and "無限迴路+" not in self.powers and self.attack_played_count % 3 == 0:
                    self.draw_random_skill()

            # 升级的无限回路：每打出3张牌（任何类型）抽1张技能牌
            if "無限迴路+" in self.powers and self.cards_played_this_turn % 3 == 0:
                self.draw_random_skill()

            # --- 处理卡牌特殊效果 ---
            if card_name == "黎明·斩击":
                times = self.energy
                self.energy = 0
                dmg_per_hit = final_damage + self.pyro_damage_bonus
                if self.enemy_wet:
                    dmg_per_hit *= 2
                    if "CrimsonWitch" not in [r["id"] for r in self.relics]:
                        self.enemy_wet = False
                        # === 新增這行：蒸發時同步清空回合數 ===
                        self.enemy_wet_turns = 0
                        # =================================
                for i in range(times):
                    hit_dmg = dmg_per_hit
                    self.enemy_hp -= hit_dmg
                    offset_y = i * 25
                    self.anim_queue.append(("damage_enemy", hit_dmg, SCREEN_W - 400, SCREEN_H * 0.35 + offset_y))
                self.finish_card_play(card, start_x, start_y)

            elif card_name == "天基烈焰":
                self.energy -= card.cost
                if self.enemy_vulnerable_turns > 0:
                    final_damage *= 2
                # 蒸发反应
                if self.enemy_wet:
                    final_damage *= 2
                    self.reactions_this_turn += 1
                    if "CrimsonWitch" not in [r["id"] for r in self.relics]:
                        self.enemy_wet = False
                        # === 新增這行：蒸發時同步清空回合數 ===
                        self.enemy_wet_turns = 0
                        # =================================

                self.apply_damage(final_damage, card, start_x, start_y)
                self.hand.remove(card)
                self._dispose_played_card(card)

            elif card_name == "不灭之火":
                self.energy -= card.cost
                # 蒸发反应
                if self.enemy_wet:
                    final_damage *= 2
                    self.reactions_this_turn += 1
                    if "CrimsonWitch" not in [r["id"] for r in self.relics]:
                        self.enemy_wet = False
                        # === 新增這行：蒸發時同步清空回合數 ===
                        self.enemy_wet_turns = 0
                        # =================================

                self.apply_damage(final_damage, card, start_x, start_y)
                self.hand.remove(card)
                self._dispose_played_card(card)

            elif card_name == "雷霆连击":
                self.energy -= card.cost
                hit_bonus = getattr(card, "permanent_dmg_bonus", 0)
                for i in range(card.hits):
                    if self.enemy_hp <= 0:
                        break
                    if i == 0:
                        self.reaction_electrocharged()
                    hit_dmg = final_damage + hit_bonus
                    self.apply_damage(hit_dmg, card, start_x, start_y)
                    if i == card.hits - 1 and self.enemy_hp > 0:
                        self.enemy_stun_turns = max(self.enemy_stun_turns, 1)
                        self.anim_queue.append(("status_enemy", "雷霆麻痹！", SCREEN_W - 400, SCREEN_H * 0.22))
                self.hand.remove(card)
                # === 修改这里：尊重卡牌的消耗属性 ===
                self._dispose_played_card(card)

            elif card_name == "死神收割":
                self.energy -= card.cost
                self.apply_damage(final_damage, card, start_x, start_y)
                heal_amt = int(final_damage * 0.5)
                self.player_hp = min(self.player_max_hp, self.player_hp + heal_amt)
                self.anim_queue.append(("heal_player", heal_amt, 250, SCREEN_H - 350))
                self.hand.remove(card)
                self._dispose_played_card(card)

            elif card_name == "神圣屏障":
                self.energy -= card.cost
                self.player_block += card.block
                self.next_turn_energy += 1
                self.finish_card_play(card, start_x, start_y)

            elif card_name == "時空停滯":
                if len(self.hand) > 1:
                    self.energy -= card.cost
                    self.selection_mode = "TIME_STASIS"
                    self.selection_source_card = card
                    self.state = "SELECT_CARD"
                    self.anim_queue.append(("status_enemy", "請選擇一張手牌", 250, SCREEN_H - 350))
                else:
                    self.anim_queue.append(("status_enemy", "沒有其他手牌可選", 250, SCREEN_H - 350))
                    return False

            elif card_name == "命運豪賭":
                self.energy -= card.cost

                if card.upgraded and len(self.hand) >= 4:
                    self.selection_mode = "FATE_GAMBLE"
                    self.state = "SELECT_CARD"
                    self.selected_cards = []
                    self.anim_queue.append(("status_enemy", "選擇 4 張手牌丟棄", 250, SCREEN_H - 350))
                else:
                    self.discard.extend([
                        c for c in self.hand
                        if c is not card and not getattr(c, 'is_temporary', False)
                    ])
                    self.hand = [c for c in self.hand if c is card]
                    self.finish_card_play(card, start_x, start_y)
                    self.draw_cards(4)
                    return True

                self.finish_card_play(card, start_x, start_y)
                return True

            elif card_name == "灵光一闪":
                self.energy -= card.cost
                pool = self.deck + self.discard
                random.shuffle(pool)
                if pool:
                    num = min(3, len(pool))
                    self.discovery_cards = []
                    for i in range(num):
                        c = pool[i]
                        if c in self.deck: self.deck.remove(c)
                        elif c in self.discard: self.discard.remove(c)
                        self.discovery_cards.append(c)
                    # === 修改這裡：如果牌不夠，動態下調需要選擇的數量 ===
                    max_can_select = len(self.discovery_cards)
                    self.discovery_select_count = min(2 if card.upgraded else 1, max_can_select)
                    # ================================================
                    self.discovery_selected = []
                    self.state = "DISCOVERY"
                    self.anim_queue.append(("status_enemy", "靈光一閃！", 250, SCREEN_H - 350))
                else:
                    self.anim_queue.append(("status_enemy", "沒有卡牌可供發現", 250, SCREEN_H - 350))

                self.finish_card_play(card, start_x, start_y)
                return True

            elif card_name == "冰霜新星":
                self.energy -= card.cost
                if self.enemy_wet:
                    self.reactions_this_turn += 1
                # 控制抗性檢定
                if self.can_apply_control():
                    multiplier = self.get_control_resistance_multiplier() * self.get_enemy_type_multiplier()
                    freeze_turns = max(1, int(1 * multiplier))
                    if freeze_turns > 0:
                        self.enemy_frozen = True
                        self.enemy_frozen_turns = freeze_turns
                        self.control_resistance += 1
                        self.control_count_this_turn += 1
                        self.anim_queue.append(("status_enemy", f"凍結！{freeze_turns}回合", SCREEN_W - 400, SCREEN_H * 0.25))
                    else:
                        self.anim_queue.append(("status_enemy", "控制無效！", SCREEN_W - 400, SCREEN_H * 0.25))
                else:
                    self.anim_queue.append(("status_enemy", "控制上限！", SCREEN_W - 400, SCREEN_H * 0.25))
                self.apply_damage(final_damage, card, start_x, start_y)
                self.hand.remove(card)
                self._dispose_played_card(card)

            elif card_name == "水刃":
                self.energy -= card.cost
                self.apply_damage(final_damage, card, start_x, start_y)
                self.enemy_wet = True
                # === 新增這行：水刃賦予 2 回合潮濕 ===
                self.enemy_wet_turns = max(getattr(self, 'enemy_wet_turns', 0), 2)
                # =================================
                self.anim_queue.append(("status_enemy", "潮濕!", SCREEN_W - 400, SCREEN_H * 0.25))
                self.hand.remove(card)
                self._dispose_played_card(card)

            else:
                self.energy -= card.cost
                if card_name == "碎冰重击" and self.enemy_frozen_turns > 0:
                    final_damage *= 3
                    self.enemy_frozen_turns = 0
                    self.enemy_frozen = False
                    self.reactions_this_turn += 1
                    self.anim_queue.append(("status_enemy", "碎冰！", SCREEN_W - 400, SCREEN_H * 0.25))
                elif card_name == "天街巡游":
                    self.reaction_electrocharged()
                    self.enemy_dot_turns = 3
                    self.enemy_dot_damage = 5
                elif card_name == "千岩固牢":
                    self.reaction_crystallize(12)
                elif card_name == "旋风护盾":
                    self.reaction_swirl()
                elif card_name == "元素爆发":
                    self.apply_damage(final_damage, card, start_x, start_y)
                    self.hand.remove(card)
                    self._dispose_played_card(card)
                    # 控制抗性檢定
                    if self.can_apply_control():
                        multiplier = self.get_control_resistance_multiplier() * self.get_enemy_type_multiplier()
                        petrify_turns = max(1, int(2 * multiplier))
                        if petrify_turns > 0:
                            self.enemy_petrify_turns = petrify_turns
                            self.control_resistance += 1
                            self.control_count_this_turn += 1
                            self.reactions_this_turn += 1
                            self.anim_queue.append(("status_enemy", f"石化！{petrify_turns}回合", SCREEN_W - 400, SCREEN_H * 0.25))
                        else:
                            self.anim_queue.append(("status_enemy", "控制無效！", SCREEN_W - 400, SCREEN_H * 0.25))
                    else:
                        self.anim_queue.append(("status_enemy", "控制上限！", SCREEN_W - 400, SCREEN_H * 0.25))
                    if self.enemy_hp <= 0:
                        self.enemy_hp = 0
                        self.anim_queue.append(("enemy_death",))
                        self.generate_rewards()
                    return True
                elif card_name == "荒星防护":
                    self.reaction_crystallize(8)
                    self.player_hp = min(self.player_max_hp, self.player_hp + 10)
                    self.anim_queue.append(("heal_player", 10, 250, SCREEN_H - 350))
                elif card_name == "大剑重击":
                    self.apply_damage(final_damage, card, start_x, start_y)
                    self.hand.remove(card)
                    self._dispose_played_card(card)
                    # 控制抗性檢定
                    if self.can_apply_control():
                        multiplier = self.get_control_resistance_multiplier() * self.get_enemy_type_multiplier()
                        stun_turns = max(1, int(1 * multiplier))
                        if stun_turns > 0:
                            self.enemy_stun_turns = stun_turns
                            self.control_resistance += 1
                            self.control_count_this_turn += 1
                            self.anim_queue.append(("status_enemy", f"暈眩！{stun_turns}回合", SCREEN_W - 400, SCREEN_H * 0.25))
                        else:
                            self.anim_queue.append(("status_enemy", "控制無效！", SCREEN_W - 400, SCREEN_H * 0.25))
                    else:
                        self.anim_queue.append(("status_enemy", "控制上限！", SCREEN_W - 400, SCREEN_H * 0.25))
                    if self.enemy_hp <= 0:
                        self.enemy_hp = 0
                        self.anim_queue.append(("enemy_death",))
                        self.generate_rewards()
                    return True
                elif card_name == "雨神之护":
                    self.enemy_wet = True
                    self.enemy_wet_turns = 3
                    self.anim_queue.append(("status_enemy", "潮濕!", SCREEN_W - 400, SCREEN_H * 0.25))
                elif card_name == "潮汐波":
                    self.enemy_wet = True
                    self.enemy_wet_turns = 4
                    self.anim_queue.append(("status_enemy", "潮濕!", SCREEN_W - 400, SCREEN_H * 0.25))
                    if self.deck:
                        drawn_card = self.deck.pop()
                        self.hand.append(drawn_card)

                self.apply_damage(final_damage, card, start_x, start_y)
                self.player_block += card.block
                if card in self.hand:
                    self.hand.remove(card)
                self._dispose_played_card(card)

            if self.enemy_hp <= 0:
                self.enemy_hp = 0
                self.anim_queue.append(("enemy_death",))
                self.generate_rewards()
            return True
        return False

    def apply_damage(self, dmg, card, sx, sy):
        # --- 處理元素護盾邏輯 ---
        if self.enemy_hit_shield > 0:
            # 判斷是否為克制元素
            is_counter = card.element in ELEMENT_COUNTERS.get(self.enemy_shield_element, [])
            reduction = 3 if is_counter else 1

            self.enemy_hit_shield = max(0, self.enemy_hit_shield - reduction)

            if is_counter:
                msg = f"有效破盾！-{reduction}層"
                # 克制破盾獎勵：敵人下一次意圖傷害降低 15%
                self.enemy_intent = max(1, int(self.enemy_intent * 0.85))
                self.anim_queue.append(("status_enemy", "元素震懾：敵人傷害降低", SCREEN_W - 400, SCREEN_H * 0.2))
            else:
                msg = f"護盾抵擋！-1層"

            self.anim_queue.append(("status_enemy", msg, SCREEN_W - 400, SCREEN_H * 0.45))

            if self.enemy_hit_shield == 0:
                self.anim_queue.append(("status_enemy", "護盾破碎！", SCREEN_W - 400, SCREEN_H * 0.45))
                self.enemy_stun_turns = 1 # 破盾獎勵：暈眩 1 回合

            # 即使抵擋也執行動畫，但傷害為 0
            tx = SCREEN_W - 400
            ty = SCREEN_H * 0.4
            self.anim_queue.append(("card_fly", card, sx, sy, tx, ty))
            return

        # 易傷增幅：受到傷害增加 50%
        if self.enemy_vulnerable_turns > 0:
            dmg = int(dmg * 1.5)

        self.enemy_hp -= dmg
        self.stats_total_damage_dealt += dmg
        self._log(f"對 {self.enemy_name} 造成 {dmg} 點傷害")
        tx = SCREEN_W - 400
        ty = SCREEN_H * 0.4
        self.anim_queue.append(("card_fly", card, sx, sy, tx, ty))
        if dmg > 0:
            self.anim_queue.append(("damage_enemy", dmg, tx, SCREEN_H * 0.35))

        # --- 處理反傷邏輯 (僅對攻擊牌生效) ---
        if self.enemy_thorns > 0 and card.type == "ATTACK":
            actual_thorns = max(0, self.enemy_thorns - self.player_block)
            self.player_block = max(0, self.player_block - self.enemy_thorns)
            if actual_thorns > 0:
                self.player_hp -= actual_thorns
                self.anim_queue.append(("damage_player", actual_thorns, 200, SCREEN_H - 350))
            self.anim_queue.append(("status_enemy", f"反傷！-{self.enemy_thorns}", 200, SCREEN_H - 380))

            # 立即檢查玩家是否死亡
            if self.player_hp <= 0:
                self.player_hp = 0
                # === 修正錯字： GAME_OVER 改為 GAMEOVER ===
                self.state = "GAMEOVER"
                self.anim_queue.append(("player_death",))

        # 草原催化者/净善摄位：生成草原核
        if self.enemy_wet and "Catalyst" in [r["id"] for r in self.relics]:
            self.bloom_cores += 1
            self.reactions_this_turn += 1
            self.anim_queue.append(("status_enemy", f"草原核+{self.bloom_cores}", SCREEN_W - 300, SCREEN_H * 0.3))
        elif self.grass_buff:
            self.bloom_cores += 1
            self.reactions_this_turn += 1
            self.anim_queue.append(("status_enemy", f"草原核+{self.bloom_cores}", SCREEN_W - 300, SCREEN_H * 0.3))

    def finish_card_play(self, card, sx, sy):
        tx, ty = 250, SCREEN_H - 300
        self.anim_queue.append(("card_fly", card, sx, sy, tx, ty))
        if card in self.hand: self.hand.remove(card)
        self._dispose_played_card(card)

    def draw_random_skill(self):
        if len(self.hand) >= self.max_hand:
            self.anim_queue.append(("status_enemy", "手牌已滿！", 250, SCREEN_H - 350))
            return

        skills = [c for c in self.deck if c.type == "SKILL"]

        # 如果牌庫中沒有技能牌，則嘗試洗棄牌堆與消耗堆
        if not skills and (self.discard or self.exhaust_pile):
            self.deck.extend(self.discard)
            self.deck.extend(self.exhaust_pile)
            self.discard.clear()
            self.exhaust_pile.clear()
            random.shuffle(self.deck)
            skills = [c for c in self.deck if c.type == "SKILL"]

        if skills:
            card = random.choice(skills)
            self.deck.remove(card)
            self.hand.append(card)
            self.anim_queue.append(("status_enemy", "無限迴路: 抽取技能", 250, SCREEN_H - 350))
        else:
            self.anim_queue.append(("status_enemy", "牌庫中沒有技能牌", 250, SCREEN_H - 350))

    def generate_rewards(self):
        if self.current_wave >= self.max_waves:
            if self.is_endless:
                # 進入下一輪無盡
                self.endless_loop_count += 1
                # 【修改】將波次設為 0，這樣等一下領完獎勵後 current_wave += 1，就會剛好進入下一輪的第 1 關
                self.current_wave = 0
                self.anim_queue.append(("status_enemy", f"進入無盡第 {self.endless_loop_count} 輪", 640, 360))
                # 這裡可以加入一些難度提升邏輯
                self.increase_difficulty()

                # 【刪除】移除了 self.start_next_wave() 和 return
                # 讓程式不要在這裡中斷，繼續往下走，生成獎勵並切換到 REWARD 介面！
            else:
                # 一般模式結束
                self.state = "JUMP"
                self.jump_progress = 0
                return

        # ... 原有的獎勵產生邏輯 ...

        self.state = "REWARD"
        self.selected_reward = None
        self.pending_relic = None
        self.stats_total_kills += 1

        if self.stage_type in ["ELITE", "BOSS", "FINAL_BOSS"]:
            self.pending_upgrade = True

        # 🌟 15% 機率獲得聖遺物
        if random.random() < 0.15:
            available_relic_keys = [k for k in RELIC_DATABASE.keys() if k not in [r["id"] for r in self.relics]]
            if available_relic_keys:
                relic_key = random.choice(available_relic_keys)
                self.pending_relic = RELIC_DATABASE[relic_key]

        pool_keys = [
            "REWARD_1", "REWARD_2", "REWARD_3", "REWARD_4",
            "BURST_FLAME", "STORM_SHIELD", "SACRIFICE",
            "SHATTER", "DAWN", "MAYA","FROST_NOVA", "HYDRO_BLADE", "RAIN_GUARD", "TIDAL_WAVE",
            "HEAVEN_FLAME", "THUNDER_COMBO", "REAPER",
            "DIVINE_BARRIER", "TIME_STASIS", "FATE_GAMBLE",
            "VOID_BLOOD", "INFINITE_LOOP", "CREATOR_WORKSHOP", "KARMA_REVERSE", "DISCOVERY"
        ]
        available_keys = [key for key in pool_keys if key not in self.obtained_rewards]

        if len(available_keys) < 3:
            self.obtained_rewards = []
            available_keys = pool_keys

        pool = [copy.deepcopy(CARD_DATABASE[key]) for key in available_keys]

        if self.selected_mode == "BURST":
            for card in pool:
                if card.base_damage > 0:
                    card.damage = card.base_damage + 5
                    if card.custom_desc:
                        card.custom_desc = "無雙!" + card.custom_desc
                    else:
                        card.custom_desc = f"無雙!造成 {card.damage} 傷害" if card.block == 0 else f"無雙!{card.damage}傷/{card.block}盾"

        self.reward_cards = random.sample(pool, 3)

    def choose_reward(self):
        if self.selected_reward:
            self.deck.append(self.selected_reward)
            self._register_owned_card(self.selected_reward)
            card_key = CARD_NAME_TO_KEY.get(self.selected_reward.base_name)
            if card_key and card_key not in self.obtained_rewards:
                self.obtained_rewards.append(card_key)

        if self.pending_relic:
            self.relics.append(self.pending_relic)
            if self.pending_relic["id"] == "CrimsonWitch":
                self.pyro_damage_bonus = 3
            self.pending_relic = None

        if self.pending_upgrade:
            self.state = "UPGRADE_CARD"
            return

        self.current_wave += 1
        if self.current_wave > self.max_waves:
            self.state = "VICTORY"
        else:
            self.start_next_wave()

    def start_next_wave(self):
        w = self.current_wave
        self.stats_highest_wave = max(self.stats_highest_wave, w)

        # 檢查並清除過期的功能牌（每5波一組）
        current_group = (w - 1) // 5 + 1
        expired_powers = []
        for power_name, power_group in list(self.powers_with_group.items()):
            if power_group != current_group:
                expired_powers.append(power_name)

        cleared_bases = set()
        for power_name in expired_powers:
            base_power_name = self._power_base_name(power_name)
            if base_power_name in cleared_bases:
                continue
            cleared_bases.add(base_power_name)
            self._clear_power_effect(base_power_name)

            returned = False
            for i, sidelined in enumerate(self.sidelined_power_cards):
                if sidelined.base_name == base_power_name:
                    self.deck.append(self.sidelined_power_cards.pop(i))
                    returned = True
                    break
            if not returned:
                is_upgraded = power_name.endswith("+") or any(
                    c.base_name == base_power_name and c.upgraded for c in self.owned_cards
                )
                fallback = self._card_from_template(base_power_name, is_upgraded)
                if fallback:
                    self.deck.append(fallback)
                    self._register_owned_card(fallback)

            self.anim_queue.append(("status_enemy", f"{power_name} 效果消失", 250, SCREEN_H - 350))

        # 重置機制屬性
        self.enemy_hit_shield = 0
        self.enemy_shield_element = "None"
        self.enemy_charge_turns = 0
        self.enemy_scaling_strength = 0
        self.enemy_thorns = 0
        self.enemy_vulnerable_turns = 0
        self.enemy_intent_type = "ATTACK"
        self.enemy_wet_turns = 0

        if w == 30:
            self.stage_type = "FINAL_BOSS"
            self.enemy_name = "最終大_BOSS_3"
            self.enemy_hit_shield = 15     # 最終 BOSS 帶 15 層盾
            self.enemy_shield_element = random.choice(["Pyro", "Hydro", "Cryo", "Electro", "Geo"])
            self.enemy_charge_turns = 1    # 開啟大招計時
            self.enemy_scaling_strength = 3 # 每回合力量 +3
        elif w == 10:
            self.stage_type = "BOSS"
            self.enemy_name = "階段 BOSS 1"
            self.enemy_hit_shield = 6
            self.enemy_shield_element = "Pyro" # 第一個 BOSS 固定的火盾，教學用
            self.enemy_charge_turns = 1    # 階段 BOSS 開啟大招計時
        elif w == 20:
            self.stage_type = "BOSS"
            self.enemy_name = "階段 BOSS 2"
            self.enemy_hit_shield = 8
            self.enemy_shield_element = random.choice(["Hydro", "Cryo", "Electro"])
            self.enemy_charge_turns = 1
        elif w == 5:
            self.stage_type = "ELITE"
            self.enemy_name = "精英怪 1"
            self.enemy_thorns = 3          # 精英怪 1 帶反傷
        elif w == 15:
            self.stage_type = "ELITE"
            self.enemy_name = "精英怪 2"
            self.enemy_scaling_strength = 2 # 精英怪 2 會成長
        elif w == 25:
            self.stage_type = "ELITE"
            self.enemy_name = "精英怪 3"
            self.enemy_vulnerable_turns = 99
            self.enemy_hit_shield = 12
            self.enemy_shield_element = "Geo" # 精英怪 3 固定岩盾
        else:
            self.stage_type = "NORMAL"
            if w <= 4: self.enemy_name = "基礎雜兵"
            elif w <= 9: self.enemy_name = "進階雜兵(盾/遠程)"
            elif w <= 14: self.enemy_name = "進階怪(屬性控制)"
            elif w <= 19: self.enemy_name = "怪物組合(群攻考驗)"
            elif w <= 24: self.enemy_name = "高難度雜兵"
            else: self.enemy_name = "終極考驗怪物"

        self.configure_stance_buff(w)

        # 确保所有类型的敌人都能加载图片
        self.enemy_image = load_enemy_image(self.enemy_name)

        if 26 <= w <= 29 and self.stage_type == "NORMAL":
            self.enemy_intent_type = "DEBUFF"

        if w <= 10:
            base_hp = 50 + w * 12
            dmg_inc = (w - 1) // 3
        elif w <= 20:
            base_hp = 170 + (w - 10) * 22
            dmg_inc = 3 + (w - 10) // 2
        else:
            base_hp = 390 + (w - 20) * 35
            dmg_inc = 8 + (w - 20) // 2

        base_min_dmg = 6 + dmg_inc
        base_max_dmg = 10 + dmg_inc

        if self.stage_type == "ELITE":
            base_hp = int(base_hp * 1.6)
            base_min_dmg = int(base_min_dmg * 1.3)
            base_max_dmg = int(base_max_dmg * 1.3)
        elif self.stage_type == "BOSS":
            base_hp = int(base_hp * 2.8)
            base_min_dmg = int(base_min_dmg * 1.5)
            base_max_dmg = int(base_max_dmg * 1.5)
        elif self.stage_type == "FINAL_BOSS":
            base_hp = int(base_hp * 4.5)
            base_min_dmg = int(base_min_dmg * 2.0)
            base_max_dmg = int(base_max_dmg * 2.0)

        self.enemy_max_hp = base_hp

        # --- 無限模式難度加成 ---
        if self.is_endless and self.endless_loop_count > 1:
            loop_factor = self.endless_loop_count - 1
            self.enemy_max_hp = int(self.enemy_max_hp * (1 + loop_factor * 0.5))
            base_min_dmg += loop_factor * 5
            base_max_dmg += loop_factor * 5

        self.enemy_hp = self.enemy_max_hp
        self.enemy_min_dmg = base_min_dmg
        self.enemy_max_dmg = base_max_dmg

        if self.selected_mode == "HARD":
            self.enemy_hp = int(self.enemy_hp * 1.3)
            self.enemy_min_dmg += 6
            self.enemy_max_dmg += 6

        self.player_block = 0
        self.energy = self.base_energy

        if "BlizzardStrayer" in [r["id"] for r in self.relics]:
            self.energy += 1

        self._consolidate_combat_piles()
        self.turn_count = 1

        self.enemy_dot_turns = 0
        self.enemy_dot_damage = 0
        self.bloom_cores = 0
        self.enemy_stun_turns = 0
        self.enemy_petrify_turns = 0
        self.enemy_frozen = False
        self.enemy_frozen_turns = 0
        self.enemy_wet = False

        random.shuffle(self.deck)
        if self.enemy_stance_enabled:
            self.update_enemy_stance(announce=False)
        self.roll_enemy_intent()
        self.draw_cards(5)
        self.refresh_target_mark()
        self.reactions_this_turn = 0
        self.state = "BATTLE"

    def end_turn(self):
        """處理玩家結束回合的邏輯"""
        self.stats_total_turns += 1
        self.check_achievements()
        for card in self.modified_cards:
            card.cost = card.original_cost
        self.modified_cards.clear()
        self.hand = [c for c in self.hand if not getattr(c, 'is_temporary', False)]

        # --- 升級虛空血脈效果：回合結束時獲得1力量 ---
        if "虛空血脈+" in self.powers:
            self.strength += 1
            self.anim_queue.append(("status_enemy", "力量提升!", 250, SCREEN_H - 350))

        # --- 交互：反應超載 (單回合反應 >= 3) ---
        if self.reactions_this_turn >= 3:
            self.enemy_stun_turns += 1
            self.anim_queue.append(("status_enemy", "反應超載：敵人癱瘓！", SCREEN_W - 400, SCREEN_H * 0.25))

        # --- 交互：能量浪費 ---
        if self.energy > 0:
            power_gain = self.energy * 2
            self.enemy_intent += power_gain
            self.anim_queue.append(("status_enemy", f"浪費能量：敵人力量 +{power_gain}", SCREEN_W - 400, SCREEN_H * 0.2))

        self.state = "ENEMY_TURN"
        self.process_enemy_turn()

    def process_enemy_turn(self):
        """原來的敵人回合邏輯，從 start_player_turn 之前的邏輯拆分出來"""
        # --- 處理回合開始能力效果 ---
        # --- 處理回合開始能力效果 ---
        if self._has_active_power("造物主工坊"):
            temp_attack = copy.deepcopy(random.choice([c for c in CARD_DATABASE.values() if c.type == "ATTACK"]))
            # 檢查是否是升級版本
            if "造物主工坊+" in self.powers:
                temp_attack.cost = 0
                temp_attack.original_cost = 0
            else:
                temp_attack.cost = 1
                temp_attack.original_cost = 1
            temp_attack.name += "+"
            temp_attack.damage += 5
            temp_attack.is_temporary = True
            # === 新增：让临时牌打出后直接消耗，不进入弃牌堆 ===
            temp_attack.exhaust = True
            if temp_attack.custom_desc:
                temp_attack.custom_desc += "。消耗"
            elif temp_attack.hits > 1 and temp_attack.base_damage > 0:
                temp_attack.custom_desc = "造成 {dmg} 傷害 x{hits} 次。消耗"
            elif temp_attack.base_damage > 0:
                temp_attack.custom_desc = "造成 {dmg} 傷害。消耗"
            # ============================================
            self.hand.append(temp_attack)
            self.anim_queue.append(("status_enemy", "工坊生成卡牌", 250, SCREEN_H - 350))

        # --- 檢查敵人狀態 ---
        enemy_can_act = True
        status_msg = ""

        if self.enemy_stun_turns > 0:
            self.enemy_stun_turns -= 1
            enemy_can_act = False
            status_msg = "敵人暈眩！"
        elif self.enemy_petrify_turns > 0:
            self.enemy_petrify_turns -= 1
            enemy_can_act = False
            status_msg = "敵人石化！"
        elif self.enemy_frozen_turns > 0:
            self.enemy_frozen_turns -= 1
            if self.enemy_frozen_turns == 0:
                self.enemy_frozen = False
            enemy_can_act = False
            status_msg = "敵人凍結！"

        # --- 交互：若敵人無法行動且正在蓄力，大招計數器重置 ---
        if not enemy_can_act and self.enemy_charge_turns > 0:
            self.enemy_charge_turns = 1
            self.anim_queue.append(("status_enemy", "蓄力被打斷！", SCREEN_W - 400, SCREEN_H * 0.25))

        if enemy_can_act:
            damage = self.enemy_intent
            self._log(f"敵人 {self.enemy_name} 意圖 {damage} 點攻擊")

            # --- 交互：連擊壓制 (本回合打出牌 >= 5) ---
            if self.cards_played_this_turn >= 5:
                damage = int(damage * 0.7) # 傷害降低 30%
                self.anim_queue.append(("status_enemy", "連擊壓制：傷害降低！", SCREEN_W - 400, SCREEN_H * 0.2))

            # --- 處理大招蓄力邏輯 ---
            if self.enemy_charge_turns > 0:
                if self.enemy_charge_turns >= self.enemy_charge_max:
                    damage = int(damage * 3.5) # 大招 3.5 倍傷害
                    self.anim_queue.append(("status_enemy", "【天罰】釋放！", SCREEN_W - 400, SCREEN_H * 0.25))
                    self.enemy_charge_turns = 1
                else:
                    self.enemy_charge_turns += 1
                    self.anim_queue.append(("status_enemy", f"蓄力中...({self.enemy_charge_turns}/{self.enemy_charge_max})", SCREEN_W - 400, SCREEN_H * 0.25))

            # --- 處理成長邏輯 ---
            if self.enemy_scaling_strength > 0:
                self.enemy_intent += self.enemy_scaling_strength
                self.anim_queue.append(("status_enemy", f"力量成長 +{self.enemy_scaling_strength}", SCREEN_W - 400, SCREEN_H * 0.2))

            # 因果逆轉判定
            karma_active = "因果逆轉" in self.powers or "因果逆轉+" in self.powers
            if karma_active:
                if random.random() < 0.3:
                    self.enemy_vulnerable_turns += 3
                    self.enemy_poison_turns += 3
                    self.anim_queue.append(("status_enemy", "因果逆轉觸發!", SCREEN_W - 400, SCREEN_H * 0.3))
                # 物理伤害时反弹一半
                counter = damage // 2
                self.enemy_hp -= counter
                self.anim_queue.append(("status_enemy", f"反彈!-{counter}", SCREEN_W - 400, SCREEN_H * 0.25))

                # === 新增這裡：防止怪物被彈死卻還能繼續攻擊 ===
                if self.enemy_hp <= 0:
                    self.enemy_hp = 0
                    self.anim_queue.append(("enemy_death",))
                    self.generate_rewards()
                    return
                # ==========================================

                # 升级因果逆转：额外抵挡四分之一伤害
                if "因果逆轉+" in self.powers:
                    block_amount = damage // 4
                    self.player_block += block_amount
                    self.anim_queue.append(("status_enemy", f"抵擋 {block_amount} 傷害!", 250, SCREEN_H - 350))

            # --- 處理塞入廢牌邏輯 ---
            if self.enemy_intent_type == "DEBUFF":
                void_card = copy.deepcopy(CARD_DATABASE["VOID"])
                # 塞入抽牌堆頂部
                self.deck.append(void_card)
                random.shuffle(self.deck) # 這裡簡單處理，洗入牌庫
                self.anim_queue.append(("status_enemy", "塞入【虛空】！", SCREEN_W - 400, SCREEN_H * 0.35))

            actual_dmg = max(0, damage - self.player_block)
            self.player_hp -= actual_dmg
            self.stats_total_damage_taken += actual_dmg
            self._log(f"受到 {actual_dmg} 點傷害 (格擋 {self.player_block})")
            if actual_dmg > 0:
                self.anim_queue.append(("damage_player", actual_dmg, 200, SCREEN_H - 350))
                # 只有未升级的虚空血脉才在受伤时获得力量
                if "虛空血脈" in self.powers and "虛空血脈+" not in self.powers:
                    self.strength += 2
                    self.anim_queue.append(("status_enemy", "力量提升!", 250, SCREEN_H - 350))
        else:
            if status_msg:
                self._log(status_msg)
                self.anim_queue.append(("status_enemy", status_msg, SCREEN_W - 400, SCREEN_H * 0.3))

        if self.player_hp <= 0:
            self.player_hp = 0
            self.state = "GAMEOVER"
            return

        self.player_block = 0

        # --- 净善摄位持续效果处理 ---
        # --- 净善摄位持续效果处理 ---
        if self.maya_active and hasattr(self, 'maya_turns'):
            self.maya_turns -= 1  # 先扣除持续回合数

            if self.maya_turns <= 0:
                # 扣除后如果归零，立刻关闭状态，不带入下一回合
                self.grass_buff = False
                self.maya_active = False
            else:
                self.grass_buff = True

        # --- 聖遺物與技能效果：回合開始 ---
        self.energy = self.base_energy + self.next_turn_energy
        if "BlizzardStrayer" in [r["id"] for r in self.relics]:
            self.energy += 1
        self.next_turn_energy = 0

        retained_cards = [c for c in self.hand if c.retain]
        discarded_cards = [c for c in self.hand if not c.retain]

        self.discard.extend(discarded_cards)
        self.hand = retained_cards
        self.attack_played_count = 0
        self.cards_played_this_turn = 0 # 重置連擊數

        # 重置控制抗性和控制计数
        self.control_resistance = 0
        self.control_count_this_turn = 0

        self.turn_count += 1
        if self.enemy_stance_enabled:
            self.update_enemy_stance(announce=True)
            self.apply_stance_defend_heal()

        self.draw_cards(5)
        self.refresh_target_mark()
        self.reactions_this_turn = 0

        # --- 應用持續傷害 ---
        total_dot = 0

        # 草原核爆炸
        if self.bloom_cores > 0:
            bloom_dmg = 8 + (10 if "DeepwoodMemories" in [r["id"] for r in self.relics] else 0)
            total_dot += bloom_dmg * self.bloom_cores
            self.anim_queue.append(("status_enemy", f"草原核爆!{bloom_dmg * self.bloom_cores}", SCREEN_W - 400, SCREEN_H * 0.25))
            self.bloom_cores = 0

        # === 新增這裡：處理潮濕回合的衰減 ===
        if getattr(self, 'enemy_wet_turns', 0) > 0:
            self.enemy_wet_turns -= 1
            if self.enemy_wet_turns <= 0:
                self.enemy_wet = False
                self.anim_queue.append(("status_enemy", "潮濕消退", SCREEN_W - 400, SCREEN_H * 0.25))
        # =================================

        if self.enemy_dot_turns > 0:
            total_dot += self.enemy_dot_damage
            self.enemy_dot_turns -= 1

        if self.enemy_poison_turns > 0:
            total_dot += 5
            self.enemy_poison_turns -= 1
            self.anim_queue.append(("status_enemy", "中毒傷害!", SCREEN_W - 400, SCREEN_H * 0.35))

        if self.maya_active:
            bloom_dmg = 10
            if "DeepwoodMemories" in [r["id"] for r in self.relics]: bloom_dmg += 10
            bloom_dmg = int(bloom_dmg * 1.5)
            total_dot += bloom_dmg
            self.anim_queue.append(("status_enemy", "草原核爆發！", SCREEN_W - 400, SCREEN_H * 0.35))

        if total_dot > 0:
            self.enemy_hp -= total_dot
            self.anim_queue.append(("dot_damage", total_dot, SCREEN_W - 400, SCREEN_H * 0.4))
            if self.enemy_hp <= 0:
                self.enemy_hp = 0
                self.anim_queue.append(("enemy_death",))
                self.generate_rewards()
                return

        if self.enemy_vulnerable_turns > 0:
            self.enemy_vulnerable_turns -= 1

        self.roll_enemy_intent()

        if self.state == "ENEMY_TURN":
            self.state = "BATTLE"

    # --- 存檔系統 ---
    def _card_to_dict(self, card):
        """將卡牌序列化為字典"""
        return {
            "base_name": card.base_name,
            "upgraded": card.upgraded,
            "permanent_dmg_bonus": getattr(card, "permanent_dmg_bonus", 0),
            "cost": card.cost,
            "original_cost": card.original_cost,
            "is_temporary": getattr(card, "is_temporary", False),
            "is_marked": getattr(card, "is_marked", False),
        }

    def _card_from_dict(self, d):
        """從字典反序列化卡牌"""
        key = CARD_NAME_TO_KEY.get(d.get("base_name"))
        if not key:
            return None
        template = CARD_DATABASE.get(key)
        if not template:
            return None
        new_card = copy.deepcopy(template)
        if d.get("upgraded"):
            new_card.upgrade()
        new_card.permanent_dmg_bonus = d.get("permanent_dmg_bonus", 0)
        new_card.cost = d.get("cost", new_card.original_cost)
        new_card.original_cost = d.get("original_cost", new_card.cost)
        new_card.is_temporary = d.get("is_temporary", False)
        new_card.is_marked = d.get("is_marked", False)
        return new_card

    def _pile_to_dict(self, pile):
        """序列化牌堆"""
        return [self._card_to_dict(c) for c in pile]

    def _pile_from_dict(self, pile_list):
        """反序列化牌堆"""
        result = []
        for d in pile_list:
            card = self._card_from_dict(d)
            if card:
                result.append(card)
        return result

    def save_to_dict(self):
        """將當前戰鬥狀態序列化為字典"""
        return {
            "version": SAVE_VERSION,
            "state": self.state,
            "player": {
                "max_hp": self.player_max_hp,
                "hp": self.player_hp,
                "block": self.player_block,
                "base_energy": self.base_energy,
                "energy": self.energy,
                "strength": self.strength,
                "next_turn_energy": self.next_turn_energy,
            },
            "enemy": {
                "max_hp": self.enemy_max_hp,
                "hp": self.enemy_hp,
                "min_dmg": self.enemy_min_dmg,
                "max_dmg": self.enemy_max_dmg,
                "intent": self.enemy_intent,
                "name": self.enemy_name,
                "stage_type": self.stage_type,
                "dot_turns": self.enemy_dot_turns,
                "dot_damage": self.enemy_dot_damage,
                "stun_turns": self.enemy_stun_turns,
                "petrify_turns": self.enemy_petrify_turns,
                "frozen": self.enemy_frozen,
                "frozen_turns": self.enemy_frozen_turns,
                "wet": self.enemy_wet,
                "wet_turns": self.enemy_wet_turns,
                "vulnerable_turns": self.enemy_vulnerable_turns,
                "poison_turns": self.enemy_poison_turns,
                "intent_type": self.enemy_intent_type,
                "hit_shield": self.enemy_hit_shield,
                "shield_element": self.enemy_shield_element,
                "charge_turns": self.enemy_charge_turns,
                "charge_max": self.enemy_charge_max,
                "scaling_strength": self.enemy_scaling_strength,
                "thorns": self.enemy_thorns,
            },
            "battle": {
                "current_wave": self.current_wave,
                "max_waves": self.max_waves,
                "is_endless": self.is_endless,
                "endless_loop_count": self.endless_loop_count,
                "selected_mode": getattr(self, "selected_mode", "NORMAL"),
                "turn_count": self.turn_count,
                "reactions_this_turn": self.reactions_this_turn,
                "cards_played_this_turn": self.cards_played_this_turn,
                "attack_played_count": self.attack_played_count,
                "control_resistance": getattr(self, "control_resistance", 0),
                "control_count_this_turn": getattr(self, "control_count_this_turn", 0),
                "enemy_stance": self.enemy_stance,
                "enemy_stance_enabled": self.enemy_stance_enabled,
                "bloom_cores": self.bloom_cores,
            },
            "mechanics": {
                "maya_active": self.maya_active,
                "maya_turns": self.maya_turns,
                "grass_buff": self.grass_buff,
                "pyro_damage_bonus": self.pyro_damage_bonus,
            },
            "deck": self._pile_to_dict(self.deck),
            "hand": self._pile_to_dict(self.hand),
            "discard": self._pile_to_dict(self.discard),
            "exhaust_pile": self._pile_to_dict(self.exhaust_pile),
            "sidelined_power_cards": self._pile_to_dict(self.sidelined_power_cards),
            "owned_cards": self._pile_to_dict(self.owned_cards),
            "powers": self.powers,
            "powers_with_group": self.powers_with_group,
            "relics": self.relics,
            "obtained_rewards": self.obtained_rewards,
            "settings": {
                "volume": self.volume,
                "fullscreen": self.fullscreen,
                "flash_enabled": self.flash_enabled,
                "current_character": self.current_character,
            },
            "ui": {
                "show_deck": self.show_deck,
                "deck_scroll": self.deck_scroll,
                "deck_sort_mode": self.deck_sort_mode,
                "show_mechanics_guide": self.show_mechanics_guide,
                "mechanics_scroll": self.mechanics_scroll,
            },
            "stats": {
                "total_cards_played": self.stats_total_cards_played,
                "total_damage_dealt": self.stats_total_damage_dealt,
                "total_damage_taken": self.stats_total_damage_taken,
                "highest_wave": self.stats_highest_wave,
                "total_kills": self.stats_total_kills,
                "total_turns": self.stats_total_turns,
                "total_reactions": self.stats_total_reactions,
            },
            "achievements": list(self.unlocked_achievements),
        }

    def load_from_dict(self, data):
        """從字典恢復戰鬥狀態"""
        if data.get("version") != SAVE_VERSION:
            return False
        # 設置
        s = data.get("settings", {})
        self.volume = s.get("volume", 0.5)
        self.fullscreen = s.get("fullscreen", False)
        self.flash_enabled = s.get("flash_enabled", True)
        self.current_character = s.get("current_character", "Default")

        # 玩家
        p = data.get("player", {})
        self.player_max_hp = p.get("max_hp", 50)
        self.player_hp = p.get("hp", 50)
        self.player_block = p.get("block", 0)
        self.base_energy = p.get("base_energy", 3)
        self.energy = p.get("energy", self.base_energy)
        self.strength = p.get("strength", 0)
        self.next_turn_energy = p.get("next_turn_energy", 0)

        # 敵人
        e = data.get("enemy", {})
        self.enemy_max_hp = e.get("max_hp", 80)
        self.enemy_hp = e.get("hp", 80)
        self.enemy_min_dmg = e.get("min_dmg", 7)
        self.enemy_max_dmg = e.get("max_dmg", 12)
        self.enemy_intent = e.get("intent", 0)
        self.enemy_name = e.get("name", "基礎雜兵")
        self.enemy_image = load_enemy_image(self.enemy_name)
        self.stage_type = e.get("stage_type", "NORMAL")
        self.enemy_dot_turns = e.get("dot_turns", 0)
        self.enemy_dot_damage = e.get("dot_damage", 0)
        self.enemy_stun_turns = e.get("stun_turns", 0)
        self.enemy_petrify_turns = e.get("petrify_turns", 0)
        self.enemy_frozen = e.get("frozen", False)
        self.enemy_frozen_turns = e.get("frozen_turns", 0)
        self.enemy_wet = e.get("wet", False)
        self.enemy_wet_turns = e.get("wet_turns", 0)
        self.enemy_vulnerable_turns = e.get("vulnerable_turns", 0)
        self.enemy_poison_turns = e.get("poison_turns", 0)
        self.enemy_intent_type = e.get("intent_type", "ATTACK")
        self.enemy_hit_shield = e.get("hit_shield", 0)
        self.enemy_shield_element = e.get("shield_element", "None")
        self.enemy_charge_turns = e.get("charge_turns", 0)
        self.enemy_charge_max = e.get("charge_max", 4)
        self.enemy_scaling_strength = e.get("scaling_strength", 0)
        self.enemy_thorns = e.get("thorns", 0)

        # 戰鬥
        b = data.get("battle", {})
        self.current_wave = b.get("current_wave", 1)
        self.max_waves = b.get("max_waves", 30)
        self.is_endless = b.get("is_endless", False)
        self.endless_loop_count = b.get("endless_loop_count", 0)
        self.selected_mode = b.get("selected_mode", "NORMAL")
        self.turn_count = b.get("turn_count", 0)
        self.reactions_this_turn = b.get("reactions_this_turn", 0)
        self.cards_played_this_turn = b.get("cards_played_this_turn", 0)
        self.attack_played_count = b.get("attack_played_count", 0)
        self.control_resistance = b.get("control_resistance", 0)
        self.control_count_this_turn = b.get("control_count_this_turn", 0)
        self.enemy_stance = b.get("enemy_stance", "ATTACK")
        self.enemy_stance_enabled = b.get("enemy_stance_enabled", False)
        self.bloom_cores = b.get("bloom_cores", 0)

        # 機制
        m = data.get("mechanics", {})
        self.maya_active = m.get("maya_active", False)
        self.maya_turns = m.get("maya_turns", 0)
        self.grass_buff = m.get("grass_buff", False)
        self.pyro_damage_bonus = m.get("pyro_damage_bonus", 0)

        # 統計
        st = data.get("stats", {})
        self.stats_total_cards_played = st.get("total_cards_played", 0)
        self.stats_total_damage_dealt = st.get("total_damage_dealt", 0)
        self.stats_total_damage_taken = st.get("total_damage_taken", 0)
        self.stats_highest_wave = st.get("highest_wave", 1)
        self.stats_total_kills = st.get("total_kills", 0)
        self.stats_total_turns = st.get("total_turns", 0)
        self.stats_total_reactions = st.get("total_reactions", 0)

        # 成就
        self.unlocked_achievements = set(data.get("achievements", []))

        # 牌堆
        self.deck = self._pile_from_dict(data.get("deck", []))
        self.hand = self._pile_from_dict(data.get("hand", []))
        self.discard = self._pile_from_dict(data.get("discard", []))
        self.exhaust_pile = self._pile_from_dict(data.get("exhaust_pile", []))
        self.sidelined_power_cards = self._pile_from_dict(data.get("sidelined_power_cards", []))
        self.owned_cards = self._pile_from_dict(data.get("owned_cards", []))

        self.powers = data.get("powers", [])
        self.powers_with_group = data.get("powers_with_group", {})
        self.relics = data.get("relics", [])
        self.obtained_rewards = data.get("obtained_rewards", [])

        # UI
        u = data.get("ui", {})
        self.show_deck = u.get("show_deck", False)
        self.deck_scroll = u.get("deck_scroll", 0)
        self.deck_sort_mode = u.get("deck_sort_mode", "TYPE")
        self.show_mechanics_guide = u.get("show_mechanics_guide", False)
        self.mechanics_scroll = u.get("mechanics_scroll", 0)

        # 重置臨時動畫狀態
        self.state = "BATTLE"
        self.anim_queue = []
        self.jump_progress = 0
        self.previous_battle_state = None
        return True
