import os
import sys


# Determine project root dynamically
def _get_project_root():
    # 本檔案位於 src/genshin_spire/
    this_dir = os.path.dirname(os.path.abspath(__file__))
    # 往上兩層到專案根目錄
    return os.path.dirname(os.path.dirname(this_dir))


PROJECT_ROOT = _get_project_root()


def get_base_path():
    # 支援 PyInstaller 打包路徑
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return PROJECT_ROOT


def get_save_path():
    """取得存檔檔案完整路徑：開發時在專案根目錄，打包後在用戶文件目錄"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包後：使用用戶文件目錄，避免臨時目錄被清理導致存檔丟失
        save_dir = os.path.join(os.path.expanduser("~"), "Documents", "GenshinSpire")
    else:
        # 開發環境：專案根目錄
        save_dir = PROJECT_ROOT

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    return os.path.join(save_dir, "savegame.json")


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
