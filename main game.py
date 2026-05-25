import pygame
import random
import sys
import copy
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

# --- 1. 初始化與基礎配置 ---
pygame.init()
SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Project: Genshin Spire")

# 字體加載
font_main = pygame.font.SysFont(["Microsoft YaHei", "SimHei", "Arial"], 20)
font_hp = pygame.font.SysFont("Arial", 22, bold=True)
font_big = pygame.font.SysFont(["SimHei", "Arial"], 60)

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GOLD = (255, 215, 0)
GREEN = (50, 200, 50)
RED = (220, 50, 50)
BLUE = (50, 150, 255)
ORANGE = (255, 165, 0)


class Animation:
    def __init__(self):
        self.active = False

    def update(self, dt):
        pass

    def draw(self, surface):
        pass


class FloatText(Animation):
    def __init__(self, x, y, text, color, size=28):
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.alpha = 255
        self.active = True
        self.timer = 0
        self.duration = 1.0
        self.velocity = -80

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        self.y += self.velocity * dt
        self.alpha = max(0, 255 - int((self.timer / self.duration) * 255))
        if self.timer >= self.duration:
            self.active = False

    def draw(self, surface):
        if not self.active or self.alpha <= 0:
            return
        font = pygame.font.SysFont("Arial", self.size, bold=True)
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        rect = text_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(text_surf, rect)


class CardFly(Animation):
    def __init__(self, card, start_pos, end_pos, callback=None):
        super().__init__()
        self.card = card
        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos
        self.x, self.y = start_pos
        self.callback = callback
        self.active = True
        self.timer = 0
        self.duration = 0.3
        self.progress = 0

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        self.progress = min(1.0, self.timer / self.duration)
        t = self.progress
        ease = 1 - (1 - t) * (1 - t)
        self.x = self.start_x + (self.end_x - self.start_x) * ease
        self.y = self.start_y + (self.end_y - self.start_y) * ease
        if self.progress >= 1.0:
            self.active = False
            if self.callback:
                self.callback()

    def draw(self, surface):
        if not self.active:
            return
        self.card.draw(surface, int(self.x), int(self.y), False)


class FlashScreen(Animation):
    def __init__(self, color=(255, 0, 0), duration=0.2):
        super().__init__()
        self.color = color
        self.duration = duration
        self.timer = 0
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.timer >= self.duration:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        alpha = int(100 * (1 - self.timer / self.duration))
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((*self.color, alpha))
        surface.blit(overlay, (0, 0))


class ShakeScreen(Animation):
    def __init__(self, intensity=10, duration=0.3):
        super().__init__()
        self.intensity = intensity
        self.duration = duration
        self.timer = 0
        self.active = True
        self.offset_x = 0
        self.offset_y = 0

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.timer < self.duration:
            import math
            self.offset_x = math.sin(self.timer * 50) * self.intensity * (1 - self.timer / self.duration)
            self.offset_y = math.cos(self.timer * 50) * self.intensity * (1 - self.timer / self.duration)
        else:
            self.active = False
            self.offset_x = 0
            self.offset_y = 0

    def draw(self, surface):
        pass


class AnimationManager:
    def __init__(self):
        self.animations = []
        self.screen_shake = None

    def add(self, anim):
        self.animations.append(anim)

    def update(self, dt):
        for anim in self.animations[:]:
            anim.update(dt)
            if not anim.active:
                self.animations.remove(anim)
        if self.screen_shake:
            self.screen_shake.update(dt)

    def draw(self, surface):
        for anim in self.animations:
            anim.draw(surface)

    def shake_screen(self, intensity=10, duration=0.3):
        self.screen_shake = ShakeScreen(intensity, duration)

    def get_shake_offset(self):
        if self.screen_shake and self.screen_shake.active:
            return self.screen_shake.offset_x, self.screen_shake.offset_y
        return 0, 0

    def has_active_animations(self):
        return len(self.animations) > 0


