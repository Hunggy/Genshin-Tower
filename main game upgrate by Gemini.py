import pygame
import random
import sys
import copy
import os
import math


def get_base_path():
    # 支援 PyInstaller 打包路徑
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# --- 1. 初始化與基礎配置 ---
pygame.init()
pygame.mixer.init()  # 確保音效模組提早初始化
SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Project: Genshin Spire")

# --- 背景圖與粒子效果 ---
class Particle:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = random.randint(0, SCREEN_W)
        self.y = random.randint(0, SCREEN_H)
        self.size = random.randint(1, 3)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.alpha = random.randint(50, 150)
        self.color = (200 + random.randint(0, 55), 200 + random.randint(0, 55), 255)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x < 0 or self.x > SCREEN_W or self.y < 0 or self.y > SCREEN_H:
            self.reset()

# 加载背景图（支持多种格式）
def load_background(name):
    for ext in [".png", ".jpg", ".jpeg"]:
        bg_path = os.path.join(get_base_path(), "images", name + ext)
        if os.path.exists(bg_path):
            try:
                bg = pygame.image.load(bg_path)
                return pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
            except:
                continue
    return None

# 创建粒子
particles = [Particle() for _ in range(50)]

# 加载多种背景图
background_menu = load_background("background_menu")
background_battle = load_background("background_battle")
background_victory = load_background("background_victory")

# 加载卡比图片
def load_kirby():
    for ext in [".png", ".jpg", ".jpeg"]:
        kirby_path = os.path.join(get_base_path(), "images", "kirby" + ext)
        if os.path.exists(kirby_path):
            try:
                img = pygame.image.load(kirby_path).convert_alpha()
                return pygame.transform.scale(img, (60, 60))
            except:
                continue
    return None

kirby_image = load_kirby()

# 加載能量圖片
def load_energy_image():
    base = get_base_path()
    # 同時搜尋當前與上級目錄的 images/Energy, images/Energry (容錯)
    energy_dirs = [
        os.path.join(base, "images", "Energy"),
        os.path.join(base, "images", "Energry"),
        os.path.join(os.path.dirname(base), "images", "Energy"),
        os.path.join(os.path.dirname(base), "images", "Energry")
    ]
    
    for d in energy_dirs:
        if os.path.exists(d):
            # 取得資料夾內第一張圖片
            files = [f for f in os.listdir(d) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            if files:
                path = os.path.join(d, files[0])
                try:
                    # 如果是 .png 則直接載入
                    if path.lower().endswith(".png"):
                        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (80, 80))
                    
                    # 如果是 .jpg 則進行去底色處理
                    img = pygame.image.load(path).convert() 
                    colorkey = img.get_at((0,0))
                    img.set_colorkey(colorkey)
                    return pygame.transform.scale(img.convert_alpha(), (80, 80))
                except Exception as e:
                    print(f"無法從 {path} 加載能量圖片: {e}")
    return None

energy_image = load_energy_image()

def load_shield_image():
    for ext in [".png", ".jpg", ".jpeg"]:
        shield_path = os.path.join(get_base_path(), "images", "shield" + ext)
        if os.path.exists(shield_path):
            try:
                return pygame.image.load(shield_path).convert_alpha()
            except:
                continue
    return None

shield_image = load_shield_image()

def load_enemy_image(enemy_name):
    base = get_base_path()
    enemy_dir = os.path.join(base, "images", "enemies")
    
    # 1. 生成可能的名稱變體
    possible_names = [enemy_name]
    
    # 替換空格為下劃線
    possible_names.append(enemy_name.replace(" ", "_"))
    # 去掉所有空格
    possible_names.append(enemy_name.replace(" ", ""))
    
    # 處理括號
    if "(" in enemy_name:
        name_no_paren = enemy_name[:enemy_name.index("(")].strip()
        possible_names.append(name_no_paren)
        possible_names.append(name_no_paren.replace(" ", "_"))
    
    # 2. 嘗試精確匹配
    for ext in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]:
        for name in possible_names:
            for d in [enemy_dir, os.path.join(base, "images")]:
                path = os.path.join(d, name + ext)
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        return scale_enemy(img)
                    except: pass

    # 3. 模糊匹配：遍歷目錄尋找最相似的文件
    try:
        if os.path.exists(enemy_dir):
            files = os.listdir(enemy_dir)
            # 簡化搜索詞：去掉所有非中文字符和字母數字以外的內容
            search_key = "".join(filter(str.isalnum, enemy_name)).lower()
            
            for f in files:
                file_key = "".join(filter(str.isalnum, os.path.splitext(f)[0])).lower()
                # 如果搜索詞包含在文件名中，或者文件名包含在搜索詞中
                if search_key in file_key or file_key in search_key:
                    path = os.path.join(enemy_dir, f)
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        return scale_enemy(img)
                    except: continue
    except: pass
    
    return None

def scale_enemy(img):
    w, h = img.get_size()
    ratio = min(120 / w, 120 / h)
    new_w, new_h = int(w * ratio), int(h * ratio)
    return pygame.transform.smoothscale(img, (new_w, new_h))

# 加載主角圖片
def load_all_characters():
    chars = {} # 格式: {"Name": [frame1, frame2, ...]}
    base = get_base_path()
    
    # 同時搜尋多個可能的目錄，防止路徑嵌套導致找不到圖片
    search_dirs = [
        os.path.join(base, "images"),
        os.path.join(os.path.dirname(base), "images"),
        os.path.join(base, "model"),
        os.path.join(base, "Genshin Tower", "model")
    ]
    
    print(f"--- 開始掃描角色圖片 ---")
    
    for d in search_dirs:
        if not os.path.exists(d): 
            continue
        
        print(f"正在搜尋目錄: {os.path.abspath(d)}")
        # 排除 Energy 資料夾，不將其作為角色模型載入
        for item in os.listdir(d):
            if item.lower() in ["energy", "engry", "energry", "enemies"]:
                continue
                
            full_path = os.path.join(d, item)
            
            # 情況 A: 資料夾 (序列幀動畫)
            if os.path.isdir(full_path):
                frames = []
                img_files = sorted([f for f in os.listdir(full_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
                for f in img_files:
                    try:
                        img = pygame.image.load(os.path.join(full_path, f)).convert_alpha()
                        frames.append(pygame.transform.scale(img, (120, 120)))
                    except: continue
                
                if frames:
                    chars[item] = frames
                    print(f"  [動畫] 載入序列: {item} (共 {len(frames)} 幀)")
            
            # 情況 B: 單張圖片
            elif item.lower().endswith((".png", ".jpg", ".jpeg")):
                name = os.path.splitext(item)[0]
                # 跳過背景圖
                if "background" in name.lower(): continue
                try:
                    img = pygame.image.load(full_path).convert_alpha()
                    chars[name] = [pygame.transform.scale(img, (120, 120))]
                    print(f"  [靜態] 載入角色: {name}")
                except: continue
    
    if not chars:
        print("  警告: 未找到任何角色圖片，使用默認圖形")
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 150, 180), (60, 60), 55)
        chars["Default"] = [surf]
    
    print(f"掃描完成，共載入 {len(chars)} 個角色")
    print(f"------------------------")
    return chars

character_images = load_all_characters()

# 加載元素圖標
def load_element_icons():
    icons = {}
    base = get_base_path()
    # 預期路徑為 images/elements/
    elements_dir = os.path.join(base, "images", "elements")
    
    if os.path.exists(elements_dir):
        for f in os.listdir(elements_dir):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                name = os.path.splitext(f)[0].capitalize() # 確保與 Pyro, Hydro 等對齊
                try:
                    img = pygame.image.load(os.path.join(elements_dir, f)).convert_alpha()
                    icons[name] = pygame.transform.smoothscale(img, (26, 26))
                except:
                    continue
    return icons

element_icons = load_element_icons()

# 字體加載（統一使用支援中文的系統字體，避免彈出文字顯示為空白）
UI_FONT_FAMILIES = [
    "Microsoft YaHei", "Microsoft YaHei UI", "SimHei", "SimSun",
    "PingFang SC", "Noto Sans CJK SC", "Arial Unicode MS", "Arial",
]
_ui_font_cache = {}


def get_ui_font(size, bold=False):
    key = (size, bold)
    if key not in _ui_font_cache:
        _ui_font_cache[key] = pygame.font.SysFont(UI_FONT_FAMILIES, size, bold=bold)
    return _ui_font_cache[key]


font_main = get_ui_font(20)
font_desc = get_ui_font(14)
font_hp = get_ui_font(22, bold=True)
font_big = get_ui_font(60)

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GOLD = (255, 215, 0)
GREEN = (50, 200, 50)
RED = (220, 50, 50)
BLUE = (50, 150, 255)
ORANGE = (255, 165, 0)

ELEMENT_COLORS = {
    "Pyro": (255, 100, 50),
    "Hydro": (50, 150, 255),
    "Cryo": (150, 240, 255),
    "Dendro": (100, 255, 100),
    "Electro": (200, 100, 255),
    "Geo": (255, 215, 0),
    "Anemo": (120, 230, 200),
    "None": (200, 200, 200)
}

# 元素護盾克制關係：盾類型 -> 克制它的玩家元素
ELEMENT_COUNTERS = {
    "Pyro": ["Hydro", "Electro"], # 火盾怕水、雷
    "Hydro": ["Cryo", "Dendro"], # 水盾怕冰、草
    "Cryo": ["Pyro", "Electro"], # 冰盾怕火、雷
    "Electro": ["Dendro", "Cryo"], # 雷盾怕草、冰
    "Geo": ["Geo", "None"],      # 岩盾怕岩、重擊(物理)
    "None": []
}


class Animation:
    def __init__(self):
        self.active = False

    def update(self, dt): pass

    def draw(self, surface): pass


class FloatText(Animation):
    def __init__(self, x, y, text, color, size=28, duration=2.4):
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.alpha = 255
        self.active = True
        self.timer = 0
        self.duration = duration
        self.velocity = -42

    def update(self, dt):
        if not self.active: return
        self.timer += dt
        self.y += self.velocity * dt
        fade_start = self.duration * 0.55
        if self.timer < fade_start:
            self.alpha = 255
        else:
            fade_t = (self.timer - fade_start) / max(0.01, self.duration - fade_start)
            self.alpha = max(0, 255 - int(fade_t * 255))
        if self.timer >= self.duration:
            self.active = False

    def draw(self, surface):
        if not self.active or self.alpha <= 0: return
        font = get_ui_font(self.size, bold=True)
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
        if not self.active: return
        self.timer += dt
        self.progress = min(1.0, self.timer / self.duration)
        t = self.progress
        ease = 1 - (1 - t) * (1 - t)
        self.x = self.start_x + (self.end_x - self.start_x) * ease
        self.y = self.start_y + (self.end_y - self.start_y) * ease
        if self.progress >= 1.0:
            self.active = False
            if self.callback: self.callback()

    def draw(self, surface):
        if not self.active: return
        self.card.draw(surface, int(self.x), int(self.y), False)


class FlashScreen(Animation):
    def __init__(self, color=(255, 0, 0), duration=0.2):
        super().__init__()
        self.color = color
        self.duration = duration
        self.timer = 0
        self.active = True

    def update(self, dt):
        if not self.active: return
        self.timer += dt
        if self.timer >= self.duration: self.active = False

    def draw(self, surface):
        if not self.active: return
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
        if not self.active: return
        self.timer += dt
        if self.timer < self.duration:
            self.offset_x = math.sin(self.timer * 50) * self.intensity * (1 - self.timer / self.duration)
            self.offset_y = math.cos(self.timer * 50) * self.intensity * (1 - self.timer / self.duration)
        else:
            self.active = False
            self.offset_x = 0
            self.offset_y = 0

    def draw(self, surface):
        pass


class AnimationManager:
    FLOAT_LANE_LEFT = 250
    FLOAT_LANE_RIGHT = SCREEN_W - 400
    FLOAT_STACK_STEP = 34

    def __init__(self):
        self.animations = []
        self.screen_shake = None

    def add(self, anim):
        self.animations.append(anim)

    def _float_lane_x(self, x):
        return self.FLOAT_LANE_LEFT if x < SCREEN_W * 0.5 else self.FLOAT_LANE_RIGHT

    def _count_active_floats_in_lane(self, lane_x):
        return sum(
            1 for a in self.animations
            if isinstance(a, FloatText) and a.active and abs(a.x - lane_x) < 100
        )

    def add_float_text(self, x, y, text, color, size=26, duration=2.4):
        lane_x = self._float_lane_x(x)
        slot = self._count_active_floats_in_lane(lane_x)
        base_y = SCREEN_H * (0.34 if lane_x == self.FLOAT_LANE_LEFT else 0.30)
        stacked_y = base_y - slot * self.FLOAT_STACK_STEP
        self.add(FloatText(lane_x, stacked_y, text, color, size=size, duration=duration))

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
        self.is_marked = False # 標記追擊
        self.permanent_dmg_bonus = 0 
        self.rect = pygame.Rect(0, 0, 120, 170)
        self.upgraded = False
        self.is_temporary = False

    def upgrade(self):
        if self.upgraded: return
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

    def draw(self, surface, x, y, is_hovered, is_selected=False, extra_dmg=0, extra_blk=0, angle=0, show_marked=True):
        # 0. 計算全局縮放比例 (基準高度 720)
        w, h = surface.get_size()
        ui_scale = h / 720.0
        
        # 1. 創建卡片基礎表面 (基準 165x235)
        base_w, base_h = 165, 235
        card_surf = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
        temp_rect = pygame.Rect(0, 0, base_w, base_h)

        # 2. 處理外框與背景
        if is_selected:
            pygame.draw.rect(card_surf, GOLD, temp_rect, border_radius=15)
        
        # 懸停時增加金色外框 (發光感)
        if is_hovered:
            pygame.draw.rect(card_surf, (255, 215, 100), temp_rect, border_radius=15, width=6)

        pygame.draw.rect(card_surf, (40, 40, 60), temp_rect, border_radius=12)
        color = (110, 100, 180) if is_selected else ((100, 100, 150) if is_hovered else (70, 70, 100))
        pygame.draw.rect(card_surf, color, temp_rect.inflate(-8, -8), border_radius=10)

        # 3. 繪製名稱與費用
        name_ts = font_main.render(self.name, True, WHITE)
        cost_str = "X" if self.is_x_cost else str(self.cost)
        cost_ts = font_hp.render(cost_str, True, GOLD)
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
        description="雷屬攻擊，造成 {dmg} 傷害共 3 次。首擊若目標【潮濕】觸發【感電】(+2易傷)。第3擊短暈眩。抽到時本場永久+1",
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
    "VOID": Card("虛空", 0, description="虛無。打出後消失", type="SKILL", exhaust=True, element="None"),
    "DISCOVERY": Card("灵光一闪", 1, description="從牌組或棄牌堆三選一加入手牌。消耗", type="SKILL", exhaust=True, element="None"),
}

