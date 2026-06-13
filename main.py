"""Entry point for Genshin Spire."""

import os
import sys

import pygame

IS_WEB = hasattr(sys, 'platform') and sys.platform == 'emscripten'

pygame.init()
pygame.mixer.init()

SCREEN_W, SCREEN_H = 1280, 720
if IS_WEB:
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
else:
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.DOUBLEBUF)

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from genshin_spire.main import main  # noqa: E402

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