# --- 2. 核心類與卡片資料庫 ---
class Card:
    def __init__(self, name, cost, damage=0, block=0, description=""):
        self.name = name
        self.cost = cost
        self.base_damage = damage
        self.base_block = block
        self.damage = damage
        self.block = block
        self.custom_desc = description  # 新增：自訂特殊效果描述
        self.rect = pygame.Rect(0, 0, 120, 170)

    def draw(self, surface, x, y, is_hovered, is_selected=False):
        self.rect.topleft = (x, y - (35 if is_hovered else 0))

        if is_selected:
            pygame.draw.rect(surface, GOLD, self.rect.inflate(10, 10), border_radius=10)

        pygame.draw.rect(surface, (40, 40, 60), self.rect, border_radius=8)
        color = (110, 100, 180) if is_selected else ((100, 100, 150) if is_hovered else (70, 70, 100))
        pygame.draw.rect(surface, color, self.rect.inflate(-4, -4), border_radius=6)

        # 繪製卡名與消耗
        name_ts = font_main.render(self.name, True, WHITE)
        cost_ts = font_hp.render(str(self.cost), True, GOLD)
        surface.blit(name_ts, (self.rect.x + 12, self.rect.y + 12))
        surface.blit(cost_ts, (self.rect.x + 95, self.rect.y + 8))

        # 智慧型動態描述文字
        if self.custom_desc:
            desc = self.custom_desc
        else:
            desc = f"造成 {self.damage} 傷害" if self.damage > 0 else f"獲得 {self.block} 防禦"

        desc_ts = font_main.render(desc, True, (200, 200, 200))
        surface.blit(desc_ts, (self.rect.x + 12, self.rect.y + 125))


# 🌟 新增：卡片資料庫 (所有的卡片原型都存在這裡)
CARD_DATABASE = {
    # 基礎卡
    "STRIKE": Card("打擊", 1, damage=6),
    "DEFEND": Card("防禦", 1, block=5),

    # 🌟 新增基礎/進階卡片
    "PIERCE": Card("西風重擊", 1, damage=9, description="造成 9 傷害"),
    "IRON_WALL": Card("千岩固牢", 2, block=12, description="獲得 12 防禦"),

    # 稀有獎勵卡池
    "REWARD_1": Card("天街巡遊", 2, damage=16),
    "REWARD_2": Card("星塵結界", 1, block=10),
    "REWARD_3": Card("元素爆發", 3, damage=25),
    "REWARD_4": Card("荒星防護", 2, block=15),

    # 🌟 新增稀有獎勵卡片
    "BURST_FLAME": Card("大劍重擊", 2, damage=18, description="揮舞大劍造成18傷害"),
    "STORM_SHIELD": Card("旋風護盾", 1, damage=4, block=6, description="攻防一體!4傷6盾"),
    "SACRIFICE": Card("不滅之火", 0, damage=12, description="0費!造成12爆發傷害")
}