# 卡牌中文名 -> CARD_DATABASE 鍵（用於能力牌到期歸還牌庫等）
CARD_NAME_TO_KEY = {
    "天街巡游": "REWARD_1", "星尘结界": "REWARD_2", "元素爆发": "REWARD_3",
    "荒星防护": "REWARD_4", "大剑重击": "BURST_FLAME", "旋风护盾": "STORM_SHIELD",
    "雨神之护": "RAIN_GUARD", "潮汐波": "TIDAL_WAVE",
    "不灭之火": "SACRIFICE", "碎冰重击": "SHATTER", "黎明·斩击": "DAWN",
    "净善摄位": "MAYA", "冰霜新星": "FROST_NOVA",
    "天基烈焰": "HEAVEN_FLAME", "雷霆连击": "THUNDER_COMBO", "死神收割": "REAPER",
    "神圣屏障": "DIVINE_BARRIER", "時空停滯": "TIME_STASIS", "命運豪賭": "FATE_GAMBLE",
    "虛空血脈": "VOID_BLOOD", "無限迴路": "INFINITE_LOOP",
    "造物主工坊": "CREATOR_WORKSHOP", "因果逆轉": "KARMA_REVERSE",
    "灵光一闪": "DISCOVERY",
}

RELIC_DATABASE = {
    "BlizzardStrayer": {"id": "BlizzardStrayer", "name": "冰風迷途的留戀", "color": (100, 200, 255), "desc": "回合開始能量 +1"},
    "CrimsonWitch": {"id": "CrimsonWitch", "name": "熾烈的炎之魔女", "color": (255, 100, 50), "desc": "火元素傷害 +3，且蒸發不消耗潮濕"},
    "DeepwoodMemories": {"id": "DeepwoodMemories", "name": "深林的記憶", "color": (100, 255, 100), "desc": "草原核基礎傷害提升 10"},
    "Catalyst": {"id": "Catalyst", "name": "草原的催化者", "color": (50, 200, 100), "desc": "攻擊潮濕敵人時生成草原核"}
}

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
        
        # 敵人基礎數值
        self.enemy_max_hp = 80
        self.enemy_hp = 80
        self.enemy_min_dmg = 7
        self.enemy_max_dmg = 12
        self.enemy_intent = 0
        self.enemy_name = "基礎雜兵"
        self.enemy_image = load_enemy_image(self.enemy_name)
        self.stage_type = "NORMAL"
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
        
        self.pending_relic = None
        self.pending_upgrade = False
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
            if len(self.hand) >= self.max_hand: break
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
            if actual_dmg > 0:
                self.anim_queue.append(("damage_player", actual_dmg, 200, SCREEN_H - 350))
                # 只有未升级的虚空血脉才在受伤时获得力量
                if "虛空血脈" in self.powers and "虛空血脈+" not in self.powers:
                    self.strength += 2
                    self.anim_queue.append(("status_enemy", "力量提升!", 250, SCREEN_H - 350))
        else:
            if status_msg:
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


# --- 特殊機制圖鑑 ---
MECHANICS_GUIDE_ENTRIES = [
    ("1. 標記追擊", "每回合開始隨機標記一張手牌（TARGET 紅標）。本回合打出該牌時，額外造成 15 點真實傷害（無視護盾）。"),
    ("2. 反應超載", "單回合內觸發 3 次及以上元素反應（蒸發、凍結、感電、結晶、擴散、碎冰、草原核等）。結束回合後，敵人下回合強制暈眩。"),
    ("3. 能量浪費", "結束回合時若仍有剩餘能量，敵人吸收能量：每剩 1 點，敵人意圖傷害永久 +2。"),
    ("4. 節奏大師", "僅部分精英/BOSS 擁有（波次 10/15/20/25/30）。每 2 回合切換：進攻姿態意圖 +50%；防禦姿態每回合回復 10 HP。切換前 1 回合有金色預告。"),
    ("5. 大招打斷", "BOSS 蓄力期間，若本回合使敵人凍結、石化或暈眩，蓄力進度重置為 1。"),
    ("6. 元素震懾", "用克制元素攻擊元素盾時，一次削 3 層盾，且敵人下次攻擊意圖傷害降低 15%。"),
    ("7. 連擊壓制", "單回合打出 ≥5 張牌，敵人該次攻擊傷害降低 30%。"),
    ("8. 元素護盾", "部分敵人帶元素盾層數；克制元素破盾更快，破盾後敵人暈眩 1 回合。"),
    ("9. 大招蓄力", "BOSS 蓄力滿後釋放高倍率攻擊；留意頭頂蓄力計數並用控制打斷。"),
    ("10. 元素反應系統", "本遊戲包含以下元素反應：\n\n【潮濕】水元素附著，使敵人進入潮濕狀態。可觸發多種元素反應。水刃、雨神之护、潮汐波可使敵人潮濕。\n\n【蒸發】火+潮濕。傷害翻倍。若裝備「熾烈的炎之魔女」，蒸發不消耗潮濕。不灭之火、黎明·斩击、天基烈焰可觸發。\n\n【感電】雷+潮濕。敵人獲得 2 層易傷（受到傷害+50%），不消耗潮濕。天街巡游、雷霆连击可觸發。\n\n【凍結】冰+水。敵人跳過下回合攻擊。冰霜新星可使敵人凍結。\n\n【碎冰】冰攻擊凍結的敵人。傷害變為 3 倍。碎冰重击可觸發。\n\n【結晶】岩+潮濕。玩家獲得護甲盾。千岩固牢、荒星防护可觸發。\n\n【擴散】風+潮濕。敵人當前意圖傷害降低 15%。旋风护盾可觸發。\n\n【草原核】攻擊潮濕敵人時生成草原核。回合開始時草原核爆炸，造成 8×數量 傷害（基礎）。裝備「深林的記憶」草原核傷害+10；裝備「草原的催化者」攻擊潮濕敵人時生成草原核；裝備「净善摄位」攻擊潮濕敵人時本回合生成草原核且草原核傷害+50%。"),
]


def wrap_text_lines(text, font, max_width):
    lines = []
    current = ""
    for char in text:
        if char == "\n":
            if current:
                lines.append(current)
            lines.append("")
            current = ""
            continue
        test = current + char
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def draw_mechanics_guide_overlay(surface, game, mx, my):
    w, h = surface.get_size()
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 215))
    surface.blit(dim, (0, 0))

    panel = pygame.Rect(int(w * 0.06), int(h * 0.05), int(w * 0.88), int(h * 0.9))
    pygame.draw.rect(surface, (32, 34, 52), panel, border_radius=14)
    pygame.draw.rect(surface, GOLD, panel, width=2, border_radius=14)

    title_ts = font_big.render("特殊機制圖鑑", True, GOLD)
    surface.blit(title_ts, (panel.x + 24, panel.y + 16))

    close_rect = pygame.Rect(panel.right - 108, panel.y + 14, 88, 34)
    close_hover = close_rect.collidepoint((mx, my))
    pygame.draw.rect(surface, (140, 60, 60) if close_hover else (100, 45, 45), close_rect, border_radius=6)
    close_ts = font_main.render("關閉", True, WHITE)
    surface.blit(close_ts, close_ts.get_rect(center=close_rect.center))

    hint_ts = font_desc.render("滾輪捲動 · ESC 關閉", True, (160, 160, 180))
    surface.blit(hint_ts, (panel.x + 24, panel.bottom - 28))

    content_rect = pygame.Rect(panel.x + 20, panel.y + 58, panel.width - 40, panel.height - 96)
    surface.set_clip(content_rect)

    text_width = content_rect.width - 8
    line_h = font_desc.get_linesize()
    y = content_rect.y - game.mechanics_scroll

    for title, body in MECHANICS_GUIDE_ENTRIES:
        title_ts = font_hp.render(title, True, (255, 220, 120))
        surface.blit(title_ts, (content_rect.x, y))
        y += line_h + 20 # 增加標題與文本之間的垂直距離 (再加大)
        for line in wrap_text_lines(body, font_desc, text_width):
            line_ts = font_desc.render(line, True, (210, 210, 220))
            surface.blit(line_ts, (content_rect.x + 8, y))
            y += line_h
        y += 40 # 增加不同機制條目之間的間距 (再加大)

    surface.set_clip(None)
    content_height = y + game.mechanics_scroll - content_rect.y
    max_scroll = max(0, content_height - content_rect.height)
    game.mechanics_scroll = max(0, min(game.mechanics_scroll, max_scroll))

    return close_rect


