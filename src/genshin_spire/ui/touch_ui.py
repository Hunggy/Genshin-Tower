import pygame

import genshin_spire.config as _cfg
from ..resources import get_ui_font


class TouchOverlay:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.state = ""
        self.buttons = {}
        self.update_layout(w, h)

    def update_layout(self, w, h):
        self.w = w
        self.h = h
        self.buttons = {}
        if not _cfg.IS_TOUCH:
            return
        bw = int(60 * h / 720)
        bh = int(36 * h / 720)
        margin = 8
        font_size = max(12, int(14 * h / 720))
        self._font = get_ui_font(font_size)

        rx = w - bw - margin
        by = h - bh - margin

        self.buttons["END_TURN"] = pygame.Rect(rx - bw - margin, by, bw, bh)
        self.buttons["TARGET_L"] = pygame.Rect(margin, by - bh - margin, bw, bh)
        self.buttons["TARGET_R"] = pygame.Rect(margin + bw + margin, by - bh - margin, bw, bh)
        self.buttons["DECK"] = pygame.Rect(margin, margin, bw, bh)
        self.buttons["GUIDE"] = pygame.Rect(margin + bw + margin, margin, bw, bh)
        self.buttons["LOG"] = pygame.Rect(margin + 2 * (bw + margin), margin, bw, bh)
        self.buttons["SCROLL_UP"] = pygame.Rect(w - bw - margin, h // 2 - bh * 2, bw, bh)
        self.buttons["SCROLL_DOWN"] = pygame.Rect(w - bw - margin, h // 2 + bh, bw, bh)
        self.buttons["BACK"] = pygame.Rect(margin, by - 2 * (bh + margin), bw, bh)
        self.buttons["CANCEL"] = pygame.Rect(margin + bw + margin, by - 2 * (bh + margin), bw, bh)
        self.buttons["ESC"] = pygame.Rect(margin, margin + bh + margin, bw, bh)

    def set_state(self, state):
        self.state = state

    def get_action(self, pos):
        if not _cfg.IS_TOUCH:
            return None
        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return name
        return None

    def draw(self, surface):
        if not _cfg.IS_TOUCH:
            return
        for name, rect in self.buttons.items():
            visible = self._is_visible(name)
            if not visible:
                continue
            s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            s.fill((50, 50, 50, 140))
            surface.blit(s, rect.topleft)
            pygame.draw.rect(surface, (180, 180, 180), rect, 1)
            label_text = {"ESC": "設定"}.get(name, name.replace("_", " "))
            label = self._font.render(label_text, True, (220, 220, 220))
            lx = rect.x + (rect.w - label.get_width()) // 2
            ly = rect.y + (rect.h - label.get_height()) // 2
            surface.blit(label, (lx, ly))

    def _is_visible(self, name):
        s = self.state
        if name in ("DECK", "GUIDE", "LOG"):
            return s in ("BATTLE", "ENEMY_TURN", "SELECT_CARD", "UPGRADE_CARD", "SHOP")
        if name in ("TARGET_L", "TARGET_R"):
            return s == "BATTLE"
        if name == "END_TURN":
            return s == "BATTLE"
        if name == "SCROLL_UP":
            return True
        if name == "SCROLL_DOWN":
            return True
        if name == "BACK":
            return s in ("MODE_SELECT", "SETTINGS")
        if name == "CANCEL":
            return s == "SELECT_CARD"
        if name == "ESC":
            return s in ("BATTLE", "ENEMY_TURN", "REWARD", "SHOP", "UPGRADE_CARD")
        return True
