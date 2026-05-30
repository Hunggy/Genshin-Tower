"""Entry point for Genshin Spire.

必须先创建 pygame 窗口（display surface），包内各模块才能在 import
时安心调用 .convert() / .convert_alpha() 加载图片。
"""

import os
import sys

# 1. 初始化 pygame（不含任何包导入）
import pygame
pygame.init()
pygame.mixer.init()

# 2. 立刻创建窗口 —— 必须在任何 .convert() 调用之前
SCREEN_W, SCREEN_H = 1280, 720
# 用 NOFRAME 防止导入时出现短暂闪屏；main() 里会重新设置标题
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.DOUBLEBUF)

# 3. 把 src 加入路径并导入游戏主循环
SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from genshin_spire.main import main  # noqa: E402

if __name__ == "__main__":
    main()