# --- 3. 繪製組件 ---
def draw_main_menu_surface(surface, game, mx, my):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
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
    
    # 在右上角繪製查看牌組按鈕
    deck_btn_w, deck_btn_h = 150 * ui_scale, 36 * ui_scale
    deck_btn_rect = pygame.Rect(w - deck_btn_w - 15 * ui_scale, 10 * ui_scale, deck_btn_w, deck_btn_h)
    is_deck_hover = deck_btn_rect.collidepoint((mx, my))
    deck_btn_color = (40, 60, 100) if is_deck_hover else (30, 45, 80)
    pygame.draw.rect(surface, deck_btn_color, deck_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD, deck_btn_rect, width=1, border_radius=int(8 * ui_scale))
    total_cards = len(game.deck) + len(game.hand) + len(game.discard)
    deck_ts = font_main.render(f"查看牌組 ({total_cards})", True, WHITE)
    surface.blit(deck_ts, deck_ts.get_rect(center=deck_btn_rect.center))
    menu_rects["DECK"] = deck_btn_rect

    # 在查看牌組左邊繪製機制圖按鈕
    guide_btn_w, guide_btn_h = 120 * ui_scale, 36 * ui_scale
    guide_btn_rect = pygame.Rect(deck_btn_rect.left - guide_btn_w - 10 * ui_scale, 10 * ui_scale, guide_btn_w, guide_btn_h)
    is_guide_hover = guide_btn_rect.collidepoint((mx, my))
    guide_btn_color = (60, 100, 60) if is_guide_hover else (40, 70, 40)
    pygame.draw.rect(surface, guide_btn_color, guide_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD if is_guide_hover else (140, 140, 160), guide_btn_rect, width=2, border_radius=int(8 * ui_scale))
    guide_ts = font_main.render("機制圖鑑", True, WHITE)
    surface.blit(guide_ts, guide_ts.get_rect(center=guide_btn_rect.center))
    menu_rects["GUIDE"] = guide_btn_rect

    return menu_rects


