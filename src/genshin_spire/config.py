import os
import sys

# --- 平台檢測 ---
IS_WEB = hasattr(sys, 'platform') and sys.platform == 'emscripten'
IS_TOUCH = False  # 遊戲啟動後動態設定


# Determine project root dynamically
def _get_project_root():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(this_dir))


PROJECT_ROOT = _get_project_root()


def get_base_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return PROJECT_ROOT


def get_save_path(slot=1):
    if IS_WEB:
        return os.path.join(get_base_path(), f"savegame_{slot}.json")
    if getattr(sys, 'frozen', False):
        save_dir = os.path.join(os.path.expanduser("~"), "Documents", "GenshinSpire")
    else:
        save_dir = PROJECT_ROOT
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    return os.path.join(save_dir, f"savegame_{slot}.json")


def get_meta_save_path():
    if IS_WEB:
        return os.path.join(get_base_path(), "meta_save.json")
    if getattr(sys, 'frozen', False):
        save_dir = os.path.join(os.path.expanduser("~"), "Documents", "GenshinSpire")
    else:
        save_dir = PROJECT_ROOT
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    return os.path.join(save_dir, "meta_save.json")


SCREEN_W, SCREEN_H = 1280, 720

# 字體加載（統一使用支援中文的系統字體，避免彈出文字顯示為空白）
UI_FONT_FAMILIES = [
    "Microsoft YaHei", "Microsoft YaHei UI", "SimHei", "SimSun",
    "PingFang SC", "Noto Sans CJK SC", "Arial Unicode MS", "Arial",
]

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

# 存檔系統常量
SAVE_VERSION = 1
