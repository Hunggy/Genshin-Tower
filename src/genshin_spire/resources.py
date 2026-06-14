import os
import pygame

from .config import get_base_path, UI_FONT_FAMILIES, SCREEN_W, SCREEN_H, IS_WEB
from .particle import Particle


def _try_load(path):
    """嘗試載入圖片，失敗回傳 None"""
    try:
        return pygame.image.load(path)
    except Exception:
        return None


def load_background(name):
    base = get_base_path()
    for ext in [".png", ".jpg", ".jpeg"]:
        img = _try_load(os.path.join(base, "images", name + ext))
        if img:
            return pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
    return None


particles = [Particle() for _ in range(50)]

background_menu = load_background("background_menu")
background_battle = load_background("background_battle")
background_victory = load_background("background_victory")


def load_kirby():
    base = get_base_path()
    for ext in [".png", ".jpg", ".jpeg"]:
        img = _try_load(os.path.join(base, "images", "kirby" + ext))
        if img:
            return pygame.transform.scale(img.convert_alpha(), (60, 60))
    return None


kirby_image = load_kirby()


def load_energy_image():
    base = get_base_path()
    energy_dirs = [
        os.path.join(base, "images", "Energy"),
        os.path.join(base, "images", "Energry"),
        os.path.join(os.path.dirname(base), "images", "Energy"),
        os.path.join(os.path.dirname(base), "images", "Energry"),
    ]
    for d in energy_dirs:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(d, f)
                if path.lower().endswith(".png"):
                    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (80, 80))
                img = pygame.image.load(path).convert()
                colorkey = img.get_at((0, 0))
                img.set_colorkey(colorkey)
                return pygame.transform.scale(img.convert_alpha(), (80, 80))
    return None


energy_image = load_energy_image()


def load_shield_image():
    base = get_base_path()
    for ext in [".png", ".jpg", ".jpeg"]:
        img = _try_load(os.path.join(base, "images", "shield" + ext))
        if img:
            return img.convert_alpha()
    return None


shield_image = load_shield_image()


_ENEMY_NAME_MAP = {
    "基礎雜兵": "enemy_basic",
    "進階雜兵(盾/遠程)": "enemy_advanced",
    "進階怪(屬性控制)": "enemy_advanced",
    "怪物組合(群攻考驗)": "enemy_group",
    "高難度雜兵": "enemy_hard",
    "終極考驗怪物": "enemy_ultimate",
    "最終大_BOSS_3": "enemy_boss_final",
    "階段 BOSS 1": "enemy_stage_boss_1",
    "階段 BOSS 2": "enemy_stage_boss_2",
    "精英怪 1": "enemy_elite_1",
    "精英怪 2": "enemy_elite_2",
    "精英怪 3": "enemy_elite_3",
    "精英怪": "enemy_elite_basic",
}


def load_enemy_image(enemy_name):
    base = get_base_path()
    enemy_dir = os.path.join(base, "images", "enemies")

    ascii_name = _ENEMY_NAME_MAP.get(enemy_name)
    search_names = []
    if ascii_name:
        search_names.append(ascii_name)
    search_names.extend([enemy_name, enemy_name.replace(" ", "_"), enemy_name.replace(" ", "")])
    if "(" in enemy_name:
        name_no_paren = enemy_name[:enemy_name.index("(")].strip()
        search_names.append(name_no_paren)
        search_names.append(name_no_paren.replace(" ", "_"))

    for ext in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]:
        for name in search_names:
            for d in [enemy_dir, os.path.join(base, "images")]:
                path = os.path.join(d, name + ext)
                if os.path.exists(path):
                    try:
                        return scale_enemy(pygame.image.load(path).convert_alpha())
                    except:
                        pass

    if os.path.exists(enemy_dir):
        try:
            files = os.listdir(enemy_dir)
            search_key = "".join(filter(str.isalnum, enemy_name)).lower()
            for f in files:
                file_key = "".join(filter(str.isalnum, os.path.splitext(f)[0])).lower()
                if search_key in file_key or file_key in search_key:
                    try:
                        return scale_enemy(pygame.image.load(os.path.join(enemy_dir, f)).convert_alpha())
                    except:
                        continue
        except:
            pass
    return None


