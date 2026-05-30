"""Shared test fixtures and utilities."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# =============================================================================
# Mock pygame globally before importing the game module
# =============================================================================
_SCREEN_W, _SCREEN_H = 1280, 720

_mock_pygame = MagicMock()
_mock_pygame.KEYDOWN = 2
_mock_pygame.K_ESCAPE = 27
_mock_pygame.K_SPACE = 32
_mock_pygame.K_LEFT = 276
_mock_pygame.K_RIGHT = 275
_mock_pygame.K_UP = 273
_mock_pygame.K_DOWN = 274
_mock_pygame.K_d = 100
_mock_pygame.K_RETURN = 13
_mock_pygame.MOUSEMOTION = 4
_mock_pygame.MOUSEBUTTONDOWN = 5
_mock_pygame.MOUSEBUTTONUP = 6
_mock_pygame.MOUSEWHEEL = 7
_mock_pygame.QUIT = 12
_mock_pygame.USEREVENT = 24
_mock_pygame.FULLSCREEN = -2147483648
_mock_pygame.DOUBLEBUF = 1073741824
_mock_pygame.K_PERIOD = 46
_mock_pygame.K_F11 = 292
_mock_pygame.KEYUP = 3
_mock_pygame.KMOD_ALT = 768
_mock_pygame.KMOD_SHIFT = 3
_mock_pygame.init = MagicMock(return_value=(0, 0))
_mock_pygame.mixer = MagicMock()
_mock_pygame.mixer.Sound = MagicMock(return_value=MagicMock())
_mock_pygame.mixer.music = MagicMock()
_mock_pygame.mixer.init = MagicMock()
_mock_pygame.time = MagicMock()
_mock_pygame.time.Clock = MagicMock(return_value=MagicMock(tick=MagicMock(return_value=16)))
_mock_pygame.time.get_ticks = MagicMock(return_value=0)
_mock_pygame.font = MagicMock()
_mock_pygame.font.SysFont = MagicMock(return_value=MagicMock(
    render=MagicMock(return_value=MagicMock(
        get_rect=MagicMock(return_value=MagicMock(
            x=0, y=0, center=(0, 0), right=0, bottom=0, left=0, top=0, width=10, height=10, w=10, h=10
        ))
    )),
    size=MagicMock(return_value=(10, 10)),
    get_height=MagicMock(return_value=10),
))
_mock_pygame.font.Font = MagicMock(return_value=_mock_pygame.font.SysFont.return_value)
_mock_pygame.display = MagicMock()
_mock_pygame.display.set_mode = MagicMock(return_value=MagicMock(
    get_rect=MagicMock(return_value=MagicMock(center=(640, 360), x=0, y=0, width=_SCREEN_W, height=_SCREEN_H)),
    blit=MagicMock(),
    fill=MagicMock(),
    subsurface=MagicMock(return_value=MagicMock(
        get_rect=MagicMock(return_value=MagicMock(x=0, y=0, width=_SCREEN_W, height=_SCREEN_H)),
        blit=MagicMock(),
        fill=MagicMock(),
    )),
))
_mock_pygame.display.flip = MagicMock()
_mock_pygame.display.get_surface = MagicMock(return_value=_mock_pygame.display.set_mode.return_value)
_mock_pygame.Surface = MagicMock(return_value=MagicMock(
    get_rect=MagicMock(return_value=MagicMock(x=0, y=0, width=_SCREEN_W, height=_SCREEN_H, center=(640, 360))),
    blit=MagicMock(),
    fill=MagicMock(),
    subsurface=MagicMock(return_value=MagicMock(
        get_rect=MagicMock(return_value=MagicMock(x=0, y=0, width=_SCREEN_W, height=_SCREEN_H)),
        blit=MagicMock(),
        fill=MagicMock(),
    )),
    set_colorkey=MagicMock(),
    get_width=MagicMock(return_value=_SCREEN_W),
    get_height=MagicMock(return_value=_SCREEN_H),
    copy=MagicMock(return_value=MagicMock(
        get_rect=MagicMock(return_value=MagicMock(x=0, y=0, width=_SCREEN_W, height=_SCREEN_H)),
        blit=MagicMock(),
        fill=MagicMock(),
        set_colorkey=MagicMock(),
    )),
))
_mock_pygame.Rect = MagicMock(return_value=MagicMock(
    x=0, y=0, width=100, height=100,
    center=(0, 0), collidepoint=MagicMock(return_value=False),
    left=0, right=100, top=0, bottom=100,
))
_mock_pygame.transform = MagicMock()
_mock_pygame.transform.scale = MagicMock(return_value=_mock_pygame.Surface())
_mock_pygame.transform.smoothscale = MagicMock(return_value=_mock_pygame.Surface())
_mock_pygame.image = MagicMock()
_mock_pygame.image.load = MagicMock(return_value=MagicMock(
    convert_alpha=MagicMock(return_value=MagicMock(
        get_rect=MagicMock(return_value=MagicMock(x=0, y=0, width=100, height=100)),
        set_colorkey=MagicMock(),
        copy=MagicMock(return_value=MagicMock()),
    )),
))
_mock_pygame.draw = MagicMock()
_mock_pygame.draw.rect = MagicMock()
_mock_pygame.draw.circle = MagicMock()
_mock_pygame.draw.polygon = MagicMock()
_mock_pygame.draw.line = MagicMock()
_mock_pygame.event = MagicMock()
_mock_pygame.event.get = MagicMock(return_value=[])
_mock_pygame.event.poll = MagicMock(return_value=MagicMock(type=0))
_mock_pygame.event.post = MagicMock()
_mock_pygame.key = MagicMock()
_mock_pygame.key.get_pressed = MagicMock(return_value=[False] * 512)
_mock_pygame.key.get_mods = MagicMock(return_value=0)
_mock_pygame.mouse = MagicMock()
_mock_pygame.mouse.get_pos = MagicMock(return_value=(0, 0))
_mock_pygame.mouse.get_pressed = MagicMock(return_value=(False, False, False))
_mock_pygame.mouse.set_visible = MagicMock()

sys.modules['pygame'] = _mock_pygame


# =============================================================================
# Import the game package
# =============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = str(PROJECT_ROOT / "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# Import the main package module (triggers all sub-imports)
import genshin_spire  # noqa: E402

game_module = genshin_spire


@pytest.fixture(scope="session")
def gm():
    """Provide the imported game module to all tests."""
    return game_module