def draw_settings_surface(surface, game, mx, my, mouse_pressed):
    w, h = surface.get_size()
    title_ts = font_big.render("遊戲設置", True, WHITE)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.1)))

    # --- 1. 音量設定區塊 ---
    vol_label = font_hp.render(f"音樂音量: {int(game.volume * 100)}%", True, (200, 200, 200))
    surface.blit(vol_label, (w // 2 - 250, h * 0.22))

    track_rect = pygame.Rect(w // 2 - 80, int(h * 0.23), 250, 10)
    click_area = track_rect.inflate(0, 30)

    if mouse_pressed and click_area.collidepoint((mx, my)):
        relative_x = mx - track_rect.x
        game.volume = max(0.0, min(1.0, relative_x / track_rect.width))
        pygame.mixer.music.set_volume(game.volume)

    pygame.draw.rect(surface, (100, 100, 100), track_rect, border_radius=5)
    fill_width = int(track_rect.width * game.volume)
    fill_rect = pygame.Rect(track_rect.x, track_rect.y, fill_width, track_rect.height)
    pygame.draw.rect(surface, GOLD, fill_rect, border_radius=5)

    knob_x = track_rect.x + fill_width
    knob_y = track_rect.centery
    knob_radius = 12 if click_area.collidepoint((mx, my)) else 10
    knob_color = WHITE if not mouse_pressed else (200, 200, 200)
    pygame.draw.circle(surface, knob_color, (knob_x, knob_y), knob_radius)

    # --- 2. 解析度設定區塊 ---
    label_ts = font_hp.render("調整解析度：", True, (200, 200, 200))
    surface.blit(label_ts, (w // 2 - 250, h * 0.32))

    res_options = [
        {"id": "RES_1280", "text": "1280 x 720", "w": 1280, "h": 720},
        {"id": "RES_1600", "text": "1600 x 900", "w": 1600, "h": 900}
    ]
    setting_rects = {}
    for i, opt in enumerate(res_options):
        rect = pygame.Rect(w // 2 - 80 + i * 140, h * 0.30, 120, 45)
        setting_rects[opt["id"]] = (rect, opt["w"], opt["h"])
        is_current = (w == opt["w"])
        is_hover = rect.collidepoint((mx, my))
        color = (50, 150, 50) if is_current else ((100, 100, 120) if is_hover else (50, 50, 60))
        pygame.draw.rect(surface, color, rect, border_radius=5)
        if is_hover or is_current: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=5)
        txt = font_main.render(opt["text"], True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    # --- 3. 全螢幕切換 ---
    fs_label_ts = font_hp.render("顯示模式：", True, (200, 200, 200))
    surface.blit(fs_label_ts, (w // 2 - 250, h * 0.42))
    
    fs_options = [
        {"id": "FS_OFF", "text": "視窗模式", "val": False},
        {"id": "FS_ON", "text": "全螢幕", "val": True}
    ]
    for i, opt in enumerate(fs_options):
        rect = pygame.Rect(w // 2 - 80 + i * 140, h * 0.40, 120, 45)
        setting_rects[opt["id"]] = (rect, opt["val"], 0)
        is_current = (game.fullscreen == opt["val"])
        is_hover = rect.collidepoint((mx, my))
        color = (50, 150, 50) if is_current else ((100, 100, 120) if is_hover else (50, 50, 60))
        pygame.draw.rect(surface, color, rect, border_radius=5)
        if is_hover or is_current: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=5)
        txt = font_main.render(opt["text"], True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    # --- 4. 閃光效果切換 ---
    flash_label_ts = font_hp.render("特效閃爍：", True, (200, 200, 200))
    surface.blit(flash_label_ts, (w // 2 - 250, h * 0.52))
    
    flash_options = [
        {"id": "FLASH_ON", "text": "開啟特效", "val": True},
        {"id": "FLASH_OFF", "text": "關閉特效", "val": False}
    ]
    for i, opt in enumerate(flash_options):
        rect = pygame.Rect(w // 2 - 80 + i * 140, h * 0.50, 120, 45)
        setting_rects[opt["id"]] = (rect, opt["val"], 0)
        is_current = (game.flash_enabled == opt["val"])
        is_hover = rect.collidepoint((mx, my))
        color = (50, 150, 50) if is_current else ((100, 100, 120) if is_hover else (50, 50, 60))
        pygame.draw.rect(surface, color, rect, border_radius=5)
        if is_hover or is_current: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=5)
        txt = font_main.render(opt["text"], True, WHITE)
        surface.blit(txt, txt.get_rect(center=rect.center))

    # --- 5. 主角選擇區塊 ---
    char_label_ts = font_hp.render("更換主角：", True, (200, 200, 200))
    surface.blit(char_label_ts, (w // 2 - 250, h * 0.65))
    
    char_names = list(character_images.keys())
    for i, char_name in enumerate(char_names):
        row = i // 3
        col = i % 3
        rect = pygame.Rect(w // 2 - 80 + col * 140, h * 0.63 + row * 65, 120, 60) # 稍微調高高度
        setting_rects[f"CHAR_{char_name}"] = (rect, char_name, 0)
        is_current = (game.current_character == char_name)
        is_hover = rect.collidepoint((mx, my))
        color = (50, 150, 50) if is_current else ((100, 100, 120) if is_hover else (50, 50, 60))
        pygame.draw.rect(surface, color, rect, border_radius=5)
        if is_hover or is_current: pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=5)
        
        # 繪製角色小圖
        frames = character_images.get(char_name)
        if frames and len(frames) > 0:
            small_img = pygame.transform.scale(frames[0], (30, 30))
            surface.blit(small_img, (rect.x + 5, rect.y + 15))
            
        display_name = char_name[:8] + ".." if len(char_name) > 8 else char_name
        txt = font_desc.render(display_name, True, WHITE)
        surface.blit(txt, (rect.x + 40, rect.y + 22))

    # --- 返回/退出按鈕 ---
    if game.previous_battle_state == "BATTLE":
        # 局內設置：顯示「返回戰鬥」和「退出對局」
        back_rect = pygame.Rect(w // 2 - 220, h * 0.85, 180, 50)
        quit_rect = pygame.Rect(w // 2 + 40, h * 0.85, 180, 50)
        setting_rects["BACK"] = (back_rect, 0, 0)
        setting_rects["QUIT_BATTLE"] = (quit_rect, 0, 0)

        is_back_hover = back_rect.collidepoint((mx, my))
        pygame.draw.rect(surface, (50, 150, 50) if is_back_hover else (40, 100, 40), back_rect, border_radius=8)
        back_ts = font_main.render("返回戰鬥", True, WHITE)
        surface.blit(back_ts, back_ts.get_rect(center=back_rect.center))

        is_quit_hover = quit_rect.collidepoint((mx, my))
        pygame.draw.rect(surface, (150, 50, 50) if is_quit_hover else (100, 40, 40), quit_rect, border_radius=8)
        quit_ts = font_main.render("退出對局", True, WHITE)
        surface.blit(quit_ts, quit_ts.get_rect(center=quit_rect.center))
    else:
        # 主菜單設置：顯示「返回主選單」
        back_rect = pygame.Rect(w // 2 - 100, h * 0.85, 200, 50)
        setting_rects["BACK"] = (back_rect, 0, 0)
        is_back_hover = back_rect.collidepoint((mx, my))
        pygame.draw.rect(surface, (150, 50, 50) if is_back_hover else (100, 40, 40), back_rect, border_radius=8)
        back_ts = font_main.render("返回主選單", True, WHITE)
        surface.blit(back_ts, back_ts.get_rect(center=back_rect.center))

    return setting_rects


def draw_mode_select_surface(surface, mx, my):
    w, h = surface.get_size()
    title_ts = font_big.render("請選擇遊戲模式", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.15)))

    modes = [
        {"id": "TEST", "title": "測試模式", "desc": "快速測試：1輪10血敵人，直達結局", "color": (100, 100, 200)},
        {"id": "NORMAL", "title": "普通模式", "desc": "原汁原味的標準冒險體驗", "color": (100, 100, 100)},
        {"id": "BURST", "title": "無雙模式", "desc": "數值增加：初始能量變 4，卡牌傷害增加 5", "color": (50, 150, 50)},
        {"id": "HARD", "title": "高難模式", "desc": "數值增加：敵人血量增至 120，攻擊傷害增加 6", "color": (150, 50, 50)},
        {"id": "ENDLESS", "title": "無限模式", "desc": "挑戰極限：每 30 波一輪，難度不斷攀升", "color": (150, 150, 50)}
    ]
    btn_rects = {}
    for i, mode in enumerate(modes):
        rect = pygame.Rect(w // 2 - 300, h * 0.22 + i * 105, 600, 85)
        btn_rects[mode["id"]] = rect
        is_hover = rect.collidepoint((mx, my))
        bg_color = [min(255, c + 30) if is_hover else c for c in mode["color"]]
        pygame.draw.rect(surface, bg_color, rect, border_radius=10)
        if is_hover: pygame.draw.rect(surface, GOLD, rect, width=3, border_radius=10)
        t_ts = font_hp.render(mode["title"], True, WHITE)
        d_ts = font_main.render(mode["desc"], True, (220, 220, 220))
        surface.blit(t_ts, (rect.x + 30, rect.y + 15))
        surface.blit(d_ts, (rect.x + 30, rect.y + 45))
    return btn_rects


def draw_ui_surface(surface, game, mx, my):
    w, h = surface.get_size()

    mode_text = "普通" if game.selected_mode == "NORMAL" else (
        "無雙 (傷害+5, 能量+1)" if game.selected_mode == "BURST" else (
            "無限模式" if game.selected_mode == "ENDLESS" else "高難 (怪物強化)"))
    mode_ts = font_main.render(f"當前模式: {mode_text}", True, (180, 180, 180))
    surface.blit(mode_ts, (20, 20))

    wave_str = f"波次: {game.current_wave} / {game.max_waves}"
    if game.is_endless:
        wave_str = f"無限模式 [第 {game.endless_loop_count} 輪] - {wave_str}"
    wave_ts = font_main.render(wave_str, True, GOLD)
    surface.blit(wave_ts, (20, 50))

    if game.enemy_hp > 0:
        enemy_rect = pygame.Rect(w - 430, h * 0.35, 120, 120)
        if game.enemy_image:
            img_x = w - 430 + (120 - game.enemy_image.get_width()) // 2
            img_y = int(h * 0.35) + (120 - game.enemy_image.get_height()) // 2
            surface.blit(game.enemy_image, (img_x, img_y))
        else:
            pygame.draw.rect(surface, (150, 50, 50), enemy_rect, border_radius=10)
            if kirby_image:
                flipped_kirby = pygame.transform.flip(pygame.transform.scale(kirby_image, (100, 100)), True, False)
                surface.blit(flipped_kirby, (w - 420, h * 0.36))
        
        type_color = GOLD if game.stage_type in ["BOSS", "FINAL_BOSS"] else (ORANGE if game.stage_type == "ELITE" else WHITE)
        name_ts = font_hp.render(game.enemy_name, True, type_color)
        surface.blit(name_ts, (w - 480, h * 0.18))
        if game.enemy_stance_enabled:
            buff_ts = font_desc.render("[特殊·節奏大師]", True, GOLD)
            surface.blit(buff_ts, (w - 480, h * 0.205))
        
        hp_y = h * 0.28
        if game.enemy_stance_enabled:
            hp_y = h * 0.34
        draw_bar(surface, w - 480, hp_y, game.enemy_hp, game.enemy_max_hp, 0, RED)
        intent_ts = font_main.render(f"意圖攻擊: {game.enemy_intent}", True, WHITE)
        surface.blit(intent_ts, (w - 460, h * 0.22))

        if game.enemy_stance_enabled:
            stance_color = RED if game.enemy_stance == "ATTACK" else BLUE
            status_line = game.get_stance_status_text()
            if status_line:
                cur_ts = font_hp.render(status_line, True, stance_color)
                surface.blit(cur_ts, (w - 480, h * 0.255))
            preview_line = game.get_stance_preview_text()
            if preview_line:
                prev_ts = font_main.render(preview_line, True, GOLD)
                surface.blit(prev_ts, (w - 480, h * 0.295))

        status_y = h * 0.52
        status_spacing = 25
        
        if game.enemy_stun_turns > 0:
            stun_ts = font_desc.render(f"[暈眩] {game.enemy_stun_turns}回合", True, (255, 200, 100))
            surface.blit(stun_ts, (w - 430, status_y))
            status_y += status_spacing
        
        if game.enemy_petrify_turns > 0:
            pet_ts = font_desc.render(f"[石化] {game.enemy_petrify_turns}回合", True, (150, 150, 150))
            surface.blit(pet_ts, (w - 430, status_y))
            status_y += status_spacing
        
        if game.enemy_frozen_turns > 0:
            froz_ts = font_desc.render(f"[凍結] {game.enemy_frozen_turns}回合", True, (100, 200, 255))
            surface.blit(froz_ts, (w - 430, status_y))
            status_y += status_spacing
            
        if game.enemy_wet:
            wet_turns = getattr(game, 'enemy_wet_turns', 0)
            # 加上回合數顯示，如果因為某些機制導致回合數為0但仍潮濕，則當作底線顯示
            wet_str = f"[潮濕] {wet_turns}回合" if wet_turns > 0 else "[潮濕]"
            wet_ts = font_desc.render(wet_str, True, (50, 150, 255))
            surface.blit(wet_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.bloom_cores > 0:
            bloom_ts = font_desc.render(f"[草原核] x{game.bloom_cores}", True, (50, 200, 100))
            surface.blit(bloom_ts, (w - 430, status_y))
            status_y += status_spacing
            
        if game.enemy_dot_turns > 0:
            dot_ts = font_desc.render(f"[燃燒] {game.enemy_dot_damage}x{game.enemy_dot_turns}", True, (255, 100, 50))
            surface.blit(dot_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.enemy_vulnerable_turns > 0:
            vul_ts = font_desc.render(f"[易傷] {game.enemy_vulnerable_turns}回合", True, (255, 150, 150))
            surface.blit(vul_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.enemy_poison_turns > 0:
            poi_ts = font_desc.render(f"[中毒] {game.enemy_poison_turns}層", True, (150, 255, 150))
            surface.blit(poi_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.cards_played_this_turn > 0:
            combo_ts = font_desc.render(f"本回合連擊: {game.cards_played_this_turn}", True, (200, 255, 200))
            surface.blit(combo_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.reactions_this_turn > 0:
            reac_ts = font_desc.render(f"本回合反應: {game.reactions_this_turn}/3", True, (100, 255, 255))
            surface.blit(reac_ts, (w - 430, status_y))
            status_y += status_spacing

        if game.enemy_hit_shield > 0:
            elem_name_map = {"Pyro": "火", "Hydro": "水", "Cryo": "冰", "Dendro": "草", "Electro": "雷", "Geo": "岩", "None": "次數"}
            elem_text = elem_name_map.get(game.enemy_shield_element, "未知")
            shield_color = ELEMENT_COLORS.get(game.enemy_shield_element, (200, 200, 255))
            shield_ts = font_desc.render(f"[{elem_text}元素盾] {game.enemy_hit_shield}層", True, shield_color)
            surface.blit(shield_ts, (w - 430, status_y))
            
            # 增加破盾提示文本
            counters = ELEMENT_COUNTERS.get(game.enemy_shield_element, [])
            if counters:
                hint_map = {"Pyro": "火", "Hydro": "水", "Cryo": "冰", "Dendro": "草", "Electro": "雷", "Geo": "岩", "None": "物理"}
                hint_text = " / ".join([hint_map.get(c, c) for c in counters])
                hint_ts = font_desc.render(f"  (弱點: {hint_text})", True, (200, 200, 200))
                surface.blit(hint_ts, (w - 430, status_y + 20))
                status_y += 20 # 額外佔用一點空間
            
            status_y += status_spacing
            
        if game.enemy_charge_turns > 0:
            charge_color = RED if game.enemy_charge_turns == game.enemy_charge_max else GOLD
            charge_ts = font_desc.render(f"[大招蓄力] {game.enemy_charge_turns}/{game.enemy_charge_max}", True, charge_color)
            surface.blit(charge_ts, (w - 430, status_y))
            status_y += status_spacing
            
        if game.enemy_thorns > 0:
            thorn_ts = font_desc.render(f"[反傷外殼] {game.enemy_thorns}", True, (255, 100, 100))
            surface.blit(thorn_ts, (w - 430, status_y))
            status_y += status_spacing
            
        if game.enemy_scaling_strength > 0:
            scale_ts = font_desc.render(f"[力量成長] +{game.enemy_scaling_strength}/回合", True, (255, 150, 100))
            surface.blit(scale_ts, (w - 430, status_y))
            status_y += status_spacing

    # --- 繪製玩家角色模型 (序列幀動畫) - 底部 ---
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    frames = character_images.get(game.current_character)
    if frames:
        # 計算當前應該顯示哪一幀 (每秒播放 10 幀)
        frame_idx = int(game.animation_tick * 10) % len(frames)
        char_img = frames[frame_idx]
        
        # 根據全局 UI 縮放調整角色大小
        if ui_scale != 1.0:
            char_w, char_h = char_img.get_size()
            char_img = pygame.transform.smoothscale(char_img, (int(char_w * ui_scale), int(char_h * ui_scale)))
            
        # 增加輕微的呼吸感 (Y 軸上下漂浮)
        float_y = math.sin(game.animation_tick * 3) * 5 * ui_scale
        # 根據比例調整繪製位置
        char_x = 100 * ui_scale
        char_y = h - (320 * ui_scale) + float_y
        surface.blit(char_img, (char_x, char_y))
    else:
        # 如果沒圖片，繪製一個圓圈代表
        pygame.draw.circle(surface, (200, 200, 200), (int(160 * ui_scale), h - int(250 * ui_scale)), int(40 * ui_scale))
    
    # --- 繪製能量 (使用圖片) - 最下方 ---
    if energy_image:
        # 繪製能量球圖片 (80x80)
        img_size = int(80 * ui_scale)
        scaled_energy = pygame.transform.smoothscale(energy_image, (img_size, img_size))
        img_x, img_y = 60 * ui_scale, h - (100 * ui_scale)
        surface.blit(scaled_energy, (img_x, img_y))
        # 將數值移至圖片右側
        energy_ts = font_hp.render(f"{game.energy}/{game.base_energy}", True, WHITE)
        text_rect = energy_ts.get_rect(midleft=(img_x + 85 * ui_scale, img_y + img_size // 2))
        surface.blit(energy_ts, text_rect)
    else:
        # 備用方案
        energy_ts = font_big.render(f"E: {game.energy}/{game.base_energy}", True, GOLD)
        surface.blit(energy_ts, (100 * ui_scale, h - 90 * ui_scale))

    # --- 繪製玩家血條 - 最底部 ---
    draw_bar(surface, 100 * ui_scale, h - 140 * ui_scale, game.player_hp, game.player_max_hp, game.player_block, GREEN)
    
    # 狀態與聖遺物跟隨血條移動
    if game.strength > 0:
        str_ts = font_desc.render(f"力量: {game.strength}", True, (255, 100, 100))
        surface.blit(str_ts, (100 * ui_scale, h - 155 * ui_scale))
    if game.next_turn_energy > 0:
        nxt_ts = font_desc.render(f"下回合能量 +{game.next_turn_energy}", True, GOLD)
        surface.blit(nxt_ts, (180 * ui_scale, h - 155 * ui_scale))
    
    relic_x = 100 * ui_scale
    for relic in game.relics:
        pygame.draw.circle(surface, relic["color"], (int(relic_x), int(h - 175 * ui_scale)), int(15 * ui_scale))
        if pygame.Rect(relic_x - 15 * ui_scale, h - 190 * ui_scale, 30 * ui_scale, 30 * ui_scale).collidepoint((mx, my)):
            r_ts = font_desc.render(relic["name"], True, WHITE)
            surface.blit(r_ts, (relic_x - 30 * ui_scale, h - 210 * ui_scale))
        relic_x += 40 * ui_scale
        
    if game.maya_active:
        maya_ts = font_desc.render("[淨善攝位激活]", True, (100, 255, 100))
        surface.blit(maya_ts, (100 * ui_scale, h - 165 * ui_scale))

    # --- 1. 計算手牌佈局與懸停檢測 ---
    num_cards = len(game.hand)
    draw_queue = []
    hovered_card = None
    
    if num_cards > 0:
        center_x = w // 2
        base_y = h - 100
        card_gap = 60   
        current_hand_width = (num_cards - 1) * card_gap
        max_angle = 30 
        arc_height = 80
        
        for i, card in enumerate(game.hand):
            if num_cards > 1:
                rel_pos = (i / (num_cards - 1)) - 0.5
            else:
                rel_pos = 0
            
            hand_split = 10 if i < num_cards/2 else -10
            card_x = center_x + rel_pos * current_hand_width - hand_split
            card_y = base_y + (rel_pos**2) * arc_height * 2.5
            angle = -rel_pos * max_angle * 2.2
            
            # 更新卡片的碰撞矩形（基於原始位置，不包含懸停偏移）
            # 這樣可以防止懸停時卡片移走導致的判定失效（抽搐問題）
            card.rect = pygame.Rect(0, 0, 165, 235)
            card.rect.center = (int(card_x), int(card_y))
            
            # 判定是否懸停 (從後往前判定，確保最上層優先)
            # 注意：這裡我們先不更新 hovered_card，等循環結束或反向遍歷
        
        # 反向遍歷檢測懸停
        for card in reversed(game.hand):
            if card.rect.collidepoint((mx, my)):
                hovered_card = card
                break

        # 準備繪製隊列
        for i, card in enumerate(game.hand):
            if num_cards > 1:
                rel_pos = (i / (num_cards - 1)) - 0.5
            else:
                rel_pos = 0
            
            hand_split = 10 if i < num_cards/2 else -10
            card_x = center_x + rel_pos * current_hand_width - hand_split
            card_y = base_y + (rel_pos**2) * arc_height * 2.5
            angle = -rel_pos * max_angle * 2.2
            
            is_selectable = (game.state == "SELECT_CARD" and card != game.selection_source_card)
            
            d_dmg = 0
            if card.type == "ATTACK":
                d_dmg += game.strength
                if card.base_name == "雷霆连击":
                    d_dmg += getattr(card, 'permanent_dmg_bonus', 0)
                elif card.base_name == "黎明·斩击":
                    d_dmg += game.pyro_damage_bonus
            
            draw_queue.append({
                "card": card,
                "x": card_x,
                "y": card_y,
                "is_hovered": (card == hovered_card),
                "is_selected": is_selectable,
                "extra_dmg": d_dmg,
                "angle": angle
            })

    # --- 2. 執行繪製 ---
    if num_cards > 0:
        # 先繪製所有非懸停卡片
        for item in draw_queue:
            if not item["is_hovered"]:
                item["card"].draw(surface, item["x"], item["y"], False, 
                                 is_selected=item["is_selected"], extra_dmg=item["extra_dmg"], angle=item["angle"])
        
        # 最後繪製懸停卡片，確保它在最上層
    if hovered_card:
        for item in draw_queue:
            if item["is_hovered"]:
                item["card"].draw(surface, item["x"], item["y"], True, 
                                 is_selected=item["is_selected"], extra_dmg=item["extra_dmg"], angle=item["angle"])

    # 牌堆顯示：左側藍色(牌庫)，右側橙色(棄牌)
    draw_pile(surface, 40 * ui_scale, h - 80 * ui_scale, len(game.deck), "牌庫", BLUE)
    draw_pile(surface, w - 40 * ui_scale, h - 80 * ui_scale, len(game.discard), "棄牌", ORANGE)

    # 結束回合按鈕 (右下角)
    btn_w, btn_h = 150 * ui_scale, 50 * ui_scale
    btn_rect = pygame.Rect(w - 230 * ui_scale, h - 120 * ui_scale, btn_w, btn_h)
    pygame.draw.rect(surface, (80, 80, 80), btn_rect, border_radius=int(5 * ui_scale))
    btn_text = font_main.render("結束回合", True, WHITE)
    surface.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

    # 查看牌組按鈕 (移動到最右上角)
    total_cards = len(game.deck) + len(game.hand) + len(game.discard)
    deck_btn_w, deck_btn_h = 150 * ui_scale, 36 * ui_scale
    deck_btn_rect = pygame.Rect(w - deck_btn_w - 15 * ui_scale, 10 * ui_scale, deck_btn_w, deck_btn_h)
    
    is_deck_hover = deck_btn_rect.collidepoint((mx, my))
    deck_btn_color = (40, 60, 100) if is_deck_hover else (30, 45, 80)
    pygame.draw.rect(surface, deck_btn_color, deck_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD, deck_btn_rect, width=1, border_radius=int(8 * ui_scale))
    
    deck_ts = font_main.render(f"查看牌組 ({total_cards})", True, WHITE)
    surface.blit(deck_ts, deck_ts.get_rect(center=deck_btn_rect.center))

    # 機制圖按鈕 (放在查看牌組左邊)
    guide_btn_w, guide_btn_h = 120 * ui_scale, 36 * ui_scale
    guide_btn_rect = pygame.Rect(deck_btn_rect.left - guide_btn_w - 10 * ui_scale, 10 * ui_scale, guide_btn_w, guide_btn_h)
    
    is_guide_hover = guide_btn_rect.collidepoint((mx, my))
    guide_btn_color = (60, 100, 60) if is_guide_hover else (40, 70, 40) 
    pygame.draw.rect(surface, guide_btn_color, guide_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD if is_guide_hover else (140, 140, 160), guide_btn_rect, width=2, border_radius=int(8 * ui_scale))
    
    guide_ts = font_main.render("機制圖鑑", True, WHITE)
    surface.blit(guide_ts, guide_ts.get_rect(center=guide_btn_rect.center))

    return hovered_card, btn_rect, deck_btn_rect, guide_btn_rect


def draw_pile(surface, x, y, count, label, color):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    pygame.draw.rect(surface, (40, 40, 50), (x - 25 * ui_scale, y - 60 * ui_scale, 50 * ui_scale, 70 * ui_scale), border_radius=int(4 * ui_scale))
    for i in range(min(count, 5)):
        offset = i * 3 * ui_scale
        pygame.draw.rect(surface, color, (x - 22 * ui_scale + offset * 0.5, y - 57 * ui_scale + offset, 44 * ui_scale - offset, 64 * ui_scale - offset),
                         border_radius=int(3 * ui_scale))
    count_ts = font_big.render(str(count), True, WHITE)
    surface.blit(count_ts, (x - count_ts.get_width() // 2, y - 25 * ui_scale))
    label_ts = font_hp.render(label, True, (180, 180, 180))
    surface.blit(label_ts, (x - label_ts.get_width() // 2, y + 10 * ui_scale))


def draw_reward_screen_surface(surface, game, mx, my):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    # 標題與副標題
    title_ts = font_big.render("戰鬥勝利！", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.15)))
    sub_ts = font_main.render("請選擇一項獎勵", True, (200, 200, 200))
    surface.blit(sub_ts, sub_ts.get_rect(center=(w // 2, h * 0.22)))

    hovered_reward = None
    for card in game.reward_cards:
        if card.rect.collidepoint((mx, my)):
            hovered_reward = card
            break

    # 計算卡牌置中起始 X 座標
    num_rewards = len(game.reward_cards)
    spacing = 180 * ui_scale
    total_width = (num_rewards - 1) * spacing
    start_x = w // 2 - total_width // 2
    
    # 垂直居中位置 (卡牌基準高度為 235)
    center_y = h * 0.5
    
    for i, card in enumerate(game.reward_cards):
        card.draw(surface, start_x + i * spacing, center_y, (card == hovered_reward), (card == game.selected_reward))

    if game.pending_relic:
        relic = game.pending_relic
        relic_rect = pygame.Rect(w // 2 - 150 * ui_scale, h * 0.75, 300 * ui_scale, 60 * ui_scale)
        pygame.draw.rect(surface, (50, 50, 70), relic_rect, border_radius=int(10 * ui_scale))
        pygame.draw.rect(surface, GOLD, relic_rect, width=2, border_radius=int(10 * ui_scale))
        
        pygame.draw.circle(surface, relic["color"], (int(w // 2 - 110 * ui_scale), int(h * 0.78)), int(20 * ui_scale))
        
        r_name_ts = font_hp.render(f"額外獲得：{relic['name']}", True, WHITE)
        r_desc_ts = font_desc.render(relic["desc"], True, (200, 200, 200))
        surface.blit(r_name_ts, (w // 2 - 80 * ui_scale, h * 0.755))
        surface.blit(r_desc_ts, (w // 2 - 80 * ui_scale, h * 0.785))

    confirm_rect = pygame.Rect(w // 2 - 100 * ui_scale, h * 0.88, 200 * ui_scale, 50 * ui_scale)
    btn_color = (50, 180, 50) if game.selected_reward else (60, 60, 60)
    pygame.draw.rect(surface, btn_color, confirm_rect, border_radius=int(5 * ui_scale))
    btn_text = font_main.render("點擊跳過" if not game.selected_reward else "確認領取", True, WHITE)
    surface.blit(btn_text, btn_text.get_rect(center=confirm_rect.center))

    # 右上角查看牌組按鈕
    deck_btn_w, deck_btn_h = 150 * ui_scale, 36 * ui_scale
    deck_btn_rect = pygame.Rect(w - deck_btn_w - 15 * ui_scale, 10 * ui_scale, deck_btn_w, deck_btn_h)
    is_deck_hover = deck_btn_rect.collidepoint((mx, my))
    deck_btn_color = (40, 60, 100) if is_deck_hover else (30, 45, 80)
    pygame.draw.rect(surface, deck_btn_color, deck_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD, deck_btn_rect, width=1, border_radius=int(8 * ui_scale))
    total_cards = len(game.deck) + len(game.hand) + len(game.discard)
    deck_ts = font_main.render(f"查看牌組 ({total_cards})", True, WHITE)
    surface.blit(deck_ts, deck_ts.get_rect(center=deck_btn_rect.center))

    # 在查看牌組左邊繪製機制圖按鈕
    guide_btn_w, guide_btn_h = 120 * ui_scale, 36 * ui_scale
    guide_btn_rect = pygame.Rect(deck_btn_rect.left - guide_btn_w - 10 * ui_scale, 10 * ui_scale, guide_btn_w, guide_btn_h)
    is_guide_hover = guide_btn_rect.collidepoint((mx, my))
    guide_btn_color = (60, 100, 60) if is_guide_hover else (40, 70, 40)
    pygame.draw.rect(surface, guide_btn_color, guide_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD if is_guide_hover else (140, 140, 160), guide_btn_rect, width=2, border_radius=int(8 * ui_scale))
    guide_ts = font_main.render("機制圖鑑", True, WHITE)
    surface.blit(guide_ts, guide_ts.get_rect(center=guide_btn_rect.center))

    return hovered_reward, confirm_rect, guide_btn_rect, deck_btn_rect

def draw_discovery_screen_surface(surface, game, mx, my):
    """繪製每兩回合一次的靈光一閃界面"""
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    # 半透明遮罩
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    
    title_ts = font_big.render("靈光一閃！", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.25)))
    sub_ts = font_main.render("從牌組中額外挑選一張卡牌加入手牌", True, (200, 200, 200))
    surface.blit(sub_ts, sub_ts.get_rect(center=(w // 2, h * 0.32)))

    hovered_card = None
    for card in game.discovery_cards:
        if card.rect.collidepoint((mx, my)):
            hovered_card = card
            break

    num_cards = len(game.discovery_cards)
    spacing = 200 * ui_scale
    total_width = (num_cards - 1) * spacing
    start_x = w // 2 - total_width // 2
    
    # 垂直居中位置
    center_y = h * 0.55
    
    for i, card in enumerate(game.discovery_cards):
        card.draw(surface, start_x + i * spacing, center_y, (card == hovered_card), show_marked=False)

    return hovered_card


def draw_deck_view_surface(surface, game, mx, my):
    w, h = surface.get_size()
    ui_scale = h / 720.0

    # 半透明背景
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    surface.blit(overlay, (0, 0))

    # --- 1. 獲取並排序卡牌 ---
    type_order = {"ATTACK": 0, "SKILL": 1, "POWER": 2}
    pool = (
        game.owned_cards
        + [c for c in game.sidelined_power_cards if c not in game.owned_cards]
    )
    if game.deck_sort_mode == "TYPE":
        all_cards = sorted(
            pool,
            key=lambda c: (type_order.get(c.type, 3), c.cost, c.name),
        )
    else:
        all_cards = sorted(
            pool,
            key=lambda c: (c.cost, type_order.get(c.type, 3), c.name),
        )

    # --- 2. 網格佈局繪製 ---
    max_per_row = 5 # 參考圖為 5 列
    card_spacing_x = 220 * ui_scale # 增加橫向間距
    card_spacing_y = 280 * ui_scale # 增加縱向間距
    # 將起始 Y 下移，增加與頂部欄的距離
    start_y_base = h * 0.35
    
    # 滾動區域裁剪 (確保不遮擋頂部排序欄)
    clip_rect = pygame.Rect(0, h * 0.18, w, h * 0.65)
    
    num_rows = (len(all_cards) + max_per_row - 1) // max_per_row
    content_h = num_rows * card_spacing_y + 150 * ui_scale
    game.max_deck_scroll = max(0, content_h - (h * 0.7)) # 基準顯示高度約 0.7h
    game.deck_scroll = max(0, min(game.deck_scroll, game.max_deck_scroll))
    
    start_x = w // 2 - ((min(len(all_cards), max_per_row) - 1) * card_spacing_x) // 2
    
    hovered_in_deck = None
    for idx, card in enumerate(all_cards):
        row = idx // max_per_row
        col = idx % max_per_row
        x = start_x + col * card_spacing_x
        y = start_y_base + row * card_spacing_y - game.deck_scroll
        
        # 裁剪繪製：只在指定區域內繪製卡牌
        if clip_rect.top - 100 * ui_scale < y < clip_rect.bottom + 100 * ui_scale:
            # 只有當鼠標在裁剪區域內時才允許懸停
            is_hover = card.rect.collidepoint((mx, my)) and clip_rect.collidepoint((mx, my))
            card.draw(surface, x, y, is_hover, show_marked=False)
            if is_hover: hovered_in_deck = card

    # --- 3. 頂部排序欄 (置於頂層) ---
    sort_bar_y = h * 0.08
    sort_bar_h = 45 * ui_scale
    pygame.draw.rect(surface, (20, 40, 60), (0, sort_bar_y, w, sort_bar_h))
    pygame.draw.line(surface, GOLD, (0, sort_bar_y), (w, sort_bar_y), 2)
    pygame.draw.line(surface, GOLD, (0, sort_bar_y + sort_bar_h), (w, sort_bar_y + sort_bar_h), 2)

    sort_options = [
        {"id": "TYPE", "text": "按類型 ▲", "x": w * 0.4},
        {"id": "COST", "text": "按能量 ▲", "x": w * 0.6}
    ]
    
    sort_rects = {}
    for opt in sort_options:
        txt_color = GOLD if game.deck_sort_mode == opt["id"] else WHITE
        ts = font_main.render(opt["text"], True, txt_color)
        rect = ts.get_rect(center=(opt["x"], sort_bar_y + sort_bar_h // 2))
        if rect.collidepoint((mx, my)):
            pygame.draw.rect(surface, (255, 255, 255, 30), rect.inflate(20, 10), border_radius=5)
        surface.blit(ts, rect)
        sort_rects[opt["id"]] = rect

    # --- 4. 底部提示與返回按鈕 (置於頂層) ---
    # 返回按鈕 (仿照參考圖：左下角大按鈕)
    back_rect = pygame.Rect(40 * ui_scale, h - 90 * ui_scale, 160 * ui_scale, 50 * ui_scale)
    is_back_hover = back_rect.collidepoint((mx, my))
    back_color = (140, 40, 40) if is_back_hover else (100, 30, 30)
    pygame.draw.rect(surface, back_color, back_rect, border_radius=int(10 * ui_scale))
    pygame.draw.rect(surface, GOLD, back_rect, width=2, border_radius=int(10 * ui_scale))
    back_ts = font_hp.render("返回", True, WHITE)
    surface.blit(back_ts, back_ts.get_rect(center=back_rect.center))

    # 底部提示文字
    bottom_hint = f"這些卡牌將會出現在每一場戰鬥中。 (總卡數: {len(all_cards)})"
    hint_ts = font_main.render(bottom_hint, True, (180, 180, 180))
    surface.blit(hint_ts, hint_ts.get_rect(center=(w // 2, h - 65 * ui_scale)))

    # --- 5. 滾動條 (放置於右側中間) ---
    if game.max_deck_scroll > 0:
        bar_w = 8 * ui_scale
        # 滾動條長度縮短並置中
        bar_h = h * 0.5 
        bar_x = w - 30 * ui_scale
        bar_y = h * 0.25 # 置中於屏幕垂直方向
        
        # 滾動條背景
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h), border_radius=int(4 * ui_scale))
        
        # 滑塊
        thumb_h = max(30 * ui_scale, (bar_h / content_h) * bar_h)
        # 根據比例計算滑塊位置
        thumb_y = bar_y + (game.deck_scroll / game.max_deck_scroll) * (bar_h - thumb_h)
        t_color = (180, 180, 180) if game.is_dragging_deck_scroll else (100, 100, 100)
        pygame.draw.rect(surface, t_color, (bar_x, thumb_y, bar_w, thumb_h), border_radius=int(4 * ui_scale))

    return back_rect, sort_rects

def draw_upgrade_view_surface(surface, game, mx, my):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 230))
    surface.blit(overlay, (0, 0))

    # 顯示本局已獲得的所有卡牌（含暫時旁置的能力牌）
    all_cards = sorted(
        game.owned_cards,
        key=lambda c: (c.name, c.upgraded),
    )
    num_cards = len(all_cards)
    max_per_row = 6 
    card_spacing_x = 200 * ui_scale # 增加橫向間距
    card_spacing_y = 280 * ui_scale # 增加縱向間距
    
    start_y_base = h * 0.35 # 下移起始位置
    clip_rect = pygame.Rect(0, h * 0.18, w, h * 0.65)
    
    # 計算內容高度與滾動範圍
    num_rows = (num_cards + max_per_row - 1) // max_per_row
    content_h = num_rows * card_spacing_y + 100 * ui_scale
    game.max_upgrade_scroll = max(0, content_h - clip_rect.height)
    game.upgrade_scroll = max(0, min(game.upgrade_scroll, game.max_upgrade_scroll))
    
    # 網格起始 X
    cols_in_row = min(num_cards, max_per_row)
    total_grid_w = (cols_in_row - 1) * card_spacing_x
    start_x = w // 2 - total_grid_w // 2
    
    hovered_card = None
    for index, card in enumerate(all_cards):
        row = index // max_per_row
        col = index % max_per_row
        card_x = start_x + col * card_spacing_x
        card_y = start_y_base + row * card_spacing_y - game.upgrade_scroll
        
        # 裁剪繪製
        if clip_rect.top - 200 * ui_scale < card_y < clip_rect.bottom + 200 * ui_scale:
            is_hover = card.rect.collidepoint((mx, my)) and clip_rect.collidepoint((mx, my))
            card.draw(surface, card_x, card_y, is_hover, is_selected=card.upgraded, show_marked=False)
            if is_hover: hovered_card = card
            
            if card.upgraded:
                s_w, s_h = int(165 * ui_scale), int(235 * ui_scale)
                s = pygame.Surface((s_w, s_h), pygame.SRCALPHA)
                s.fill((0, 0, 0, 150))
                surface.blit(s, (card_x - s_w // 2, card_y - s_h // 2))
                up_ts = font_hp.render("MAX", True, GOLD)
                surface.blit(up_ts, up_ts.get_rect(center=(card_x, card_y)))
            elif card in game.sidelined_power_cards:
                act_ts = font_desc.render("本輪生效", True, (120, 255, 160))
                surface.blit(act_ts, act_ts.get_rect(center=(card_x, card_y + 90 * ui_scale)))

    # --- 頂層 UI 元素 (置於最後繪製) ---
    title_ts = font_big.render("【精英/BOSS 獎勵】從已獲得牌組中選一張升級", True, GOLD)
    surface.blit(title_ts, title_ts.get_rect(center=(w // 2, h * 0.06)))

    close_rect = pygame.Rect(w // 2 - 100 * ui_scale, int(h * 0.13), 200 * ui_scale, 40 * ui_scale)
    is_hover_close = close_rect.collidepoint((mx, my))
    pygame.draw.rect(surface, (100, 100, 100) if is_hover_close else (60, 60, 60), close_rect, border_radius=int(5 * ui_scale))
    close_ts = font_main.render("跳過升級", True, WHITE)
    surface.blit(close_ts, close_ts.get_rect(center=close_rect.center))
    
    # 繪製右側滾動條
    if game.max_upgrade_scroll > 0:
        bar_w = 10 * ui_scale
        bar_h = clip_rect.height
        bar_x = w - 25 * ui_scale
        bar_y = clip_rect.y
        pygame.draw.rect(surface, (30, 30, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=int(5 * ui_scale))
        thumb_h = max(40 * ui_scale, (clip_rect.height / content_h) * bar_h)
        thumb_y = bar_y + (game.upgrade_scroll / game.max_upgrade_scroll) * (bar_h - thumb_h)
        t_color = (200, 200, 200) if game.is_dragging_upgrade_scroll else (120, 120, 120)
        pygame.draw.rect(surface, t_color, (bar_x + 1, thumb_y, bar_w - 2, thumb_h), border_radius=int(4 * ui_scale))
        
    # 右上角查看牌組按鈕
    deck_btn_w, deck_btn_h = 150 * ui_scale, 36 * ui_scale
    deck_btn_rect = pygame.Rect(w - deck_btn_w - 15 * ui_scale, 10 * ui_scale, deck_btn_w, deck_btn_h)
    is_deck_hover = deck_btn_rect.collidepoint((mx, my))
    deck_btn_color = (40, 60, 100) if is_deck_hover else (30, 45, 80)
    pygame.draw.rect(surface, deck_btn_color, deck_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD, deck_btn_rect, width=1, border_radius=int(8 * ui_scale))
    total_cards = len(game.deck) + len(game.hand) + len(game.discard)
    deck_ts = font_main.render(f"查看牌組 ({total_cards})", True, WHITE)
    surface.blit(deck_ts, deck_ts.get_rect(center=deck_btn_rect.center))

    # 在查看牌組左邊繪製機制圖按鈕
    guide_btn_w, guide_btn_h = 120 * ui_scale, 36 * ui_scale
    guide_btn_rect = pygame.Rect(deck_btn_rect.left - guide_btn_w - 10 * ui_scale, 10 * ui_scale, guide_btn_w, guide_btn_h)
    is_guide_hover = guide_btn_rect.collidepoint((mx, my))
    guide_btn_color = (60, 100, 60) if is_guide_hover else (40, 70, 40)
    pygame.draw.rect(surface, guide_btn_color, guide_btn_rect, border_radius=int(8 * ui_scale))
    pygame.draw.rect(surface, GOLD if is_guide_hover else (140, 140, 160), guide_btn_rect, width=2, border_radius=int(8 * ui_scale))
    guide_ts = font_main.render("機制圖鑑", True, WHITE)
    surface.blit(guide_ts, guide_ts.get_rect(center=guide_btn_rect.center))

    return close_rect, hovered_card, guide_btn_rect, deck_btn_rect


def draw_bar(surface, x, y, cur, mx, block, color):
    w, h = surface.get_size()
    ui_scale = h / 720.0
    
    width = 250 * ui_scale
    height = 15 * ui_scale
    pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
    if mx > 0:
        pygame.draw.rect(surface, color, (x, y, int((cur / mx) * width), height))
    if block > 0:
        shield_w = 30 * ui_scale
        shield_h = 34 * ui_scale
        cx = x - 22 * ui_scale
        cy = y + 8 * ui_scale
        if shield_image:
            img = pygame.transform.smoothscale(shield_image, (int(shield_w), int(shield_h)))
            surface.blit(img, (cx - shield_w // 2, cy - shield_h // 2))
        else:
            shield_points = [
                (cx, cy - shield_h // 2),
                (cx + shield_w // 2, cy - shield_h // 2 + 6 * ui_scale),
                (cx + shield_w // 2, cy + shield_h // 4),
                (cx, cy + shield_h // 2),
                (cx - shield_w // 2, cy + shield_h // 4),
                (cx - shield_w // 2, cy - shield_h // 2 + 6 * ui_scale),
            ]
            pygame.draw.polygon(surface, BLUE, shield_points)
            pygame.draw.polygon(surface, (150, 180, 255), shield_points, width=2)
        b_ts = font_main.render(str(block), True, WHITE)
        surface.blit(b_ts, b_ts.get_rect(center=(cx, cy)))
    val_ts = font_hp.render(f"{cur}/{mx}", True, WHITE)
    surface.blit(val_ts, (x + width // 2 - val_ts.get_width() // 2, y - 25 * ui_scale))


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        sound_map = {
            "attack": ["attack.mp3", "attack.wav"],
            "shield": ["shield.mp3", "shield.wav"],
            "hurt": ["hurt.mp3", "hurt.wav"],
            "jump": ["星之卡比掉下悬崖_爱给网_aigei_com.mp3", "jump.mp3", "jump.wav"],
            "gta_death": ["GTA V 死亡逮捕音效(GTA V WastedBuste_爱给网_aigei_com.mp3"],
            "mage_death": ["法师死亡_爱给网_aigei_com.mp3"]
        }
        
        for name, files in sound_map.items():
            found = False
            for filename in files:
                path = os.path.join(get_base_path(), "audio", filename)
                if os.path.exists(path):
                    try:
                        self.sounds[name] = pygame.mixer.Sound(path)
                        self.sounds[name].set_volume(0.5)
                        found = True
                        break
                    except Exception as e:
                        print(f"無法加載音效 {filename}: {e}")
            
            if not found:
                self.sounds[name] = None

    def play(self, sound_name):
        sound = self.sounds.get(sound_name)
        if sound:
            sound.play()

    def set_volume(self, volume):
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(volume)


FLOAT_ANIM_TYPES = frozenset({
    "damage_enemy", "block_player", "damage_player", "heal_player", "dot_damage",
    "true_damage", "status_enemy",
})
MAX_ANIMS_PER_FRAME = 6
MAX_FLOATS_PER_FRAME = 2


def _collapse_status_messages(game):
    """合併排隊中的連續狀態提示，避免一幀噴出過多紫字。"""
    if not game.anim_queue or game.anim_queue[0][0] != "status_enemy":
        return
    msgs = []
    while game.anim_queue and game.anim_queue[0][0] == "status_enemy":
        msgs.append(game.anim_queue.pop(0))
    if len(msgs) == 1:
        game.anim_queue.insert(0, msgs[0])
        return
    _, _, x, y = msgs[-1]
    if len(msgs) <= 2:
        text = " · ".join(m[1] for m in msgs)
    else:
        text = f"{msgs[-2][1]} · {msgs[-1][1]}"
    game.anim_queue.insert(0, ("status_enemy", text, x, y))


def process_animation_queue(game, anim_mgr, sound_mgr):
    _collapse_status_messages(game)
    processed = 0
    floats_added = 0
    while game.anim_queue and processed < MAX_ANIMS_PER_FRAME:
        if floats_added >= MAX_FLOATS_PER_FRAME:
            atype = game.anim_queue[0][0]
            if atype in FLOAT_ANIM_TYPES:
                break

        anim_data = game.anim_queue.pop(0)
        atype = anim_data[0]
        processed += 1

        if atype == "card_fly":
            _, card, sx, sy, tx, ty = anim_data
            anim_mgr.add(CardFly(card, (sx, sy), (tx, ty)))
        elif atype == "damage_enemy":
            _, dmg, x, y = anim_data
            sound_mgr.play("attack")
            if game.flash_enabled:
                anim_mgr.shake_screen(intensity=8, duration=0.2)
                anim_mgr.add(FlashScreen((255, 255, 255), 0.15))
            anim_mgr.add_float_text(x, y, f"-{dmg}", RED, size=32, duration=1.8)
            floats_added += 1
        elif atype == "block_player":
            _, blk, x, y = anim_data
            sound_mgr.play("shield")
            anim_mgr.add_float_text(x, y, f"+{blk} 護盾", BLUE, size=24)
            floats_added += 1
        elif atype == "damage_player":
            _, dmg, x, y = anim_data
            sound_mgr.play("hurt")
            if game.flash_enabled:
                anim_mgr.shake_screen(intensity=15, duration=0.3)
                anim_mgr.add(FlashScreen((220, 40, 40), 0.2))
            anim_mgr.add_float_text(x, y, f"-{dmg}", RED, size=32, duration=1.9)
            floats_added += 1
        elif atype == "heal_player":
            _, amt, x, y = anim_data
            anim_mgr.add_float_text(x, y, f"+{amt} 生命", GREEN, size=24)
            floats_added += 1
        elif atype == "dot_damage":
            _, dmg, x, y = anim_data
            anim_mgr.add_float_text(x, y, f"{dmg} 燃燒", (255, 100, 50), size=22)
            floats_added += 1
        elif atype == "true_damage":
            _, dmg, x, y = anim_data
            anim_mgr.add_float_text(x, y, f"-{dmg} 真傷", (255, 230, 120), size=26, duration=2.0)
            floats_added += 1
        elif atype == "status_enemy":
            _, msg, x, y = anim_data
            anim_mgr.add_float_text(x, y, msg, (200, 150, 255), size=24, duration=2.6)
            floats_added += 1
        elif atype == "enemy_death":
            sound_mgr.play("mage_death")


def play_bgm(volume=0.5, is_endless=False):
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        bgm_found = False
        if is_endless:
            bgm_path = os.path.join(get_base_path(), "audio", "Nyanyanyanyanyanyanya.mp3")
            if os.path.exists(bgm_path):
                pygame.mixer.music.load(bgm_path)
                bgm_found = True
        
        if not bgm_found:
            for ext in [".mp3", ".wav"]:
                bgm_path = os.path.join(get_base_path(), "audio", f"bgm{ext}")
                if os.path.exists(bgm_path):
                    pygame.mixer.music.load(bgm_path)
                    bgm_found = True
                    break
        
        if bgm_found:
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        else:
            print("警告：未找到背景音樂文件 (bgm.mp3 或 bgm.wav)")
    except Exception as e:
        print(f"無法播放背景音樂: {e}")


def main():
    global screen

    game = BattleManager()
    play_bgm(game.volume)

    anim_mgr = AnimationManager()
    sound_mgr = SoundManager()
    sound_mgr.set_volume(game.volume)
    
    clock = pygame.time.Clock()

    menu_rects = {}
    setting_rects = {}
    mode_rects = {}
    last_state = game.state

    while True:
        dt = clock.tick(60) / 1000.0
        game.animation_tick += dt
        
        # 初始化 UI 變量，防止跨狀態衝突
        hovered = None
        hovered_reward = None
        hovered_discovery = None
        btn_rect = pygame.Rect(0,0,0,0)
        deck_btn_rect = pygame.Rect(0,0,0,0)
        confirm_rect = pygame.Rect(0,0,0,0)
        close_rect = pygame.Rect(0,0,0,0)
        mechanics_btn_rect = pygame.Rect(0, 0, 0, 0)
        guide_close_rect = pygame.Rect(0, 0, 0, 0)
        menu_rects = {}
        setting_rects = {}
        mode_rects = {}

        if game.state == "JUMP" and last_state != "JUMP":
            pygame.mixer.music.stop()
            sound_mgr.play("jump")
        elif game.state == "GAMEOVER" and last_state != "GAMEOVER":
            pygame.mixer.music.stop()
            sound_mgr.play("gta_death")
        elif game.state == "MAIN_MENU" and last_state in ["VICTORY", "GAMEOVER", "STARTUP"]:
            if not pygame.mixer.music.get_busy():
                play_bgm(game.volume, is_endless=game.is_endless)
        
        last_state = game.state

        process_animation_queue(game, anim_mgr, sound_mgr)
        anim_mgr.update(dt)

        mx, my = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        w, h = screen.get_size()
        ui_scale = h / 720.0

        # 更新牌組滾動拖拽
        if game.show_deck and game.is_dragging_deck_scroll:
            bar_y = h * 0.25
            bar_h = h * 0.7
            if bar_h > 0:
                rel_y = (my - bar_y) / bar_h
                game.deck_scroll = rel_y * game.max_deck_scroll
                game.deck_scroll = max(0, min(game.deck_scroll, game.max_deck_scroll))
        
        # 更新強化界面滾動拖拽
        if game.state == "UPGRADE_CARD" and game.is_dragging_upgrade_scroll:
            bar_y = h * 0.25
            bar_h = h * 0.65
            if bar_h > 0:
                rel_y = (my - bar_y) / bar_h
                game.upgrade_scroll = rel_y * game.max_upgrade_scroll
                game.upgrade_scroll = max(0, min(game.upgrade_scroll, game.max_upgrade_scroll))

        shake_x, shake_y = anim_mgr.get_shake_offset()
        use_shake = (shake_x != 0 or shake_y != 0)

        for p in particles:
            p.update()
        
        current_bg = None
        if game.state in ["STARTUP", "MAIN_MENU", "SETTINGS", "MODE_SELECT"]:
            current_bg = background_menu
        elif game.state in ("BATTLE", "REWARD", "ENEMY_TURN", "SELECT_CARD", "DISCOVERY", "UPGRADE_CARD"):
            current_bg = background_battle
        elif game.state == "JUMP":
            current_bg = background_victory
        
        if use_shake:
            game_surface = pygame.Surface((w, h))
            if current_bg:
                game_surface.blit(current_bg, (0, 0))
            else:
                game_surface.fill((30, 30, 40))
            for p in particles:
                pygame.draw.circle(game_surface, (*p.color, p.alpha), (int(p.x), int(p.y)), p.size)
            main_surface = game_surface
        else:
            if current_bg:
                screen.blit(current_bg, (0, 0))
            else:
                screen.fill((30, 30, 40))
            for p in particles:
                pygame.draw.circle(screen, (*p.color, p.alpha), (int(p.x), int(p.y)), p.size)
            main_surface = screen

        if game.state == "STARTUP":
            if game.alpha < 255:
                game.alpha += 5
                if game.alpha > 255: game.alpha = 255
            else:
                pygame.time.delay(300)
                game.state = "MAIN_MENU"
            logo_ts = font_big.render("GENSHIN START", True, GOLD)
            logo_ts.set_alpha(game.alpha)
            main_surface.blit(logo_ts, logo_ts.get_rect(center=(w // 2, h // 2)))

        elif game.state == "MAIN_MENU":
            menu_rects = draw_main_menu_surface(main_surface, game, mx, my)
            # 在主選單也要繪製機制圖 (如果打開的話)
            if game.show_mechanics_guide:
                guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)

        elif game.state == "SETTINGS":
            setting_rects = draw_settings_surface(main_surface, game, mx, my, mouse_pressed)
            sound_mgr.set_volume(game.volume)

        elif game.state == "MODE_SELECT":
            mode_rects = draw_mode_select_surface(main_surface, mx, my)

        elif game.state in ("BATTLE", "ENEMY_TURN"):
            if game.show_deck:
                back_rect, sort_rects = draw_deck_view_surface(main_surface, game, mx, my)
            elif game.show_mechanics_guide:
                guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
            else:
                hovered, btn_rect, deck_btn_rect, guide_btn_rect = draw_ui_surface(main_surface, game, mx, my)

        elif game.state == "REWARD":
            hovered_reward, confirm_rect, guide_btn_rect, deck_btn_rect = draw_reward_screen_surface(main_surface, game, mx, my)

        elif game.state == "UPGRADE_CARD":
            close_rect, clicked_card, guide_btn_rect, deck_btn_rect = draw_upgrade_view_surface(main_surface, game, mx, my)

        elif game.state == "SELECT_CARD":
            hovered, _, _, _ = draw_ui_surface(main_surface, game, mx, my)
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100)) 
            main_surface.blit(overlay, (0, 0))
            
            prompt_text = "請點擊選擇一張手牌發動效果"
            if game.selection_mode == "TIME_STASIS":
                prompt_text = "【時空停滯】請選擇一張手牌變為 0 費"
            
            prompt_ts = font_big.render(prompt_text, True, GOLD)
            main_surface.blit(prompt_ts, prompt_ts.get_rect(center=(w // 2, h // 2)))
            
            cancel_ts = font_main.render("點擊右鍵取消選擇", True, WHITE)
            main_surface.blit(cancel_ts, cancel_ts.get_rect(center=(w // 2, h // 2 + 60)))

        elif game.state == "DISCOVERY":
            # 繪製靈光一閃界面
            hovered_discovery = draw_discovery_screen_surface(main_surface, game, mx, my)

        elif game.state == "JUMP":
            game.jump_progress += dt * 0.4
            
            player_x = w // 2
            player_y = h * 0.65
            
            scale = max(0, 1.0 - game.jump_progress)
            player_size = int(80 * scale)
            
            if kirby_image and player_size > 0:
                scaled_kirby = pygame.transform.scale(kirby_image, (player_size, player_size))
                kirby_x = player_x - player_size // 2
                kirby_y = player_y - player_size // 2
                main_surface.blit(scaled_kirby, (kirby_x, kirby_y))
            elif player_size > 0:
                pygame.draw.circle(main_surface, (255, 150, 180), (player_x, player_y), int(25 * scale))
            
            for i in range(40):
                angle = (i / 40) * 360
                distance = 50 + game.jump_progress * 200 + random.randint(-20, 20)
                px = player_x + math.cos(math.radians(angle)) * distance
                py = player_y + math.sin(math.radians(angle)) * distance
                alpha = max(0, 200 - int(game.jump_progress * 250))
                size = max(2, 6 - int(game.jump_progress * 8))
                pygame.draw.circle(main_surface, (255, 180, 200, alpha), (int(px), int(py)), size)
            
            fade_alpha = int(255 * min(1, game.jump_progress * 1.5))
            if fade_alpha > 0:
                overlay = pygame.Surface((w, h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, fade_alpha))
                main_surface.blit(overlay, (0, 0))
            
            if game.jump_progress >= 1.0:
                game.state = "VICTORY"

        elif game.state in ["VICTORY", "GAMEOVER"]:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            main_surface.blit(overlay, (0, 0))
            msg = "恭喜通關！(30層達成)" if game.state == "VICTORY" else "YOU DIED"
            msg_ts = font_big.render(msg, True, GOLD if game.state == "VICTORY" else RED)
            main_surface.blit(msg_ts, msg_ts.get_rect(center=(w // 2, h // 2 - 30)))
            hint_ts = font_main.render("點擊滑鼠左鍵返回主選單", True, WHITE)
            main_surface.blit(hint_ts, hint_ts.get_rect(center=(w // 2, h // 2 + 50)))

        anim_mgr.draw(main_surface)

        if game.show_mechanics_guide:
            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)

        if use_shake:
            screen.fill((30, 30, 40))
            screen.blit(game_surface, (int(shake_x), int(shake_y)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game.show_mechanics_guide:
                        game.show_mechanics_guide = False
                        game.mechanics_scroll = 0
                    elif game.state == "MODE_SELECT":
                        game.state = "MAIN_MENU"
                    elif game.state == "BATTLE":
                        game.state = "SETTINGS"
                        game.previous_battle_state = "BATTLE"
                elif event.key == pygame.K_d and game.state == "BATTLE" and not game.show_mechanics_guide:
                    game.show_deck = not game.show_deck

            if event.type == pygame.MOUSEWHEEL:
                if game.show_mechanics_guide:
                    game.mechanics_scroll -= event.y * 28
                elif game.show_deck:
                    game.deck_scroll -= event.y * 40
                elif game.state == "UPGRADE_CARD":
                    game.upgrade_scroll -= event.y * 40

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    game.is_dragging_deck_scroll = False
                    game.is_dragging_upgrade_scroll = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if game.state == "MAIN_MENU":
                        if game.show_mechanics_guide:
                            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
                            if guide_close_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = False
                                game.mechanics_scroll = 0
                        elif menu_rects.get("START") and menu_rects["START"].collidepoint((mx, my)):
                            game.state = "MODE_SELECT"
                        elif menu_rects.get("SETTINGS") and menu_rects["SETTINGS"].collidepoint((mx, my)):
                            game.state = "SETTINGS"
                        elif menu_rects.get("QUIT") and menu_rects["QUIT"].collidepoint((mx, my)):
                            pygame.quit()
                            sys.exit()
                        elif menu_rects.get("GUIDE") and menu_rects["GUIDE"].collidepoint((mx, my)):
                            game.show_mechanics_guide = True
                            game.mechanics_scroll = 0

                    elif game.state == "SETTINGS":
                        if setting_rects.get("BACK") and setting_rects["BACK"][0].collidepoint((mx, my)):
                            if game.previous_battle_state == "BATTLE":
                                game.state = "BATTLE"
                                game.previous_battle_state = None
                            else:
                                game.state = "MAIN_MENU"
                        elif setting_rects.get("QUIT_BATTLE") and setting_rects["QUIT_BATTLE"][0].collidepoint((mx, my)):
                            # 退出對局：重置遊戲狀態並返回主選單
                            game.state = "MAIN_MENU"
                            game.previous_battle_state = None
                            game.__init__()
                        else:
                            for res_id, (rect, val1, val2) in setting_rects.items():
                                if res_id == "BACK": continue
                                if rect.collidepoint((mx, my)):
                                    if res_id == "FS_ON":
                                        game.fullscreen = True
                                        screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
                                    elif res_id == "FS_OFF":
                                        game.fullscreen = False
                                        screen = pygame.display.set_mode((w, h))
                                    elif res_id == "FLASH_ON":
                                        game.flash_enabled = True
                                    elif res_id == "FLASH_OFF":
                                        game.flash_enabled = False
                                    elif res_id.startswith("CHAR_"):
                                        game.current_character = val1
                                    elif res_id.startswith("RES_"):
                                        flags = pygame.FULLSCREEN if game.fullscreen else 0
                                        screen = pygame.display.set_mode((val1, val2), flags)
                                    break

                    elif game.state == "MODE_SELECT":
                        for mode_id, rect in mode_rects.items():
                            if rect.collidepoint((mx, my)):
                                game.apply_mode_modifiers(mode_id)
                                break

                    elif game.state in ("BATTLE", "ENEMY_TURN"):
                        if game.show_deck:
                            back_rect, sort_rects = draw_deck_view_surface(main_surface, game, mx, my)
                            if back_rect.collidepoint((mx, my)):
                                game.show_deck = False
                            else:
                                for sort_id, rect in sort_rects.items():
                                    if rect.collidepoint((mx, my)):
                                        game.deck_sort_mode = sort_id
                                        game.deck_scroll = 0 # 切換排序時重置滾動
                                        break
                            # 檢查是否點擊滾動條區域 (右側 30 像素寬)
                            if mx > w - 40 * ui_scale:
                                game.is_dragging_deck_scroll = True
                        elif game.show_mechanics_guide:
                            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
                            if guide_close_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = False
                                game.mechanics_scroll = 0
                        else:
                            # 確保獲取最新的按鈕區域
                            _, temp_btn_rect, temp_deck_btn_rect, temp_guide_btn_rect = draw_ui_surface(main_surface, game, mx, my)
                            
                            if temp_deck_btn_rect.collidepoint((mx, my)):
                                game.show_deck = True
                                game.deck_scroll = 0
                            elif temp_guide_btn_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = True
                                game.mechanics_scroll = 0
                            elif game.state == "BATTLE":
                                # 僅在玩家回合允許出牌和結束回合
                                if hovered:
                                    game.play_card(hovered, hovered.rect.x, hovered.rect.y)
                                elif temp_btn_rect.collidepoint((mx, my)):
                                    game.end_turn()

                    elif game.state == "REWARD":
                        hovered_reward, confirm_rect, guide_btn_rect, deck_btn_rect = draw_reward_screen_surface(main_surface, game, mx, my)
                        if game.show_mechanics_guide:
                            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
                            if guide_close_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = False
                                game.mechanics_scroll = 0
                        elif guide_btn_rect.collidepoint((mx, my)):
                            game.show_mechanics_guide = True
                            game.mechanics_scroll = 0
                        elif deck_btn_rect.collidepoint((mx, my)):
                            game.show_deck = True
                            game.deck_scroll = 0
                        elif hovered_reward:
                            game.selected_reward = hovered_reward
                        elif confirm_rect.collidepoint((mx, my)):
                            game.choose_reward()

                    elif game.state == "UPGRADE_CARD":
                        close_rect, clicked_card, guide_btn_rect, deck_btn_rect = draw_upgrade_view_surface(main_surface, game, mx, my)
                        
                        if game.show_mechanics_guide:
                            guide_close_rect = draw_mechanics_guide_overlay(main_surface, game, mx, my)
                            if guide_close_rect.collidepoint((mx, my)):
                                game.show_mechanics_guide = False
                                game.mechanics_scroll = 0
                        elif guide_btn_rect.collidepoint((mx, my)):
                            game.show_mechanics_guide = True
                            game.mechanics_scroll = 0
                        elif deck_btn_rect.collidepoint((mx, my)):
                            game.show_deck = True
                            game.deck_scroll = 0
                        # 檢查是否點擊滾動條區域
                        elif mx > w - 40 * ui_scale:
                            game.is_dragging_upgrade_scroll = True
                        
                        if clicked_card and not clicked_card.upgraded:
                            clicked_card.upgrade()
                            game._sync_power_entry_for_card(clicked_card)
                            game.pending_upgrade = False
                            game.current_wave += 1
                            if game.current_wave > game.max_waves:
                                game.state = "VICTORY"
                            else:
                                game.start_next_wave()
                        elif close_rect.collidepoint((mx, my)):
                            game.pending_upgrade = False
                            game.current_wave += 1
                            if game.current_wave > game.max_waves:
                                game.state = "VICTORY"
                            else:
                                game.start_next_wave()

                    elif game.state == "DISCOVERY":
                        if hovered_discovery:
                            # 靈光一閃獲得的卡牌不受普通手牌上限 5 的限制（只要不超過總上限 10）
                            if len(game.hand) < game.max_hand:
                                game.hand.append(hovered_discovery)
                                game.anim_queue.append(("status_enemy", f"獲得 {hovered_discovery.name}", 640, 360))
                            else:
                                game.discard.append(hovered_discovery)
                                game.anim_queue.append(("status_enemy", "手牌已滿，加入棄牌堆", 640, 360))
                            
                            game.discovery_selected.append(hovered_discovery)
                            game.discovery_cards.remove(hovered_discovery)
                            
                            # 检查是否已经选够数量
                            if len(game.discovery_selected) >= game.discovery_select_count:
                                # 其他卡牌放回牌組並洗牌
                                game.deck.extend(game.discovery_cards)
                                game.discovery_cards.clear()
                                game.discovery_selected.clear()
                                random.shuffle(game.deck)
                                game.state = "BATTLE"
                                game.refresh_target_mark()

                    elif game.state == "SELECT_CARD":
                        if hovered and hovered != game.selection_source_card:
                            if game.selection_mode == "TIME_STASIS":
                                hovered.cost = 0
                                game.modified_cards.append(hovered) 
                                game.anim_queue.append(("status_enemy", f"{hovered.name} 變為 0 費", 250, SCREEN_H - 350))
                                game.finish_card_play(game.selection_source_card, SCREEN_W // 2, SCREEN_H // 2)
                            
                            elif game.selection_mode == "FATE_GAMBLE":
                                # 命运豪赌升级版本：自选4张手牌丢弃
                                game.selected_cards.append(hovered)
                                game.hand.remove(hovered)
                                # === 修改这里：临时牌不进入弃牌堆 ===
                                if not getattr(hovered, 'is_temporary', False):
                                    game.discard.append(hovered)
                                game.anim_queue.append(("status_enemy", f"已選擇 {len(game.selected_cards)}/4 張", 250, SCREEN_H - 350))
                                
                                if len(game.selected_cards) >= 4 or len(game.hand) == 0:
                                    # 选够4张或手牌已空，抽4张牌
                                    game.draw_cards(4)
                                    game.selected_cards.clear()
                                    game.selection_mode = None
                                    game.state = "BATTLE"
                            
                            if game.selection_mode != "FATE_GAMBLE":
                                game.selection_mode = None
                                game.selection_source_card = None
                                game.state = "BATTLE"

                    elif game.state in ["VICTORY", "GAMEOVER"]:
                        game.reset_game()
                        sound_mgr.set_volume(game.volume)

                elif event.button == 3: 
                    if game.state == "SELECT_CARD":
                        # === 修改這裡：防止命運豪賭被右鍵取消導致崩潰 ===
                        if game.selection_mode == "FATE_GAMBLE":
                            game.anim_queue.append(("status_enemy", "無法取消！", 250, SCREEN_H - 350))
                            continue
                        # ==========================================
                        game.energy += game.selection_source_card.cost
                        game.selection_mode = None
                        game.selection_source_card = None
                        game.state = "BATTLE"
                        game.anim_queue.append(("status_enemy", "已取消選擇", 250, SCREEN_H - 350))

if __name__ == "__main__":
    main()