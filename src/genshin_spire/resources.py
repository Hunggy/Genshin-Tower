import os
import pygame

from .config import get_base_path, UI_FONT_FAMILIES, SCREEN_W, SCREEN_H
from .particle import Particle


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
        os.path.join(os.path.dirname(base), "images", "Energry"),
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
                    colorkey = img.get_at((0, 0))
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
                    except:
                        pass

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
                    except:
                        continue
    except:
        pass

    return None


def scale_enemy(img):
    w, h = img.get_size()
    ratio = min(120 / w, 120 / h)
    new_w, new_h = int(w * ratio), int(h * ratio)
    return pygame.transform.smoothscale(img, (new_w, new_h))


# 加載主角圖片
def load_all_characters():
    chars = {}  # 格式: {"Name": [frame1, frame2, ...]}
    base = get_base_path()

    # 同時搜尋多個可能的目錄，防止路徑嵌套導致找不到圖片
    search_dirs = [
        os.path.join(base, "images"),
        os.path.join(os.path.dirname(base), "images"),
        os.path.join(base, "model"),
        os.path.join(base, "Genshin Tower", "model"),
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
                    except:
                        continue

                if frames:
                    chars[item] = frames
                    print(f"  [動畫] 載入序列: {item} (共 {len(frames)} 幀)")

            # 情況 B: 單張圖片
            elif item.lower().endswith((".png", ".jpg", ".jpeg")):
                name = os.path.splitext(item)[0]
                # 跳過背景圖
                if "background" in name.lower():
                    continue
                try:
                    img = pygame.image.load(full_path).convert_alpha()
                    chars[name] = [pygame.transform.scale(img, (120, 120))]
                    print(f"  [靜態] 載入角色: {name}")
                except:
                    continue

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
                name = os.path.splitext(f)[0].capitalize()  # 確保與 Pyro, Hydro 等對齊
                try:
                    img = pygame.image.load(os.path.join(elements_dir, f)).convert_alpha()
                    icons[name] = pygame.transform.smoothscale(img, (26, 26))
                except:
                    continue
    return icons


element_icons = load_element_icons()

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