class BattleManager:
    def __init__(self):
        self.state = "STARTUP"
        self.alpha = 0
        self.selected_mode = None

        # 基礎玩家數值
        self.player_max_hp = 50
        self.player_hp = 50
        self.player_block = 0
        self.base_energy = 3
        self.energy = 3

        # 基礎怪物數值
        self.enemy_max_hp = 80
        self.enemy_hp = 80
        self.enemy_min_dmg = 7
        self.enemy_max_dmg = 12
        self.enemy_intent = 0

        # 牌組
        self.deck = []
        self.hand = []
        self.discard = []
        self.reward_cards = []
        self.selected_reward = None
        self.show_deck = False
        
        # 波次系统
        self.current_wave = 1
        self.max_waves = 5
        
        # 回合计数系统
        self.turn_count = 0
        self.max_hand = 5
        
        # 动画队列
        self.anim_queue = []
        self.last_enemy_hp = 80
        self.last_player_hp = 50
        
        # 已获取的奖励卡记录
        self.obtained_rewards = []

    def apply_mode_modifiers(self, mode_name):
        self.selected_mode = mode_name

        # 使用 copy.deepcopy 從資料庫安全複製卡片，避免污染原型數值
        # 初始牌組微調：4張打擊、4張防禦、1張西風重擊、1張千岩固牢
        self.deck = [copy.deepcopy(CARD_DATABASE["STRIKE"]) for _ in range(4)] + \
                    [copy.deepcopy(CARD_DATABASE["DEFEND"]) for _ in range(4)] + \
                    [copy.deepcopy(CARD_DATABASE["PIERCE"])], \
            [copy.deepcopy(CARD_DATABASE["IRON_WALL"])]

        # 攤平結構 (因上方的逗號產生的 tuple 修正)
        self.deck = [copy.deepcopy(CARD_DATABASE["STRIKE"]) for _ in range(4)] + \
                    [copy.deepcopy(CARD_DATABASE["DEFEND"]) for _ in range(4)] + \
                    [copy.deepcopy(CARD_DATABASE["PIERCE"])], \
            [copy.deepcopy(CARD_DATABASE["IRON_WALL"])]
        # 修正陣列巢狀組合
        self.deck = []
        for _ in range(4): self.deck.append(copy.deepcopy(CARD_DATABASE["STRIKE"]))
        for _ in range(4): self.deck.append(copy.deepcopy(CARD_DATABASE["DEFEND"]))
        self.deck.append(copy.deepcopy(CARD_DATABASE["PIERCE"]))
        self.deck.append(copy.deepcopy(CARD_DATABASE["IRON_WALL"]))

        if mode_name == "BURST":
            self.base_energy = 4
            self.energy = 4
            for card in self.deck:
                if card.base_damage > 0:
                    card.damage = card.base_damage + 5
                    if card.custom_desc == "":  # 同步更新描述
                        card.custom_desc = f"造成 {card.damage} 傷害"

        elif mode_name == "HARD":
            self.enemy_max_hp = 120
            self.enemy_hp = 120
            self.enemy_min_dmg += 6
            self.enemy_max_dmg += 6

        random.shuffle(self.deck)
        self.enemy_intent = random.randint(self.enemy_min_dmg, self.enemy_max_dmg)
        self.state = "BATTLE"
        self.draw_cards(5)

    def draw_cards(self, num):
        for _ in range(num):
            if len(self.hand) >= self.max_hand:
                break
            if not self.deck:
                self.deck, self.discard = self.discard[:], []
                random.shuffle(self.deck)
            if self.deck:
                self.hand.append(self.deck.pop())

    def play_card(self, card, start_x, start_y):
        if self.energy >= card.cost:
            self.energy -= card.cost
            
            target_x = SCREEN_W - 400 if card.damage > 0 else 250
            target_y = SCREEN_H * 0.4 if card.damage > 0 else SCREEN_H - 300
            
            self.anim_queue.append(("card_fly", card, start_x, start_y, target_x, target_y))
            
            self.enemy_hp -= card.damage
            self.player_block += card.block
            self.hand.remove(card)
            self.discard.append(card)
            
            if card.damage > 0:
                self.anim_queue.append(("damage_enemy", card.damage, SCREEN_W - 400, SCREEN_H * 0.35))
            if card.block > 0:
                self.anim_queue.append(("block_player", card.block, 250, SCREEN_H - 350))

            if self.enemy_hp <= 0:
                self.enemy_hp = 0
                self.generate_rewards()
            return True
        return False

    def generate_rewards(self):
        self.state = "REWARD"
        self.selected_reward = None

        # 🌟 從擴充後的稀有卡池中隨機挑選 3 張作為獎勵（排除已獲取的）
        pool_keys = ["REWARD_1", "REWARD_2", "REWARD_3", "REWARD_4", "BURST_FLAME", "STORM_SHIELD", "SACRIFICE"]
        
        # 过滤掉已获取的奖励卡
        available_keys = [key for key in pool_keys if key not in self.obtained_rewards]
        
        # 如果所有奖励都拿过了，重置记录
        if len(available_keys) < 3:
            self.obtained_rewards = []
            available_keys = pool_keys
        
        pool = [copy.deepcopy(CARD_DATABASE[key]) for key in available_keys]

        if self.selected_mode == "BURST":
            for card in pool:
                if card.base_damage > 0:
                    card.damage = card.base_damage + 5
                    # 如果不是預設傷害格式，重新包裝描述
                    card.custom_desc = f"無雙!造成 {card.damage} 傷害" if card.block == 0 else f"無雙!{card.damage}傷/{card.block}盾"

        self.reward_cards = random.sample(pool, 3)

    def choose_reward(self):
        if self.selected_reward:
            self.deck.append(self.selected_reward)
            # 记录已获取的奖励卡
            reward_keys = {
                "大劍重擊": "REWARD_1",
                "荒星防護": "REWARD_2",
                "元素爆發": "REWARD_3",
                "風刃連擊": "REWARD_4",
                "不滅之火": "BURST_FLAME",
                "旋風護盾": "STORM_SHIELD",
                "元素之怒": "SACRIFICE"
            }
            card_key = reward_keys.get(self.selected_reward.name)
            if card_key and card_key not in self.obtained_rewards:
                self.obtained_rewards.append(card_key)
        
        self.current_wave += 1
        if self.current_wave > self.max_waves:
            self.state = "VICTORY"
        else:
            self.start_next_wave()

    def start_next_wave(self):
        self.enemy_max_hp = 80 + (self.current_wave - 1) * 30
        self.enemy_hp = self.enemy_max_hp
        self.enemy_min_dmg = 7 + (self.current_wave - 1) * 2
        self.enemy_max_dmg = 12 + (self.current_wave - 1) * 2
        
        if self.selected_mode == "HARD":
            self.enemy_hp += 40
            self.enemy_min_dmg += 6
            self.enemy_max_dmg += 6
        
        self.player_block = 0
        self.energy = self.base_energy
        
        # 没打出的手牌放回牌库
        self.deck.extend(self.hand)
        self.hand.clear()
        
        # 重置回合计数
        self.turn_count = 0
        
        random.shuffle(self.deck)
        self.draw_cards(5)
        self.enemy_intent = random.randint(self.enemy_min_dmg, self.enemy_max_dmg)
        self.state = "BATTLE"

    def end_turn(self):
        damage = max(0, self.enemy_intent - self.player_block)
        self.player_hp -= damage
        if damage > 0:
            self.anim_queue.append(("damage_player", damage, 200, SCREEN_H - 350))
        if self.player_hp <= 0:
            self.player_hp = 0
            self.state = "GAMEOVER"

        self.player_block = 0
        self.energy = self.base_energy
        
        # 没打出的手牌放回牌库
        self.deck.extend(self.hand)
        self.hand.clear()
        
        # 回合计数
        self.turn_count += 1
        
        # 每2回合把弃牌堆洗回牌库
        if self.turn_count % 2 == 0:
            self.deck.extend(self.discard)
            self.discard.clear()
            random.shuffle(self.deck)
        
        self.draw_cards(5)
        self.enemy_intent = random.randint(self.enemy_min_dmg, self.enemy_max_dmg)


