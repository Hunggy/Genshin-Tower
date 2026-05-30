import pygame

from ..config import GOLD, WHITE
from ..resources import font_big, font_hp, font_desc
from ..save import MECHANICS_GUIDE_ENTRIES
from .common import wrap_text_lines


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
        y += line_h + 20
        for line in wrap_text_lines(body, font_desc, text_width):
            line_ts = font_desc.render(line, True, (210, 210, 220))
            surface.blit(line_ts, (content_rect.x + 8, y))
            y += line_h
        y += 40

    surface.set_clip(None)
    content_height = y + game.mechanics_scroll - content_rect.y
    max_scroll = max(0, content_height - content_rect.height)
    game.mechanics_scroll = max(0, min(game.mechanics_scroll, max_scroll))

    return close_rect