def scale_enemy(img):
    w, h = img.get_size()
    ratio = min(120 / w, 120 / h)
    return pygame.transform.smoothscale(img, (int(w * ratio), int(h * ratio)))


def load_all_characters():
    chars = {}
    base = get_base_path()

    search_dirs = [
        os.path.join(base, "images"),
        os.path.join(os.path.dirname(base), "images"),
        os.path.join(base, "model"),
        os.path.join(base, "Genshin Tower", "model"),
    ]

    for d in search_dirs:
        if not os.path.exists(d):
            continue
        for item in os.listdir(d):
            if item.lower() in ["energy", "engry", "energry", "enemies"]:
                continue
            full_path = os.path.join(d, item)
            if os.path.isdir(full_path):
                frames = []
                img_files = sorted([f for f in os.listdir(full_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
                for f in img_files:
                    try:
                        img = pygame.image.load(os.path.join(full_path, f)).convert_alpha()
                        frames.append(pygame.transform.scale(img, (120, 120)))
                    except:
                        continue
                if frames:
                    chars[item] = frames
            elif item.lower().endswith((".png", ".jpg", ".jpeg")):
                name = os.path.splitext(item)[0]
                if "background" in name.lower():
                    continue
                try:
                    img = pygame.image.load(full_path).convert_alpha()
                    chars[name] = [pygame.transform.scale(img, (120, 120))]
                except:
                    continue

    if not chars:
        surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 150, 180), (60, 60), 55)
        chars["Default"] = [surf]
    return chars


character_images = load_all_characters()


def load_element_icons():
    icons = {}
    base = get_base_path()
    elements_dir = os.path.join(base, "images", "elements")
    if os.path.exists(elements_dir):
        for f in os.listdir(elements_dir):
            if f.lower().endswith((".png", ".jpg", ".jpeg")):
                name = os.path.splitext(f)[0].capitalize()
                try:
                    img = pygame.image.load(os.path.join(elements_dir, f)).convert_alpha()
                    icons[name] = pygame.transform.smoothscale(img, (26, 26))
                except:
                    continue
    return icons


element_icons = load_element_icons()

_ui_font_cache = {}

_web_font_obj = None


def _get_web_font():
    global _web_font_obj
    if _web_font_obj is not None:
        return _web_font_obj
    base = get_base_path()
    for candidate in [
        os.path.join(base, "fonts", "NotoSansSC-Regular.otf"),
        os.path.join(base, "images", "NotoSansSC-Regular.otf"),
        os.path.join(base, "NotoSansSC-Regular.otf"),
    ]:
        try:
            f = pygame.font.Font(candidate, 16)
            _web_font_obj = f
            return _web_font_obj
        except Exception:
            continue
    _web_font_obj = False
    return _web_font_obj


def get_ui_font(size, bold=False):
    key = (size, bold)
    if key not in _ui_font_cache:
        if IS_WEB:
            fp = _get_web_font()
            if fp:
                try:
                    _ui_font_cache[key] = pygame.font.Font(fp.path, size)
                except Exception:
                    _ui_font_cache[key] = pygame.font.SysFont(UI_FONT_FAMILIES, size, bold=bold)
            else:
                _ui_font_cache[key] = pygame.font.SysFont(UI_FONT_FAMILIES, size, bold=bold)
        else:
            _ui_font_cache[key] = pygame.font.SysFont(UI_FONT_FAMILIES, size, bold=bold)
    return _ui_font_cache[key]


font_main = get_ui_font(20)
font_desc = get_ui_font(14)
font_hp = get_ui_font(22, bold=True)
font_big = get_ui_font(60)