# --- 3. 繪製組件（適應解析度） ---
def draw_main_menu_surface(surface, mx, my):
    w, h = surface.get_size()
    title_ts = font_big.render("Project: Genshin Spire", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.25)))

    buttons = [
        {"id": "START", "text": "開始遊戲"},
        {"id": "SETTINGS", "text": "遊戲設置"},
        {"id": "QUIT", "text": "退出遊戲"}
    ]
    menu_rects = {}
    for i, btn in enumerate(buttons):
        rect = pygame.Rect(w // 2 - 150, h * 0.45 + i * 80, 300, 50)
        menu_rects[btn["id"]] = rect
        is_hover = rect.collidepoint((mx, my))
        color = (100, 100, 150) if is_hover else (60, 60, 80)
        pygame.draw.rect(surface, color, rect, border_radius=8)
        if is_hover: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=8)
        text_ts = font_main.render(btn["text"], True, WHITE)
        surface.blit(text_ts, text_ts.get_rect(center=rect.center))
    return menu_rects


def draw_settings_surface(surface, mx, my):
    w, h = surface.get_size()
    title_ts = font_big.render("遊戲設置", True, WHITE)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.2)))

    label_ts = font_hp.render("調整視窗解析度：", True, (200, 200, 200))
    surface.blit(label_ts, (w // 2 - 250, h * 0.4))

    res_options = [
        {"id": "RES_1280", "text": "1280 x 720 (預設)", "w": 1280, "h": 720},
        {"id": "RES_1600", "text": "1600 x 900 (放大)", "w": 1600, "h": 900}
    ]
    setting_rects = {}
    for i, opt in enumerate(res_options):
        rect = pygame.Rect(w // 2 - 50 + i * 160, h * 0.38, 150, 45)
        setting_rects[opt["id"]] = (rect, opt["w"], opt["h"])
        is_current = (w == opt["w"])
        is_hover = rect.collidepoint((mx, my))
        color = (50, 150, 50) if is_current else ((100, 100, 120) if is_hover else (50, 50, 60))
        pygame.draw.rect(surface, color, rect, border_radius=5)
        if is_hover or is_current: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=5)
        txt = font_main.render(opt["text"], True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    back_rect = pygame.Rect(w // 2 - 100, h * 0.7, 200, 50)
    setting_rects["BACK"] = (back_rect, 0, 0)
    is_back_hover = back_rect.collidepoint((mx, my))
    pygame.draw.rect(surface, (150, 50, 50) if is_back_hover else (100, 40, 40), back_rect, border_radius=8)
    back_ts = font_main.render("返回主選單", True, WHITE)
    surface.blit(back_ts, back_ts.get_rect(center=back_rect.center))
    return setting_rects


def draw_main_menu(mx, my):
    screen.fill((20, 20, 30))
    return draw_main_menu_surface(screen, mx, my)


def draw_settings(mx, my):
    screen.fill((25, 25, 35))
    return draw_settings_surface(screen, mx, my)


def draw_mode_select_surface(surface, mx, my):
    w, h = surface.get_size()
    title_ts = font_big.render("請選擇遊戲模式", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.15)))

    modes = [
        {"id": "NORMAL", "title": "普通模式", "desc": "原汁原味的標準冒險體驗", "color": (100, 100, 100)},
        {"id": "BURST", "title": "無雙模式", "desc": "數值增加：初始能量變 4，卡牌傷害增加 5", "color": (50, 150, 50)},
        {"id": "HARD", "title": "高難模式", "desc": "數值增加：敵人血量增至 120，攻擊傷害增加 6", "color": (150, 50, 50)}
    ]
    btn_rects = {}
    for i, mode in enumerate(modes):
        rect = pygame.Rect(w // 2 - 300, h * 0.33 + i * 130, 600, 90)
        btn_rects[mode["id"]] = rect
        is_hover = rect.collidepoint((mx, my))
        bg_color = [min(255, c + 30) if is_hover else c for c in mode["color"]]
        pygame.draw.rect(surface, bg_color, rect, border_radius=10)
        if is_hover: pygame.draw.rect(surface, GOLD, rect, width=3, border_radius=10)
        t_ts = font_hp.render(mode["title"], True, WHITE)
        d_ts = font_main.render(mode["desc"], True, (220, 220, 220))
        surface.blit(t_ts, (rect.x + 30, rect.y + 20))
        surface.blit(d_ts, (rect.x + 30, rect.y + 50))
    return btn_rects


def draw_mode_select(mx, my):
    screen.fill((25, 25, 35))
    return draw_mode_select_surface(screen, mx, my)


def draw_ui_surface(surface, game, mx, my):
    w, h = surface.get_size()

    mode_text = "普通" if game.selected_mode == "NORMAL" else (
        "無雙 (傷害+5, 能量+1)" if game.selected_mode == "BURST" else "高難 (怪物強化)")
    mode_ts = font_main.render(f"當前模式: {mode_text}", True, (180, 180, 180))
    surface.blit(mode_ts, (20, 20))
    
    wave_ts = font_main.render(f"波次: {game.current_wave} / {game.max_waves}", True, GOLD)
    surface.blit(wave_ts, (20, 50))

    if game.enemy_hp > 0:
        pygame.draw.rect(surface, (150, 50, 50), (w - 430, h * 0.35, 120, 120), border_radius=10)
        draw_bar(w - 480, h * 0.28, game.enemy_hp, game.enemy_max_hp, 0, RED, "ENEMY")
        intent_ts = font_main.render(f"意圖攻擊: {game.enemy_intent}", True, WHITE)
        surface.blit(intent_ts, (w - 460, h * 0.22))

    draw_bar(100, h - 340, game.player_hp, game.player_max_hp, game.player_block, GREEN, "PLAYER")
    energy_ts = font_big.render(f"E: {game.energy}/{game.base_energy}", True, GOLD)
    surface.blit(energy_ts, (100, h - 310))

    hovered_card = None
    hovered_pos = (0, 0)
    for card in reversed(game.hand):
        if card.rect.collidepoint((mx, my)):
            hovered_card = card
            hovered_pos = (card.rect.x, card.rect.y)
            break

    for i, card in enumerate(game.hand):
        spacing = min(140, (w - 280) // max(1, len(game.hand)))
        card.draw(surface, 100 + i * spacing, h - 200, (card == hovered_card))

    # 牌库展示（左侧）
    draw_pile(surface, 50, h - 200, len(game.deck), "牌庫", BLUE)
    
    # 弃牌堆展示（右侧）
    draw_pile(surface, w - 100, h - 200, len(game.discard), "棄牌", ORANGE)
    
    btn_rect = pygame.Rect(w - 230, h - 120, 150, 50)
    pygame.draw.rect(surface, (80, 80, 80), btn_rect, border_radius=5)
    btn_text = font_main.render("結束回合", True, WHITE)
    surface.blit(btn_text, btn_text.get_rect(center=btn_rect.center))
    
    deck_btn_rect = pygame.Rect(w - 390, h - 120, 120, 50)
    pygame.draw.rect(surface, (60, 80, 120), deck_btn_rect, border_radius=5)
    deck_ts = font_main.render(f"牌組 ({len(game.deck)})", True, WHITE)
    surface.blit(deck_ts, deck_ts.get_rect(center=deck_btn_rect.center))
    
    return hovered_card, btn_rect, deck_btn_rect


def draw_pile(surface, x, y, count, label, color):
    """绘制牌堆展示"""
    # 牌堆背景
    pygame.draw.rect(surface, (40, 40, 50), (x - 25, y - 60, 50, 70), border_radius=4)
    
    # 牌堆堆叠效果
    for i in range(min(count, 5)):
        offset = i * 3
        pygame.draw.rect(surface, color, (x - 22 + offset*0.5, y - 57 + offset, 44 - offset, 64 - offset), border_radius=3)
    
    # 数量文字
    count_ts = font_big.render(str(count), True, WHITE)
    surface.blit(count_ts, (x - count_ts.get_width() // 2, y - 25))
    
    # 标签文字
    label_ts = font_hp.render(label, True, (180, 180, 180))
    surface.blit(label_ts, (x - label_ts.get_width() // 2, y + 10))


def draw_ui(game, mx, my):
    screen.fill((30, 30, 40))
    return draw_ui_surface(screen, game, mx, my)


def draw_reward_screen_surface(surface, game, mx, my):
    w, h = surface.get_size()
    title_ts = font_big.render("戰鬥勝利！", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.14)))
    sub_ts = font_main.render("請選擇一項獎勵", True, (200, 200, 200))
    surface.blit(sub_ts, sub_ts.get_rect(center=(w // 2, h * 0.2)))

    hovered_reward = None
    for card in game.reward_cards:
        if card.rect.collidepoint((mx, my)):
            hovered_reward = card
            break

    start_x = w // 2 - (3 * 140 + 2 * 60) // 2
    for i, card in enumerate(game.reward_cards):
        card.draw(surface, start_x + i * 200, h * 0.38, (card == hovered_reward), (card == game.selected_reward))

    confirm_rect = pygame.Rect(w // 2 - 100, h * 0.78, 200, 50)
    btn_color = (50, 180, 50) if game.selected_reward else (60, 60, 60)
    pygame.draw.rect(surface, btn_color, confirm_rect, border_radius=5)
    btn_text = font_main.render("點擊跳過" if not game.selected_reward else "確認領取", True, WHITE)
    surface.blit(btn_text, btn_text.get_rect(center=confirm_rect.center))
    return hovered_reward, confirm_rect


def draw_reward_screen(game, mx, my):
    screen.fill((25, 25, 35))
    return draw_reward_screen_surface(screen, game, mx, my)


def draw_deck_view_surface(surface, game, mx, my):
    w, h = surface.get_size()
    
    title_ts = font_big.render("牌組", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.08)))
    
    all_cards = game.deck + game.hand + game.discard
    cards_by_name = {}
    for card in all_cards:
        if card.name not in cards_by_name:
            cards_by_name[card.name] = []
        cards_by_name[card.name].append(card)
    
    start_y = h * 0.15
    col_x = w // 4
    row_y = start_y
    max_per_row = 6
    card_spacing = 130
    row_spacing = 180
    
    for idx, (name, cards) in enumerate(cards_by_name.items()):
        count = len(cards)
        card = cards[0]
        row = idx // max_per_row
        col = idx % max_per_row
        x = col_x + col * card_spacing
        y = start_y + row * row_spacing
        card.draw(surface, x, y, False)
        
        count_ts = font_hp.render(f"x{count}", True, GOLD)
        surface.blit(count_ts, (card.rect.x + card.rect.width - 30, card.rect.y + card.rect.height - 30))
    
    close_rect = pygame.Rect(w // 2 - 100, h - 80, 200, 50)
    pygame.draw.rect(surface, (150, 50, 50), close_rect, border_radius=5)
    close_ts = font_main.render("關閉 (D)", True, WHITE)
    surface.blit(close_ts, close_ts.get_rect(center=close_rect.center))
    
    hint_ts = font_main.render(f"牌組總數: {len(all_cards)} | 牌庫: {len(game.deck)} | 手牌: {len(game.hand)} | 棄牌堆: {len(game.discard)}", True, (200, 200, 200))
    surface.blit(hint_ts, hint_ts.get_rect(center=(w // 2, h * 0.95)))
    
    return close_rect


def draw_deck_view(game, mx, my):
    screen.fill((25, 25, 35))
    return draw_deck_view_surface(screen, game, mx, my)

def draw_bar(x, y, cur, mx, block, color, label):
    width = 250
    pygame.draw.rect(screen, (50, 50, 50), (x, y, width, 15))
    if mx > 0: pygame.draw.rect(screen, color, (x, y, int((cur / mx) * width), 15))
    if block > 0:
        pygame.draw.rect(screen, BLUE, (x - 35, y - 5, 25, 25), border_radius=4)
        b_ts = font_main.render(str(block), True, WHITE)
        screen.blit(b_ts, b_ts.get_rect(center=(x - 22, y + 7)))
    val_ts = font_hp.render(f"{cur}/{mx}", True, WHITE)
    screen.blit(val_ts, (x + width // 2 - val_ts.get_width() // 2, y - 25))


# --- 音效管理器 ---
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()
    
    def load_sounds(self):
        sound_files = ["attack", "shield", "hurt"]
        for name in sound_files:
            mp3_path = os.path.join(get_base_path(), "audio", f"{name}.mp3")
            wav_path = os.path.join(get_base_path(), "audio", f"{name}.wav")
            
            try:
                if os.path.exists(mp3_path):
                    self.sounds[name] = pygame.mixer.Sound(mp3_path)
                elif os.path.exists(wav_path):
                    self.sounds[name] = pygame.mixer.Sound(wav_path)
                else:
                    print(f"未找到音效文件: {name}.mp3 或 {name}.wav")
                    self.sounds[name] = None
                    continue
                
                self.sounds[name].set_volume(0.5)
            except Exception as e:
                print(f"无法加载音效 {name}: {e}")
                self.sounds[name] = None
    
    def play(self, sound_name):
        sound = self.sounds.get(sound_name)
        if sound:
            sound.play()


# --- 4. 主程序 ---
def play_bgm():
    try:
        pygame.mixer.init()
        bgm_path = os.path.join(get_base_path(), "audio", "bgm.mp3")
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.8)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"无法播放背景音乐: {e}")

def main():
    global screen, anim_mgr, sound_mgr
    play_bgm()
    
    game = BattleManager()
    anim_mgr = AnimationManager()
    sound_mgr = SoundManager()
    clock = pygame.time.Clock()
    menu_rects = {}
    setting_rects = {}
    mode_rects = {}
    last_time = pygame.time.get_ticks()    
    while True:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0
        last_time = current_time
        
        anim_mgr.update(dt)
        
        mx, my = pygame.mouse.get_pos()
        w, h = screen.get_size()
        
        shake_x, shake_y = anim_mgr.get_shake_offset()
        use_shake = shake_x != 0 or shake_y != 0
        
        if use_shake:
            game_surface = pygame.Surface((w, h))
            game_surface.fill((30, 30, 40))
            main_surface = game_surface
        else:
            screen.fill((30, 30, 40))
            main_surface = screen

        if game.state == "STARTUP":
            if game.alpha < 255:
                game.alpha += 5
            else:
                pygame.time.delay(300)
                game.state = "MAIN_MENU"
            logo_ts = font_big.render("GENSHIN START", True, GOLD)
            logo_ts.set_alpha(game.alpha)
            main_surface.blit(logo_ts, logo_ts.get_rect(center=(w // 2, h // 2)))

        elif game.state == "MAIN_MENU":
            menu_rects = draw_main_menu_surface(main_surface, mx, my)

        elif game.state == "SETTINGS":
            setting_rects = draw_settings_surface(main_surface, mx, my)

        elif game.state == "MODE_SELECT":
            mode_rects = draw_mode_select_surface(main_surface, mx, my)

        elif game.state == "BATTLE":
            if game.show_deck:
                close_rect = draw_deck_view_surface(main_surface, game, mx, my)
            else:
                hovered, btn_rect, deck_btn_rect = draw_ui_surface(main_surface, game, mx, my)

        elif game.state == "REWARD":
            hovered_reward, confirm_rect = draw_reward_screen_surface(main_surface, game, mx, my)

        elif game.state in ["VICTORY", "GAMEOVER"]:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            main_surface.blit(overlay, (0, 0))
            msg = "VICTORY!" if game.state == "VICTORY" else "YOU DIED"
            msg_ts = font_big.render(msg, True, GOLD if game.state == "VICTORY" else RED)
            main_surface.blit(msg_ts, msg_ts.get_rect(center=(w // 2, h // 2 - 30)))
            hint_ts = font_main.render("點擊滑鼠左鍵返回主選單", True, WHITE)
            main_surface.blit(hint_ts, hint_ts.get_rect(center=(w // 2, h // 2 + 50)))
        
        if use_shake:
            screen.fill((30, 30, 40))
            screen.blit(game_surface, (int(shake_x), int(shake_y)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    if game.state == "BATTLE":
                        game.show_deck = not game.show_deck
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.state == "MAIN_MENU":
                    if menu_rects["START"].collidepoint((mx, my)):
                        game.state = "MODE_SELECT"
                    elif menu_rects["SETTINGS"].collidepoint((mx, my)):
                        game.state = "SETTINGS"
                    elif menu_rects["QUIT"].collidepoint((mx, my)):
                        pygame.quit()
                        sys.exit()

                elif game.state == "SETTINGS":
                    if setting_rects["BACK"][0].collidepoint((mx, my)):
                        game.state = "MAIN_MENU"
                    else:
                        for res_id, (rect, target_w, target_h) in setting_rects.items():
                            if res_id != "BACK" and rect.collidepoint((mx, my)):
                                screen = pygame.display.set_mode((target_w, target_h))
                                break

                elif game.state == "MODE_SELECT":
                    for mode_id, rect in mode_rects.items():
                        if rect.collidepoint((mx, my)):
                            game.apply_mode_modifiers(mode_id)
                            break

                elif game.state == "BATTLE":
                    if game.show_deck:
                        if close_rect.collidepoint((mx, my)):
                            game.show_deck = False
                    else:
                        if hovered:
                            card_x = hovered.rect.x
                            card_y = hovered.rect.y
                            game.play_card(hovered, card_x, card_y)
                        elif btn_rect.collidepoint((mx, my)):
                            game.end_turn()
                        elif deck_btn_rect.collidepoint((mx, my)):
                            game.show_deck = True

                elif game.state == "REWARD":
                    if hovered_reward:
                        game.selected_reward = None if game.selected_reward == hovered_reward else hovered_reward
                    elif confirm_rect.collidepoint((mx, my)):
                        game.choose_reward()

                elif game.state in ["VICTORY", "GAMEOVER"]:
                    game = BattleManager()

        for _ in range(len(game.anim_queue)):
            anim_data = game.anim_queue.pop(0)
            anim_type = anim_data[0]
            if anim_type == "card_fly":
                card, start_x, start_y, target_x, target_y = anim_data[1:]
                anim_mgr.add(CardFly(card, (start_x, start_y), (target_x, target_y)))
            elif anim_type == "damage_enemy":
                _, value, x, y = anim_data
                anim_mgr.add(FloatText(x, y, f"-{value}", RED, 36))
                anim_mgr.shake_screen(2, 0.1)
                sound_mgr.play("attack")
            elif anim_type == "damage_player":
                _, value, x, y = anim_data
                anim_mgr.add(FloatText(x, y, f"-{value}", RED, 36))
                anim_mgr.shake_screen(8, 0.2)
                sound_mgr.play("hurt")
            elif anim_type == "block_player":
                _, value, x, y = anim_data
                anim_mgr.add(FloatText(x, y, f"+{value}", BLUE, 28))
                sound_mgr.play("shield")

        anim_mgr.draw(screen)
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
