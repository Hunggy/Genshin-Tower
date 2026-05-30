import pygame
import math
import random

from .config import ELEMENT_COLORS, WHITE, GOLD, RED, SCREEN_W, SCREEN_H
from .resources import get_ui_font, font_main, font_hp, font_desc, element_icons


class Card:
    def __init__(self, name, cost, damage=0, block=0, description="", type="ATTACK", hits=1, exhaust=False, retain=False, is_x_cost=False, element="None"):
        self.name = name
        self.base_name = name
        self.cost = cost
        self.original_cost = cost
        self.is_x_cost = is_x_cost
        self.base_damage = damage
        self.base_block = block
        self.damage = damage
        self.block = block
        self.custom_desc = description
        self.type = type
        self.hits = hits
        self.exhaust = exhaust
        self.retain = retain
        self.element = element
        self.is_marked = False  # 標記追擊
        self.permanent_dmg_bonus = 0
        self.rect = pygame.Rect(0, 0, 120, 170)
        self.upgraded = False
        self.is_temporary = False

    def upgrade(self):
        if self.upgraded:
            return
        self.upgraded = True
        self.name += "+"
        if self.damage > 0:
            self.damage += 3
            self.base_damage += 3
        if self.block > 0:
            self.block += 3
            self.base_block += 3

        if self.cost >= 2 and random.random() < 0.15:
            self.cost -= 1
            self.original_cost -= 1

        if self.base_name == "雷霆连击":
            self.hits += 1
        elif self.base_name == "時空停滯":
            self.custom_desc = "選擇 1 張手牌變 0 費。保留"
            self.cost = 0
            self.original_cost = 0
        elif self.base_name == "净善摄位":
            self.custom_desc = "進入「摩訶善法大公殿」狀態。草原核傷害提升50%，兩回合內攻擊敵人時生成草原核"
        elif self.base_name == "虛空血脈":
            self.custom_desc = "每當結束回合時，獲得 1 力量"
        elif self.base_name == "無限迴路":
            self.custom_desc = "每打出 3 張牌，隨機抽 1 張技能牌"
        elif self.base_name == "造物主工坊":
            self.custom_desc = "每回合開始獲得 1 張 0 費升級臨時攻擊牌(真0費)"
        elif self.base_name == "因果逆轉":
            self.custom_desc = "受到非物理傷害或負面效果時，敵人獲得3易傷3中毒；受到物理傷害時，反彈一半傷害給敵人 並抵擋四分之一傷"
        elif self.base_name == "潮汐波":
            self.custom_desc = "使目標【潮濕】4回合，抽1张牌"
            self.cost = 1
            self.original_cost = 1
        elif self.base_name == "命運豪賭":
            self.custom_desc = "丟棄自選4張手牌，抽取4张牌"
        elif self.base_name == "灵光一闪":
            self.custom_desc = "從牌組或棄牌堆三選二加入手牌。消耗"

    def draw(self, surface, x, y, is_hovered, is_selected=False, extra_dmg=0, extra_blk=0, angle=0, show_marked=True, has_energy=True):
        # 0. 計算全局縮放比例 (基準高度 720)
        w, h = surface.get_size()
        ui_scale = h / 720.0

        # 1. 創建卡片基礎表面 (基準 165x235)
        base_w, base_h = 165, 235
        card_surf = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
        temp_rect = pygame.Rect(0, 0, base_w, base_h)

        # 稀有度/類型邊框顏色
        # SKILL 中帶 block 為防御型(藍)，無 block 為功能型(青)
        if self.type == "SKILL":
            if self.block > 0:
                type_main = (80, 80, 180)       # 防御藍
                type_bg   = (50, 50, 90)
            else:
                type_main = (80, 160, 160)       # 功能青
                type_bg   = (40, 70, 70)
        elif self.type == "ATTACK":
            type_main = (180, 80, 80)
            type_bg   = (90, 50, 50)
        elif self.type == "POWER":
            type_main = (140, 80, 180)
            type_bg   = (80, 50, 90)
        else:
            type_main = (70, 70, 100)
            type_bg   = (40, 40, 60)

        # 2. 處理外框與背景
        if is_selected:
            pygame.draw.rect(card_surf, GOLD, temp_rect, border_radius=15)

        # 懸停時增加金色外框 (發光感)
        if is_hovered:
            pygame.draw.rect(card_surf, (255, 215, 100), temp_rect, border_radius=15, width=6)

        # 能量不足時紅色邊框提示
        if not has_energy and not is_selected:
            pygame.draw.rect(card_surf, RED, temp_rect, border_radius=15, width=4)

        pygame.draw.rect(card_surf, type_bg, temp_rect, border_radius=12)
        color = (110, 100, 180) if is_selected else ((100, 100, 150) if is_hovered else type_main)
        pygame.draw.rect(card_surf, color, temp_rect.inflate(-8, -8), border_radius=10)

        # 能量不足時整體變暗
        if not has_energy:
            dark_overlay = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
            dark_overlay.fill((0, 0, 0, 100))
            card_surf.blit(dark_overlay, (0, 0))

        # 3. 繪製名稱與費用
        name_color = (120, 120, 120) if not has_energy else WHITE
        name_ts = font_main.render(self.name, True, name_color)
        cost_str = "X" if self.is_x_cost else str(self.cost)
        cost_color = (120, 120, 120) if not has_energy else GOLD
        cost_ts = font_hp.render(cost_str, True, cost_color)
        card_surf.blit(name_ts, (18, 18))
        card_surf.blit(cost_ts, (130, 12))

        # 3.5 繪製元素圖標
        if self.element != "None":
            icon = element_icons.get(self.element)
            if icon:
                card_surf.blit(icon, (15, 42))
            else:
                elem_color = ELEMENT_COLORS.get(self.element, WHITE)
                elem_name_map = {"Pyro": "火", "Hydro": "水", "Cryo": "冰", "Dendro": "草", "Electro": "雷", "Geo": "岩", "Anemo": "風"}
                elem_text = elem_name_map.get(self.element, self.element)
                elem_ts = font_desc.render(elem_text, True, elem_color)
                pygame.draw.circle(card_surf, (20, 20, 40), (28, 55), 13)
                pygame.draw.circle(card_surf, elem_color, (28, 55), 13, width=1)
                card_surf.blit(elem_ts, (21, 46))

        # 3.6 繪製標記追擊 (TARGET) 特效
        if show_marked and self.is_marked:
            pulse = int(40 + 30 * math.sin(pygame.time.get_ticks() / 200))
            glow = (255, 50 + pulse // 2, 50 + pulse // 2)
            pygame.draw.rect(card_surf, glow, temp_rect, width=5, border_radius=12)
            mark_ts = font_desc.render("TARGET 真傷15", True, (255, 255, 255))
            mark_bg = pygame.Surface((mark_ts.get_width() + 10, 20), pygame.SRCALPHA)
            mark_bg.fill((255, 50, 50, 220))
            card_surf.blit(mark_bg, (temp_rect.centerx - mark_bg.get_width() // 2, 98))
            card_surf.blit(mark_ts, (temp_rect.centerx - mark_ts.get_width() // 2, 100))

        # 4. 處理描述文字
        disp_dmg = self.damage + extra_dmg
        disp_blk = self.block + extra_blk

        if self.custom_desc:
            try:
                desc = self.custom_desc.format(dmg=disp_dmg, blk=disp_blk, hits=self.hits)
            except KeyError:
                desc = self.custom_desc
        elif self.hits > 1 and self.base_damage > 0:
            desc = f"造成 {disp_dmg} 傷害 x{self.hits} 次"
        else:
            desc = f"造成 {disp_dmg} 傷害" if (self.base_damage > 0) else f"獲得 {disp_blk} 防禦"

        # 5. 自動換行邏輯
        max_text_width = 140
        current_y = 140
        lines = []
        current_line = ""

        for char in desc:
            test_line = current_line + char
            if font_desc.size(test_line)[0] <= max_text_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)

        # 6. 繪製多行文字
        for line in lines:
            desc_ts = font_desc.render(line, True, (200, 200, 200))
            card_surf.blit(desc_ts, (15, current_y))
            current_y += font_desc.get_linesize() - 2

        # 7. 旋轉與縮放
        # 應用全局 UI 縮放
        final_w = int(base_w * ui_scale)
        final_h = int(base_h * ui_scale)

        # 懸停時放大 1.15 倍
        if is_hovered:
            final_w = int(final_w * 1.15)
            final_h = int(final_h * 1.15)
            # 降低上升高度：從 140 降至 80
            draw_y = y - (80 * ui_scale)
        else:
            draw_y = y

        card_surf = pygame.transform.smoothscale(card_surf, (final_w, final_h))

        final_angle = 0 if is_hovered else angle
        rotated_surf = pygame.transform.rotate(card_surf, final_angle)

        # 更新碰撞矩形
        base_rect = rotated_surf.get_rect(center=(int(x), int(y)))
        self.rect = base_rect

        render_rect = rotated_surf.get_rect(center=(int(x), int(draw_y)))
        surface.blit(rotated_surf, render_rect.topleft)


CARD_DATABASE = {
    "STRIKE": Card("打击", 1, damage=6, element="None"),
    "DEFEND": Card("防御", 1, block=5, type="SKILL", element="None"),
    "PIERCE": Card("西风重击", 1, damage=9, element="None"),
    "IRON_WALL": Card("千岩固牢", 2, block=12, description="獲得 {blk} 防禦。保留。潮濕時【結晶】+12 盾並計入反應", type="SKILL", retain=True, element="Geo"),
    "REWARD_1": Card("天街巡游", 2, damage=16, description="造成 {dmg} 傷害+3回合燃燒。潮濕時【感電】+2易傷並計入反應", element="Electro"),
    "REWARD_2": Card("星尘结界", 1, block=10, description="獲得 {blk} 防禦。保留", type="SKILL", retain=True, element="None"),
    "REWARD_3": Card("元素爆发", 3, damage=25, description="造成 {dmg} 傷害，石化敵人 2 回合", element="Geo"),
    "REWARD_4": Card("荒星防护", 2, block=5, description="獲得 {blk} 防禦，回復 10 生命。保留。潮濕時【結晶】+8 盾並計入反應", type="SKILL", retain=True, element="Geo"),
    "BURST_FLAME": Card("大剑重击", 2, damage=18, description="造成 {dmg} 伤害，敌人晕眩 1 回合", element="None"),
    "STORM_SHIELD": Card("旋风护盾", 1, damage=4, block=6, description="風屬 {dmg} 傷 {blk} 盾。潮濕時【擴散】敵人意圖-15%並計入反應", type="SKILL", element="Anemo"),
    "SACRIFICE": Card("不灭之火", 0, damage=12, description="0费!造成{dmg}爆发伤害。若触发【蒸发】，伤害翻倍", element="Pyro"),
    "SHATTER": Card("碎冰重击", 1, damage=8, description="造成 {dmg} 傷害。若目標【凍結】，消耗狀態並造成 3 倍傷害", element="Cryo"),
    "DAWN": Card("黎明·斩击", 0, damage=7, description="消耗所有能量。造成 {dmg} 傷害 X 次。若觸發【蒸發】，傷害翻倍", is_x_cost=True, element="Pyro"),
    "MAYA": Card("净善摄位", 1, description="進入「摩訶善法大公殿」狀態。草原核傷害提升50%，本回合攻擊敵人時生成草原核", type="POWER", element="Dendro"),
    "FROST_NOVA": Card("冰霜新星", 1, damage=5, description="造成 {dmg} 傷害。使目標【凍結】（跳過下回合攻擊）", element="Cryo"),
    "HYDRO_BLADE": Card("水刃", 1, damage=6, description="造成 {dmg} 傷害，使目標【潮濕】 2 回合", element="Hydro"),
    "RAIN_GUARD": Card("雨神之护", 1, block=10, description="獲得 {blk} 防禦，使目標【潮濕】 3 回合", type="SKILL", element="Hydro"),
    "TIDAL_WAVE": Card("潮汐波", 2, description="使目標【潮濕】 4 回合，抽 1 張牌", type="SKILL", element="Hydro"),

    # ⚔️ 攻擊牌
    "HEAVEN_FLAME": Card("天基烈焰", 3, damage=32, description="造成 {dmg} 傷害。若目標【易傷】或觸發【蒸發】，傷害翻倍", element="Pyro"),
    "THUNDER_COMBO": Card(
        "雷霆连击", 1, damage=6, hits=3, type="ATTACK", element="Electro",
        description="雷屬攻擊，造成 {dmg} 傷害共 3 次。首擊若目標【潮濕】觸發【感電】(+2易傷)。第3擊短暫眩。抽到時本場永久+1",
    ),
    "REAPER": Card("死神收割", 2, damage=14, description="全體 {dmg} 傷害。回復造成傷害 50% 的生命。消耗", exhaust=True, element="None"),

    # 🛡️ 技能牌
    "DIVINE_BARRIER": Card("神圣屏障", 2, block=20, description="獲得 {blk} 護甲。下回合能量 +1。保留", type="SKILL", retain=True, element="None"),
    "TIME_STASIS": Card("時空停滯", 1, description="選擇 1 張手牌本回合變 0 費。保留", type="SKILL", retain=True, element="None"),
    "FATE_GAMBLE": Card("命運豪賭", 0, description="丟棄所有手牌，抽取 4 張牌", type="SKILL", element="None"),

    # 🔮 能力牌
    "VOID_BLOOD": Card("虛空血脈", 1, description="每當失去生命時，獲得 2 力量", type="POWER", element="None"),
    "INFINITE_LOOP": Card("無限迴路", 2, description="每打出 3 張攻擊牌，隨機抽 1 張技能牌", type="POWER", element="None"),
    "CREATOR_WORKSHOP": Card("造物主工坊", 3, description="每回合開始獲得 1 張 1 費升級臨時攻擊牌", type="POWER", element="None"),
    "KARMA_REVERSE": Card("因果逆轉", 2, description="受到非物理傷害或負面效果時，敵人獲得3易傷3中毒；受到物理傷害時，反彈一半傷害給敵人", type="POWER", element="None"),
    "VOID": Card("虚空", 0, description="虛無。打出後消失", type="SKILL", exhaust=True, element="None"),
    "DISCOVERY": Card("灵光一闪", 1, description="從牌組或棄牌堆三選一加入手牌。消耗", type="SKILL", exhaust=True, element="None"),
}

# 卡牌中文名 -> CARD_DATABASE 鍵（用於能力牌到期歸還牌庫等）
CARD_NAME_TO_KEY = {
    "打击": "STRIKE", "防御": "DEFEND", "西风重击": "PIERCE", "千岩固牢": "IRON_WALL",
    "天街巡游": "REWARD_1", "星尘结界": "REWARD_2", "元素爆发": "REWARD_3",
    "荒星防护": "REWARD_4", "大剑重击": "BURST_FLAME", "旋风护盾": "STORM_SHIELD",
    "雨神之护": "RAIN_GUARD", "潮汐波": "TIDAL_WAVE",
    "不灭之火": "SACRIFICE", "碎冰重击": "SHATTER", "黎明·斩击": "DAWN",
    "净善摄位": "MAYA", "冰霜新星": "FROST_NOVA", "水刃": "HYDRO_BLADE",
    "天基烈焰": "HEAVEN_FLAME", "雷霆连击": "THUNDER_COMBO", "死神收割": "REAPER",
    "神圣屏障": "DIVINE_BARRIER", "時空停滯": "TIME_STASIS", "命運豪賭": "FATE_GAMBLE",
    "虛空血脈": "VOID_BLOOD", "無限迴路": "INFINITE_LOOP",
    "造物主工坊": "CREATOR_WORKSHOP", "因果逆轉": "KARMA_REVERSE",
    "灵光一闪": "DISCOVERY", "虚空": "VOID",
}

RELIC_DATABASE = {
    "BlizzardStrayer": {"id": "BlizzardStrayer", "name": "冰風迷途的留戀", "color": (100, 200, 255), "desc": "回合開始能量 +1"},
    "CrimsonWitch": {"id": "CrimsonWitch", "name": "熾烈的炎之魔女", "color": (255, 100, 50), "desc": "火元素傷害 +3，且蒸發不消耗潮濕"},
    "DeepwoodMemories": {"id": "DeepwoodMemories", "name": "深林的記憶", "color": (100, 255, 100), "desc": "草原核基礎傷害提升 10"},
    "Catalyst": {"id": "Catalyst", "name": "草原的催化者", "color": (50, 200, 100), "desc": "攻擊潮濕敵人時生成草原核"}
}
